import logging
import os
import random
import string
import subprocess

import requests
from geo.Geoserver import Geoserver

from .app import nasaaccess as app
# from .config import R_script, data_path, geoserver, nasaaccess_R

try:
    R_script = app.get_custom_setting("nasaaccess_script")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    R_script = ""   

try:
    data_path = app.get_custom_setting("data_path")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    data_path = ""   

try:
    geoserver_password = app.get_custom_setting("geoserver_password")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_password = ""   

try:
    geoserver_user = app.get_custom_setting("geoserver_user")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_user = ""   

try:
    geoserver_URI = app.get_custom_setting("geoserver_URI")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_URI = ""   

try:
    geoserver_workspace = app.get_custom_setting("geoserver_workspace")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_workspace = ""   

try:
    nasaaccess_R = app.get_custom_setting("nasaaccess_R")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    nasaaccess_R = ""

geoserver = {
    "user": geoserver_user,
    "password": geoserver_password,
    "workspace": geoserver_workspace,
    "URI": geoserver_URI,
}

def nasaaccess_run(
    email, functions, watershed, dem, start, end, app_workspace, nexgdpp, nextgdppcmip
):

    # identify where each of the input files are located in the server
    shp_path = os.path.join(app_workspace, "shapefiles", watershed, watershed + ".shp")
    dem_path = os.path.join(app_workspace, "DEMfiles", dem, dem + ".tif")
    unique_id = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )

    unique_path = os.path.join(data_path, "outputs", unique_id)
    if not os.path.exists(unique_path):
        os.makedirs(unique_path)
        os.chmod(unique_path, 0o777)
        unique_path = os.path.join(unique_path, "nasaaccess_data")

        os.makedirs(unique_path)
        os.chmod(unique_path, 0o777)
    functions = ",".join(functions)
    separator = ","
    separator2 = ","
    separator3 = ","
    separator4 = ","
    nexgdpp_str = separator.join(nexgdpp)
    nextgdppcmip_str = separator2.join(nextgdppcmip)
    start_str = separator3.join(start)
    end_str = separator4.join(end)

    print(nasaaccess_R)
    print(R_script)
    print(email)
    print(functions)
    print(nexgdpp_str)
    print(nextgdppcmip_str)
    print(unique_id)
    print(shp_path)
    print(dem_path)
    print(unique_path)
    print(start)
    print(end)

    logging.info(
        "Trying to run {0} functions for {1} watershed from {2} until {3}".format(
            functions, watershed, start, end
        )
    )
    try:
        # pass user's inputs and file paths to the nasaaccess python function that will run detached from the app
        # run = subprocess.call([nasaaccess_py3, nasaaccess_script, email, functions, unique_id,
        #                         shp_path, dem_path, unique_path, tempdir, start, end])
        subprocess.Popen(
            [
                nasaaccess_R,
                R_script,
                email,
                functions,
                unique_id,
                shp_path,
                dem_path,
                unique_path + "/",
                start_str,
                end_str,
                nexgdpp_str,
                nextgdppcmip_str,
            ]
        )
        return "nasaaccess is running"
    except Exception as e:
        logging.info(str(e))
        return str(e)


def upload_shapefile(id, shp_path):

    """
    Check to see if shapefile is on geoserver. If not, upload it.
    """

    prj_path = os.path.join(shp_path, id + ".prj")
    f = open(prj_path)
    validate = 0
    for line in f:
        if "PROJCS" in line:
            validate = 1
            print(
                "This shapefile is in a projected coordinate system. nasaaccess will only work on shapefiles in a geographic coordinate system"
            )
            return {"bool":False, "mssg":"This shapefile is in a projected coordinate system. nasaaccess will only work on shapefiles in a geographic coordinate system"}
    try:
        # if validate == 0:
        print("here")
        geoserver_engine = app.get_spatial_dataset_service("ADPC", as_engine=True)
        print(geoserver_engine)
        response = geoserver_engine.get_layer(id)
        print(response)
        WORKSPACE = geoserver["workspace"]
        GEOSERVER_URI = geoserver["URI"]

        if response["success"] is False:
            print(
                "Shapefile was not found on GeoServer. Uploading it now from app workspace"
            )

            # Create the workspace if it does not already exist
            response = geoserver_engine.list_workspaces()
            if response["success"]:
                workspaces = response["result"]
                if WORKSPACE not in workspaces:
                    geoserver_engine.create_workspace(
                        workspace_id=WORKSPACE, uri=GEOSERVER_URI
                    )

            # Upload shapefile to the workspaces
            store_id = WORKSPACE + ":" + id
            print(shp_path)
            geoserver_engine.create_shapefile_resource(
                store_id=store_id,
                shapefile_base=os.path.join(shp_path, id),
                overwrite=True,
            )
            return {"bool":True, "mssg":"Sucessful upload of the shapefile"}
        else:
            return {"bool":False, "mssg":"Shapefile is already on the GeoServer"}

    except Exception:
        print(e)
        return {"bool":False, "mssg":"it was not possible to upload the shapefile"}
    # return "uploaded shapefile"
    ##Delete files
    # shutil.rmtree(shp_path)


def upload_dem(id, dem_path):

    """
    upload dem to user workspace and geoserver
    """

    geoserver_engine = app.get_spatial_dataset_service("ADPC", as_engine=True)

    response = geoserver_engine.get_layer(id, debug=True)

    WORKSPACE = geoserver["workspace"]
    GEOSERVER_URI = geoserver["URI"]
    USER = geoserver["user"]
    PASSWORD = geoserver["password"]
    REST_URL = geoserver_engine.endpoint
    try:
        if response["success"] is False:
            print("DEM was not found on geoserver. Uploading it now from app workspace")

            # Create the workspace if it does not already exist
            response = geoserver_engine.list_workspaces()
            if response["success"]:
                workspaces = response["result"]
                if WORKSPACE not in workspaces:
                    geoserver_engine.create_workspace(
                        workspace_id=WORKSPACE, uri=GEOSERVER_URI
                    )
            file_path = os.path.join(dem_path, id + ".tif")

            geo = Geoserver(REST_URL.split("/rest")[0], username=USER, password=PASSWORD)

            geo.create_coveragestore(layer_name=id, path=file_path, workspace=WORKSPACE)

            new_style = geo.create_coveragestyle(raster_path=file_path, style_name=f'{id}_style', workspace=WORKSPACE,
                                    color_ramp='RdYlBu')
            geo.publish_style(layer_name=id, style_name=f'{id}_style', workspace=WORKSPACE)

            return True
        else:
            return False
    except Exception as e:
        print (e)
        return False

    # return "uploaded dem"
    ##Delete Files
    # shutil.rmtree(dem_path)
