import os
import zipfile
from datetime import datetime, timedelta

import pandas as pd
from django.http import FileResponse, JsonResponse

# from .config import data_path
from .logic import nasaaccess_run, upload_dem, upload_shapefile
from .app import nasaaccess as app

try:
    data_path = app.get_custom_setting("data_path")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    data_path = ""   

def run_nasaaccess(request):

    """
    Controller to call nasaaccess R functions.
    """
    # Get selected parameters and pass them into nasaccess R scripts
    error_now = ""
    try:
        d_start = request.POST.getlist("startDate[]")
        d_end = request.POST.getlist("endDate[]")
        functions = request.POST.getlist("functions[]")
        nexgdpp = request.POST.getlist("nexgdpp[]")
        nextgdppcmip = request.POST.getlist("nextgdppcmip[]")

        watershed = request.POST.get("watershed")
        dem = request.POST.get("dem")
        email = request.POST.get("email")
        # user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path)
        app_workspace_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "workspaces", "app_workspace"
        )

        os.chmod(app_workspace_path, 0o777)
        result = nasaaccess_run(
            email,
            functions,
            watershed,
            dem,
            d_start,
            d_end,
            app_workspace_path,
            nexgdpp,
            nextgdppcmip,
        )
        return JsonResponse({"Result": str(result)})
    except Exception as e:
        error_now = str(e)
        return JsonResponse({"Error": str(e)})

    return JsonResponse({"Error": error_now})


def upload_shapefiles(request):

    """
    Controller to upload new shapefiles to app server and publish to geoserver
    """
    files = request.FILES.getlist("files")

    # create new dir or check dir for shapefiles
    app_workspace_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "workspaces", "app_workspace"
    )
    shp_path = os.path.join(app_workspace_path, "shapefiles")

    if not os.path.exists(shp_path):
        os.makedirs(shp_path)
        os.chmod(shp_path, 0o777)

    # Loop to create files in a directory with the name of the first file.
    for n, shp_file in enumerate(files):
        shp_path_directory = os.path.join(shp_path, shp_file.name.split(".")[0])
        shp_path_directory_file = os.path.join(shp_path_directory, shp_file.name)

        if not os.path.exists(shp_path_directory):
            os.makedirs(shp_path_directory)
            os.chmod(shp_path_directory, 0o777)
        if os.path.isfile(shp_path_directory_file):
            print("file already exists")
        else:
            with open(shp_path_directory_file, "wb") as dst:
                for chunk in files[n].chunks():
                    dst.write(chunk)

    filename = os.path.splitext(os.path.basename(shp_path_directory))[0].split(".")[0]
    checker = upload_shapefile(filename, shp_path_directory)
    return JsonResponse({"file": f"{filename}","checker":checker})


def upload_tiffiles(request):
    """
    Controller to upload new DEM files
    """
    files = request.FILES.getlist("files")
    print(files)
    # create new dir or check dir for shapefiles
    app_workspace_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "workspaces", "app_workspace"
    )

    dem_path = os.path.join(app_workspace_path, "DEMfiles")
    if not os.path.exists(dem_path):
        os.makedirs(dem_path)
        os.chmod(dem_path, 0o777)

    # Loop to create files in a directory with the name of the first file.
    for n, dem_file in enumerate(files):
        dem_path_directory = os.path.join(dem_path, dem_file.name.split(".")[0])
        dem_path_directory_file = os.path.join(dem_path_directory, dem_file.name)

        if not os.path.exists(dem_path_directory):
            os.makedirs(dem_path_directory)
            os.chmod(dem_path_directory, 0o777)
        if os.path.isfile(dem_path_directory_file):
            print("file already exists")
        else:
            with open(dem_path_directory_file, "wb") as dst:
                for chunk in files[n].chunks():
                    dst.write(chunk)

    filename = os.path.splitext(os.path.basename(dem_path_directory))[0].split(".")[0]

    checker = upload_dem(filename, dem_path_directory)
    return JsonResponse({"file": f"{filename}", "checker":checker})


def download_data(request):
    """
    Controller to download data using a unique access code emailed to the user when their data is ready
    """
    if request.method == "POST":
        print(request.POST)
        # get access code from form
        access_code = request.POST.get("access_code")

        # identify user's file path on the server
        unique_path = os.path.join(data_path, "outputs", access_code, "nasaaccess_data")

        # compress the entire directory into a .zip file
        def zipfolder(foldername, target_dir):
            zipobj = zipfile.ZipFile(foldername + ".zip", "w", zipfile.ZIP_DEFLATED)
            rootlen = len(target_dir) + 1
            for base, dirs, files in os.walk(target_dir):
                for file in files:
                    fn = os.path.join(base, file)
                    zipobj.write(fn, fn[rootlen:])

        zipfolder(unique_path, unique_path)

        path_to_file = os.path.join(
            data_path, "outputs", access_code, "nasaaccess_data.zip"
        )

        if os.path.exists(path_to_file):
            zip_file = open(path_to_file, "rb")
            return FileResponse(zip_file)

    return JsonResponse({"error": "There was an error during the response"})


def getValues(request):
    return_obj = {}
    file = request.POST["name"]
    func_name = request.POST["func"]
    access_code = request.POST["access_code"]
    print(file)
    new_path = ""
    unique_path = os.path.join(
        data_path, "outputs", access_code, "nasaaccess_data", access_code
    )
    if os.path.exists(unique_path) is False:
        unique_path = os.path.join(data_path, "outputs", access_code, "nasaaccess_data")

    if func_name == "GLDASpolyCentroid":
        pre_path = os.path.join(unique_path, "GLDASpolyCentroid")
        new_path = os.path.join(unique_path, "GLDASpolyCentroid", "temp_Master.txt")

    if func_name == 'GPM_NRT':
        pre_path = os.path.join(unique_path,'GPM_NRT')
        new_path = os.path.join(unique_path,'GPM_NRT','precipitationMaster.txt')
    
    if func_name == "GLDASwat":
        pre_path = os.path.join(unique_path, "GLDASwat")
        new_path = os.path.join(unique_path, "GLDASwat", "temp_Master.txt")

    if func_name == "GPMpolyCentroid":
        pre_path = os.path.join(unique_path, "GPMpolyCentroid")

        new_path = os.path.join(
            unique_path, "GPMpolyCentroid", "precipitationMaster.txt"
        )

    if func_name == "GPMswat":
        pre_path = os.path.join(unique_path, "GPMswat")

        new_path = os.path.join(unique_path, "GPMswat", "precipitationMaster.txt")

    if func_name == "NEX_GDPPswat":
        pre_path = os.path.join(unique_path, "NEXGDPP")
        new_path = os.path.join(unique_path, "NEXGDPP", "prGrid_Master.txt")

    if func_name == "NEX_GDPP_CMIP6":
        pre_path = os.path.join(unique_path, "NEX_GDPP_CMIP6")

        new_path = os.path.join(unique_path, "NEX_GDPP_CMIP6", "prGrid_Master.txt")

    if os.path.exists(new_path):
        path_file = os.path.join(pre_path, f"{file}.txt")
        mypd = pd.read_csv(path_file)
        if func_name == "NEX_GDPPswat" or func_name == "NEX_GDPP_CMIP6" or func_name == "GPM_NRT" or func_name == "GPMswat":
            new_pd = mypd.reset_index(drop=True)
        else:
            new_pd = mypd.reset_index()

        if func_name == "GLDASpolyCentroid" or func_name == "GLDASwat":
            if new_pd.empty:
                return_obj["max_val"] = []
                return_obj["min_val"] = []
            else:
                new_pd.columns = ["max_val", "min_val"]
                return_obj["max_val"] = new_pd["max_val"].to_list()
                return_obj["min_val"] = new_pd["min_val"].to_list()
        else:
            if new_pd.empty:
                return_obj["val"] = []
            else:
                print(new_pd)
                new_pd.columns = ["val"]
                return_obj["val"] = new_pd["val"].to_list()

        starting_date = list(mypd)
        date = datetime.strptime(starting_date[0], "%Y%m%d")
        date_arr = []
        for one_day in range(new_pd.shape[0]):
            new_date2 = date + timedelta(days=one_day)
            new_date_string = new_date2.strftime("%m/%d/%Y")
            date_arr.append(new_date_string)
        new_pd["time"] = date_arr
        return_obj["labels"] = new_pd["time"].to_list()

    return JsonResponse(return_obj)


def plot_data(request):
    """
    Controller to download data using a unique access code emailed to the user when their data is ready
    """
    response_obj = {}

    if request.method == "POST":
        # get access code from form
        access_code = request.POST["access_code"]

        # identify user's file path on the server
        unique_path = os.path.join(
            data_path, "outputs", access_code, "nasaaccess_data", access_code
        )
        if os.path.exists(unique_path) is False:
            unique_path = os.path.join(
                data_path, "outputs", access_code, "nasaaccess_data"
            )

        # get the series from folders

        gldaspolycentroid_path = os.path.join(
            unique_path, "GLDASpolyCentroid", "temp_Master.txt"
        )
        gpnnrt_path = os.path.join(unique_path,'GPM_NRT','precipitationMaster.txt')

        gldasswat_path = os.path.join(unique_path, "GLDASwat", "temp_Master.txt")
        gpmpolycentroid_path = os.path.join(
            unique_path, "GPMpolyCentroid", "precipitationMaster.txt"
        )
        gpmswat_path = os.path.join(unique_path, "GPMswat", "precipitationMaster.txt")
        nextgdpp_path = os.path.join(unique_path, "NEXGDPP", "prGrid_Master.txt")
        nexgdppcmip6_path = os.path.join(
            unique_path, "NEX_GDPP_CMIP6", "prGrid_Master.txt"
        )

        # print(gldaspolycentroid_path)
        if os.path.exists(gldaspolycentroid_path):
            # print('GLDASpolyCentroid')
            data_master_1 = pd.read_csv(gldaspolycentroid_path)
            response_obj["GLDASpolyCentroid"] = data_master_1.to_dict("index")

        if os.path.exists(gpnnrt_path):
            # print('GPM_NRT')
            data_master_1 = pd.read_csv(gpnnrt_path)
            response_obj['GPM_NRT'] = data_master_1.to_dict('index')

        if os.path.exists(gldasswat_path):
            # print('GLDASwat')
            data_master_1 = pd.read_csv(gldasswat_path)
            response_obj["GLDASwat"] = data_master_1.to_dict("index")

        if os.path.exists(gpmpolycentroid_path):
            # print('GPMpolyCentroid')
            data_master_1 = pd.read_csv(gpmpolycentroid_path)
            response_obj["GPMpolyCentroid"] = data_master_1.to_dict("index")

        if os.path.exists(gpmswat_path):
            # print('GPMswat')
            data_master_1 = pd.read_csv(gpmswat_path)
            response_obj["GPMswat"] = data_master_1.to_dict("index")

        if os.path.exists(nextgdpp_path):
            # print('NEXGDPP')
            data_master_1 = pd.read_csv(nextgdpp_path)
            response_obj["NEX_GDPPswat"] = data_master_1.to_dict("index")
        if os.path.exists(nexgdppcmip6_path):
            # print('NEX_GDPP_CMIP6')
            data_master_1 = pd.read_csv(nexgdppcmip6_path)
            response_obj["NEX_GDPP_CMIP6"] = data_master_1.to_dict("index")
    return JsonResponse(response_obj)
