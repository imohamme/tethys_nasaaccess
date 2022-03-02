from django.db import models
import os, random, string, subprocess, requests, shutil, logging, zipfile
from .config import *
from tethys_sdk.services import get_spatial_dataset_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from .app import nasaaccess as app
import shutil

logging.basicConfig(filename=nasaaccess_log,level=logging.INFO)

Base = declarative_base()
Persistent_Store_Name = 'catalog_db'

class Shapefiles(Base):
    __tablename__ = 'shapefiles'
    
    id = Column(Integer, primary_key=True)  # Record number.
    shapefile = Column(String(1000))

  
    def __init__(self, shapefile):
        self.shapefile= shapefile

class DEMfiles(Base):
    __tablename__ = 'demfiles'
    
    id = Column(Integer, primary_key=True)  # Record number.
    DEMfile = Column(String(1000))

  
    def __init__(self, demfile):
        self.DEMfile= demfile

class accessCode(Base):
    __tablename__ = 'accesscode'
    
    id = Column(Integer, primary_key=True)  # Record number.
    accessCode = Column(String(1000))


def set_rc_vars():
    old_dodsrcfile = os.environ.get('DAPRCFILE')
    old_netrc = os.environ.get('NETRC')
    os.environ['DAPRCFILE'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'app_workspace', '.dodsrc')
    os.environ['NETRC'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces', 'app_workspace', '.netrc')
    return old_dodsrcfile, old_netrc

def nasaaccess_run(email, functions, watershed, dem, start, end, app_workspace,nexgdpp,nextgdppcmip):
    set_rc_vars()
    #identify where each of the input files are located in the server
    # shp_path_sys = os.path.join(data_path, 'shapefiles', watershed, watershed + '.shp')
    shp_path = os.path.join(app_workspace, 'shapefiles', watershed, watershed + '.shp')
    # shp_path = ''
    # if os.path.isfile(shp_path_sys):
        # shp_path = shp_path_sys
    # if os.path.isfile(shp_path_user):
        # shp_path = shp_path_user
    # dem_path_sys = os.path.join(data_path, 'DEMfiles', dem, dem + '.tif')
    dem_path = os.path.join(app_workspace, 'DEMfiles',dem, dem + '.tif')
    # dem_path = ''
    # if os.path.isfile(dem_path_sys):
        # dem_path = dem_path_sys
    # if os.path.isfile(dem_path_user):
    #    dem_path = dem_path_user
    #create a new folder to store the user's requested data
    unique_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    unique_path = os.path.join(data_path, 'outputs', unique_id)
    if not os.path.exists(unique_path):
        os.makedirs(unique_path)
        os.chmod(unique_path, 0o777)
        unique_path = os.path.join(unique_path, 'nasaaccess_data')

        os.makedirs(unique_path)
        os.chmod(unique_path, 0o777)
    #create a temporary directory to store all intermediate data while nasaaccess functions run
    tempdir = os.path.join(data_path, 'temp', 'earthdata', unique_id)
    os.makedirs(tempdir)
    os.chmod(tempdir, 0o777)
    functions = ','.join(functions)
    separator=","
    separator2=","
    separator3=','
    separator4 = ','
    nexgdpp_str= separator.join(nexgdpp)
    nextgdppcmip_str= separator2.join(nextgdppcmip)
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
    print(tempdir)
    print(start)
    print(end)
    
    logging.info(
        "Trying to run {0} functions for {1} watershed from {2} until {3}".format(functions, watershed, start, end))
    try:
        #pass user's inputs and file paths to the nasaaccess python function that will run detached from the app
        # run = subprocess.call([nasaaccess_py3, nasaaccess_script, email, functions, unique_id,
        #                         shp_path, dem_path, unique_path, tempdir, start, end])
        run = subprocess.Popen([nasaaccess_R, R_script, email, functions, unique_id,
                                shp_path, dem_path, unique_path, tempdir+'/', start_str, end_str,nexgdpp_str,nextgdppcmip_str])
        return "nasaaccess is running"
    except Exception as e:
        logging.info(str(e))
        return str(e)

def upload_shapefile(id, shp_path):

    '''
    Check to see if shapefile is on geoserver. If not, upload it.
    '''

    prj_path = os.path.join(shp_path, id + '.prj')
    f = open(prj_path)
    validate = 0
    for line in f:
        if 'PROJCS' in line:
            validate = 1
            print('This shapefile is in a projected coordinate system. nasaaccess will only work on shapefiles in a geographic coordinate system')

    if validate == 0:
        print("here")
        geoserver_engine = app.get_spatial_dataset_service('ADPC', as_engine = True)
        print(geoserver_engine)
        response = geoserver_engine.get_layer(id)
        print(response)
        WORKSPACE = geoserver['workspace']
        GEOSERVER_URI = geoserver['URI']

        if response['success'] == False:
            print('Shapefile was not found on geoserver. Uploading it now from app workspace')

            # Create the workspace if it does not already exist
            response = geoserver_engine.list_workspaces()
            if response['success']:
                workspaces = response['result']
                if WORKSPACE not in workspaces:
                    geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=GEOSERVER_URI)

            # Upload shapefile to the workspaces
            store_id = WORKSPACE + ':' + id
            print(shp_path)
            geoserver_engine.create_shapefile_resource(
                store_id=store_id,
                shapefile_base=os.path.join(shp_path, id),
                overwrite=True
            )

        ##Delete files
        # shutil.rmtree(shp_path)



def upload_dem(id, dem_path):

    '''
    upload dem to user workspace and geoserver
    '''

    geoserver_engine = app.get_spatial_dataset_service('ADPC', as_engine = True)

    response = geoserver_engine.get_layer(id, debug=True)

    WORKSPACE = geoserver['workspace']
    GEOSERVER_URI = geoserver['URI']
    USER = geoserver['user']
    PASSWORD = geoserver['password']
    REST_URL = geoserver_engine.endpoint
    if response['success'] == False:
        print('DEM was not found on geoserver. Uploading it now from app workspace')

        # Create the workspace if it does not already exist
        response = geoserver_engine.list_workspaces()
        if response['success']:
            workspaces = response['result']
            if WORKSPACE not in workspaces:
                geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=GEOSERVER_URI)
        file_path = os.path.join(dem_path, id + '.tif')
        headers = {'Content-type': 'image/tiff', }

        data = open(file_path, 'rb').read()

        request_url = '{0}workspaces/{1}/coveragestores/{2}/file.geotiff'.format(REST_URL,
                                                                                 WORKSPACE,id)

        requests.put(request_url, verify=False, headers=headers, data=data, auth=(USER, PASSWORD))

        ##Delete Files
        # shutil.rmtree(dem_path)