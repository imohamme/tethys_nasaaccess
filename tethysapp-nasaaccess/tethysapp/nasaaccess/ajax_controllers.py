import os, datetime, logging, glob
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse,FileResponse
from django.core.files import File
from wsgiref.util import FileWrapper

# from .forms import UploadShpForm, UploadDEMForm
from .config import *
# from .modelDjango import *
from .model import *
from .app import nasaaccess

logging.basicConfig(filename=nasaaccess_log,level=logging.INFO)

def run_nasaaccess(request):

    """
    Controller to call nasaaccess R functions.
    """
    # Get selected parameters and pass them into nasaccess R scripts
    try:
        d_start = request.POST.get('startDate')
        d_end = request.POST.get('endDate')
        # start = request.POST.get('startDate')
        # d_start = str(datetime.datetime.strptime(start, '%b %d, %Y').strftime('%Y-%m-%d'))
        # end = request.POST.get(str('endDate'))
        # d_end = str(datetime.datetime.strptime(end, '%b %d, %Y').strftime('%Y-%m-%d'))
        functions = request.POST.getlist('functions[]')
        nexgdpp=request.POST.getlist('nexgdpp[]')
        nextgdppcmip=request.POST.getlist('nextgdppcmip[]')


        
        watershed = request.POST.get('watershed')
        dem = request.POST.get('dem')
        email = request.POST.get('email')
        user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path)
        os.chmod(user_workspace, 0o777)
        result = nasaaccess_run(email, functions, watershed, dem, d_start, d_end, user_workspace,nexgdpp,nextgdppcmip)
        return JsonResponse({'Result': str(result)})
    except Exception as e:
        return JsonResponse({'Error': str(e)})

def upload_shapefiles(request):

    """
    Controller to upload new shapefiles to app server and publish to geoserver
    """
    files = request.FILES.getlist('files')
    
    #create new dir or check dir for shapefiles
    user_workspace_path = nasaaccess.get_user_workspace(request.user).path

    shp_path = os.path.join(user_workspace_path,'shapefiles')
    # shp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'user_workspaces','shapefiles')


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

    # filepath = glob.glob(os.path.join(shp_path_directory, '*.shp'))[0]
    # shp_path_directory_file = os.path.join(shp_path_directory, shp_file.name)

    filename = os.path.splitext(os.path.basename(shp_path_directory))[0].split('.')[0]
    print(shp_path_directory)
    print(filename)
    # path_to_shp = os.path.join(shp_path, filename)
    upload_shapefile(filename,shp_path_directory)
    return JsonResponse({"file":f'{filename}'})

    # if request.method == 'POST':
    #     form = UploadShpForm(request.POST, request.FILES)
    #     id = request.FILES['shapefile'].name.split('.')[0] # Get name of the watershed from the shapefile name
    #     if form.is_valid():
    #         form.save()  # Save the shapefile to the nasaaccess data file path
    #         perm_file_path = os.path.join(data_path, 'shapefiles', id)
    #         user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path, 'shapefiles')
    #         shp_path_user = os.path.join(user_workspace, id)
    #         if os.path.isfile(perm_file_path) or os.path.isfile(shp_path_user):
    #             logging.info('file already exists')
    #         else:
    #             logging.info('saving shapefile to server')
    #             if not os.path.exists(user_workspace):
    #                 os.makedirs(user_workspace)
    #                 os.chmod(user_workspace, 0o777)
    #                 os.makedirs(shp_path_user)
    #                 os.chmod(shp_path_user, 0o777)
    #             if not os.path.exists(shp_path_user):
    #                 os.makedirs(shp_path_user)
    #                 os.chmod(shp_path_user, 0o777)
    #             upload_shapefile(id, shp_path_user) # Run upload_shapefile function to upload file to the geoserver
    #         return HttpResponseRedirect('../') # Return to Home page
    # else:
    #     return HttpResponseRedirect('../') # Return to Home page


def upload_tiffiles(request):
    """
    Controller to upload new DEM files
    """
    files = request.FILES.getlist('files')
    print(files)
    #create new dir or check dir for shapefiles
    user_workspace_path = nasaaccess.get_user_workspace(request.user).path

    dem_path = os.path.join(user_workspace_path,'DEMfiles')
    # dem_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'user_workspaces','DEMfiles')
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
    print(filename)
    print(dem_path_directory)
    upload_dem(filename,dem_path_directory)
    return JsonResponse({"file":f'{filename}'})

    # if request.method == 'POST':
    #     form = UploadDEMForm(request.POST, request.FILES)
    #     id = request.FILES['DEMfile'].name
    #     if form.is_valid():
    #         form.save(commit=True)
    #         perm_file_path = os.path.join(data_path, 'DEMfiles', id)
    #         dem_path_user = os.path.join(nasaaccess.get_user_workspace(request.user).path, 'DEMfiles')
    #         print(perm_file_path)
    #         print(dem_path_user)
    #         if os.path.isfile(perm_file_path) or os.path.isfile(dem_path_user):
    #             logging.info('file already exists')
    #         else:
    #             logging.info('saving dem to server')
    #             if not os.path.exists(dem_path_user):
    #                 os.makedirs(dem_path_user)
    #                 os.chmod(dem_path_user, 0o777)
    #             upload_dem(id, dem_path_user)
    #         return HttpResponseRedirect('../')
    # else:
    #     return HttpResponseRedirect('../')


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

        #download the zip file using the browser's download dialogue box
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