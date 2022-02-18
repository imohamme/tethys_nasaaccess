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



# # Model for the Upload Shapefiles form
# class Shapefiles(models.Model):
#     shapefile = models.FileField(upload_to=os.path.join(data_path, 'temp', 'shapefiles'),max_length=500)

#     class Meta:
#         app_label = 'nasaaccess'

# # Model for the Upload DEM files form
# class DEMfiles(models.Model):
#     DEMfile = models.FileField(upload_to=os.path.join(data_path, 'temp', 'DEMfiles'),max_length=500)
#     class Meta:
#         app_label = 'nasaaccess'
# # Model for data access form
# class accessCode(models.Model):
#     access_code = models.CharField(max_length=6)

#     class Meta:
#         app_label = 'nasaaccess'

def nasaaccess_run(email, functions, watershed, dem, start, end, user_workspace,nexgdpp,nextgdppcmip):
    #identify where each of the input files are located in the server
    shp_path_sys = os.path.join(data_path, 'shapefiles', watershed, watershed + '.shp')
    shp_path_user = os.path.join(user_workspace, 'shapefiles', watershed, watershed + '.shp')
    shp_path = ''
    if os.path.isfile(shp_path_sys):
        shp_path = shp_path_sys
    if os.path.isfile(shp_path_user):
        shp_path = shp_path_user
    dem_path_sys = os.path.join(data_path, 'DEMfiles', dem, dem + '.tif')
    dem_path_user = os.path.join(user_workspace, 'DEMfiles',dem, dem + '.tif')
    dem_path = ''
    if os.path.isfile(dem_path_sys):
        dem_path = dem_path_sys
    if os.path.isfile(dem_path_user):
        dem_path = dem_path_user
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

    nexgdpp_str=separator.join(nexgdpp)
    nextgdppcmip_str=separator2.join(nextgdppcmip)

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
                                shp_path, dem_path, unique_path, tempdir+'/', start, end,nexgdpp_str,nextgdppcmip_str])
        return "nasaaccess is running"
    except Exception as e:
        logging.info(str(e))
        return str(e)

def upload_shapefile(id, shp_path):

    '''
    Check to see if shapefile is on geoserver. If not, upload it.
    '''

    # Create a string with the path to the zip archive
    # zip_archive = os.path.join(data_path, 'temp', 'shapefiles', id + '.zip')
    # zip_ref = zipfile.ZipFile(zip_archive, 'r')
    # zip_ref.extractall(shp_path)
    # zip_ref.close()
    # zip_archive = os.path.join(shp_path, id + '.zip')
    # if not os.path.exists(zip_archive):
    #     zipFiles(id, shp_path)
    SessionMaker = app.get_persistent_store_database(
        Persistent_Store_Name, as_sessionmaker=True)
    session = SessionMaker()
    prj_path = os.path.join(shp_path, id + '.prj')
    f = open(prj_path)
    validate = 0
    for line in f:
        if 'PROJCS' in line:
            validate = 1
            print('This shapefile is in a projected coordinate system. nasaaccess will only work on shapefiles in a geographic coordinate system')

    if validate == 0:
        print("here")
        # geoserver_engine = get_spatial_dataset_engine(name='ADPC')
        geoserver_engine = app.get_spatial_dataset_service('ADPC', as_engine = True)
        print(geoserver_engine)
        # response = geoserver_engine.get_layer(id, debug=True)
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
            store = id
            store_id = WORKSPACE + ':' + store
            print(shp_path)
            geoserver_engine.create_shapefile_resource(
                store_id=store_id,
                # shapefile_zip=zip_archive,
                shapefile_base=os.path.join(shp_path, id),
                overwrite=True
            )
    ## Save to database
    if session.query(Shapefiles).filter(Shapefiles.shapefile == id).first() is None:

        shapefile_geoserver=Shapefiles(shapefile=id)
        session.add(shapefile_geoserver)
        session.commit()
        session.close()


        ##Delete files
        # shutil.rmtree(shp_path)

    # os.remove(zip_archive)


def upload_dem(id, dem_path):

    '''
    upload dem to user workspace and geoserver
    '''
    SessionMaker = app.get_persistent_store_database(
        Persistent_Store_Name, as_sessionmaker=True)
    session = SessionMaker()
    # shutil.copy2(os.path.join(data_path, 'temp', 'DEMfiles', id), dem_path)
    geoserver_engine = app.get_spatial_dataset_service('ADPC', as_engine = True)

    # geoserver_engine = get_spatial_dataset_engine(name='ADPC')
    response = geoserver_engine.get_layer(id, debug=True)

    WORKSPACE = geoserver['workspace']
    GEOSERVER_URI = geoserver['URI']

    if response['success'] == False:
        print('DEM was not found on geoserver. Uploading it now from app workspace')

        # Create the workspace if it does not already exist
        response = geoserver_engine.list_workspaces()
        if response['success']:
            workspaces = response['result']
            if WORKSPACE not in workspaces:
                geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=GEOSERVER_URI)
        file_path = os.path.join(dem_path, id + '.tif')
        storename = id
        headers = {'Content-type': 'image/tiff', }
        user = geoserver['user']
        password = geoserver['password']
        data = open(file_path, 'rb').read()

        request_url = '{0}workspaces/{1}/coveragestores/{2}/file.geotiff'.format(geoserver['rest_url'],
                                                                                 WORKSPACE, storename)

        requests.put(request_url, verify=False, headers=headers, data=data, auth=(user, password))
    ## Save to database
    if session.query(DEMfiles).filter(DEMfiles.DEMfile == id).first() is None:

        dem_geoserver=DEMfiles(demfile=id)
        session.add(dem_geoserver)
        session.commit()
        session.close()
    # os.remove(os.path.join(data_path, 'temp', 'DEMfiles', id))
    # shutil.rmtree(dem_path)
