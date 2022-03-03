import os, datetime, logging, glob
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse,FileResponse
from django.core.files import File
from wsgiref.util import FileWrapper

from .config import *
from .model import *
from .app import nasaaccess
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(filename=nasaaccess_log,level=logging.INFO)

def run_nasaaccess(request):

    """
    Controller to call nasaaccess R functions.
    """
    # Get selected parameters and pass them into nasaccess R scripts
    try:
        d_start = request.POST.getlist('startDate[]')
        d_end = request.POST.getlist('endDate[]')
        functions = request.POST.getlist('functions[]')
        nexgdpp=request.POST.getlist('nexgdpp[]')
        nextgdppcmip=request.POST.getlist('nextgdppcmip[]')

        
        watershed = request.POST.get('watershed')
        dem = request.POST.get('dem')
        email = request.POST.get('email')
        # user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path)
        app_workspace_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'app_workspace')

        os.chmod(app_workspace_path, 0o777)
        result = nasaaccess_run(email, functions, watershed, dem, d_start, d_end, app_workspace_path,nexgdpp,nextgdppcmip)
        return JsonResponse({'Result': str(result)})
    except Exception as e:
        return JsonResponse({'Error': str(e)})

def upload_shapefiles(request):

    """
    Controller to upload new shapefiles to app server and publish to geoserver
    """
    files = request.FILES.getlist('files')
    
    #create new dir or check dir for shapefiles
    app_workspace_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'app_workspace')
    shp_path = os.path.join(app_workspace_path,'shapefiles')


    if not os.path.exists(shp_path):
        os.makedirs(shp_path)
        os.chmod(shp_path, 0o777)

    #Loop to create files in a directory with the name of the first file.
    for n, shp_file in enumerate(files):
        shp_path_directory = os.path.join(shp_path, shp_file.name.split('.')[0])
        shp_path_directory_file = os.path.join(shp_path_directory, shp_file.name)

        if not os.path.exists(shp_path_directory):
            os.makedirs(shp_path_directory)
            os.chmod(shp_path_directory, 0o777)
        if os.path.isfile(shp_path_directory_file):
            logging.info('file already exists')
        else:
            with open(shp_path_directory_file, 'wb') as dst:
                for chunk in files[n].chunks():
                    dst.write(chunk)

    filename = os.path.splitext(os.path.basename(shp_path_directory))[0].split('.')[0]
    upload_shapefile(filename,shp_path_directory)
    return JsonResponse({"file":f'{filename}'})


def upload_tiffiles(request):
    """
    Controller to upload new DEM files
    """
    files = request.FILES.getlist('files')
    print(files)
    #create new dir or check dir for shapefiles
    app_workspace_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'app_workspace')

    dem_path = os.path.join(app_workspace_path,'DEMfiles')
    if not os.path.exists(dem_path):
        os.makedirs(dem_path)
        os.chmod(dem_path, 0o777)

    #Loop to create files in a directory with the name of the first file.
    for n, dem_file in enumerate(files):
        dem_path_directory = os.path.join(dem_path, dem_file.name.split('.')[0])
        dem_path_directory_file = os.path.join(dem_path_directory, dem_file.name)

        if not os.path.exists(dem_path_directory):
            os.makedirs(dem_path_directory)
            os.chmod(dem_path_directory, 0o777)
        if os.path.isfile(dem_path_directory_file):
            logging.info('file already exists')
        else:
            with open(dem_path_directory_file, 'wb') as dst:
                for chunk in files[n].chunks():
                    dst.write(chunk)

    filename = os.path.splitext(os.path.basename(dem_path_directory))[0].split('.')[0]

    # path_to_shp = os.path.join(shp_path, filename)

    upload_dem(filename,dem_path_directory)
    return JsonResponse({"file":f'{filename}'})


def download_data(request):
    """
    Controller to download data using a unique access code emailed to the user when their data is ready
    """
    if request.method == 'POST':
        #get access code from form
        access_code = request.POST['access_code']

        #identify user's file path on the server
        unique_path = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data')

        #compress the entire directory into a .zip file
        def zipfolder(foldername, target_dir):
            zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
            rootlen = len(target_dir) + 1
            for base, dirs, files in os.walk(target_dir):
                for file in files:
                    fn = os.path.join(base, file)
                    zipobj.write(fn, fn[rootlen:])

        zipfolder(unique_path, unique_path)

        #open the zip file
        path_to_file = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data.zip')
        # f = open(path_to_file, 'r')
        # myfile = File(f)

        # download the zip file using the browser's download dialogue box
        # response = HttpResponse(myfile, content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename=nasaaccess_data.zip'
        # return response
        # zip_file = open(path_to_file, 'rb')

        # return FileResponse(zip_file, as_attachment=True)
        if os.path.exists(path_to_file):
            print("jola")
            with open(path_to_file, 'rb') as zip_file:
                    response = HttpResponse(FileWrapper(zip_file), content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="foo.zip"'
                    return response
        try:
            zip_file = open(path_to_file, 'rb')
            response = HttpResponse(zip_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=nasaaccess_data.zip'
            return response
        except Exception as e:
            print(e)
        return HttpResponse()

def getValues(request):
    return_obj = {}
    file = request.POST['name']
    func_name = request.POST['func']
    access_code = request.POST['access_code']

    new_path = ''
    unique_path = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data',access_code)
    if os.path.exists(unique_path) == False:
        unique_path = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data')
    if func_name == 'GLDASpolyCentroid':
        pre_path = os.path.join(unique_path,'GLDASpolyCentroid')
        new_path = os.path.join(unique_path,'GLDASpolyCentroid','temp_Master.txt')
   
    if func_name == 'GLDASwat':
        pre_path = os.path.join(unique_path,'GLDASwat')
        new_path = os.path.join(unique_path,'GLDASwat','temp_Master.txt')

    if func_name == 'GPMpolyCentroid':
        pre_path = os.path.join(unique_path,'GPMpolyCentroid')

        new_path = os.path.join(unique_path,'GPMpolyCentroid','precipitationMaster.txt')

    if func_name == 'GPMswat':
        pre_path = os.path.join(unique_path,'GPMswat')

        new_path = os.path.join(unique_path,'GPMswat','precipitationMaster.txt')

    if func_name == 'NEX_GDPPswat':
        pre_path = os.path.join(unique_path,'NEXGDPP')
        new_path = os.path.join(unique_path,'NEXGDPP','prGrid_Master.txt')

    if func_name == 'NEX_GDPP_CMIP6':
        pre_path = os.path.join(unique_path,'NEX_GDPP_CMIP6')
        
        new_path = os.path.join(unique_path,'NEX_GDPP_CMIP6','prGrid_Master.txt')

    if os.path.exists(new_path):
        path_file = os.path.join(pre_path,f'{file}.txt')
        mypd = pd.read_csv(path_file)
        if func_name == 'NEX_GDPPswat' or func_name == 'NEX_GDPP_CMIP6':
            new_pd = mypd.reset_index(drop=True)
        else:
            new_pd = mypd.reset_index()

        print(func_name)
        print(new_pd)

        if func_name == 'GLDASpolyCentroid' or func_name == 'GLDASwat':
            if new_pd.empty:
                return_obj["max_val"]= []
                return_obj["min_val"]= []
            else:
                new_pd.columns = ["max_val", "min_val"]
                return_obj["max_val"]= new_pd["max_val"].to_list()
                return_obj["min_val"]= new_pd["min_val"].to_list()
        else:
            if new_pd.empty:
                return_obj['val'] = []
            else:
                new_pd.columns = ["val"]
                return_obj['val'] =  new_pd["val"].to_list()

        starting_date = list(mypd)
        date = datetime.strptime(starting_date[0], '%Y%m%d')
        date_arr = []
        for one_day in range(new_pd.shape[0]):
            new_date2 = date + timedelta(days=one_day)
            new_date_string = new_date2.strftime('%m/%d/%Y')
            date_arr.append(new_date_string)
        new_pd['time'] = date_arr
        return_obj['labels'] = new_pd['time'].to_list()

    return JsonResponse(return_obj)

def plot_data(request):
    """
    Controller to download data using a unique access code emailed to the user when their data is ready
    """
    response_obj= {}

    if request.method == 'POST':
        #get access code from form
        access_code = request.POST['access_code']

        #identify user's file path on the server
        unique_path = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data',access_code)
        if os.path.exists(unique_path) == False:
            unique_path = os.path.join(data_path, 'outputs', access_code, 'nasaaccess_data')


        #get the series from folders

        gldaspolycentroid_path = os.path.join(unique_path,'GLDASpolyCentroid','temp_Master.txt')
        gldasswat_path = os.path.join(unique_path,'GLDASwat','temp_Master.txt')
        gpmpolycentroid_path = os.path.join(unique_path,'GPMpolyCentroid','precipitationMaster.txt')
        gpmswat_path = os.path.join(unique_path,'GPMswat','precipitationMaster.txt')
        nextgdpp_path = os.path.join(unique_path,'NEXGDPP','prGrid_Master.txt')
        nexgdppcmip6_path = os.path.join(unique_path,'NEX_GDPP_CMIP6','prGrid_Master.txt')

        print(gldaspolycentroid_path)
        if os.path.exists(gldaspolycentroid_path):
            print('GLDASpolyCentroid')
            data_master_1 = pd.read_csv(gldaspolycentroid_path)
            response_obj['GLDASpolyCentroid'] = data_master_1.to_dict('index')

        if os.path.exists(gldasswat_path):
            print('GLDASwat')
            data_master_1 = pd.read_csv(gldasswat_path)
            response_obj['GLDASwat'] = data_master_1.to_dict('index')

        if os.path.exists(gpmpolycentroid_path):
            print('GPMpolyCentroid')
            data_master_1 = pd.read_csv(gpmpolycentroid_path)
            response_obj['GPMpolyCentroid'] = data_master_1.to_dict('index')
  
        if os.path.exists(gpmswat_path):
            print('GPMswat')
            data_master_1 = pd.read_csv(gpmswat_path)
            response_obj['GPMswat'] = data_master_1.to_dict('index')

        if os.path.exists(nextgdpp_path):
            print('NEXGDPP')
            data_master_1 = pd.read_csv(nextgdpp_path)
            response_obj['NEX_GDPPswat'] = data_master_1.to_dict('index')
        if os.path.exists(nexgdppcmip6_path):
            print('NEX_GDPP_CMIP6')
            data_master_1 = pd.read_csv(nexgdppcmip6_path)
            response_obj['NEX_GDPP_CMIP6'] = data_master_1.to_dict('index')
    return JsonResponse(response_obj)