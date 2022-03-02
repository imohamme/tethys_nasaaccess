from tethys_sdk.gizmos import *
from django.shortcuts import render
import os, datetime
# from .forms import UploadShpForm, UploadDEMForm, accessCodeForm
from .config import *
from .app import nasaaccess
# from .model import Base , DEMfiles, Shapefiles, accessCode
from .config import *
from geoserver.catalog import Catalog

# from tethys_sdk.workspaces import user_workspace
Persistent_Store_Name = 'catalog_db'


def home(request):
    """
    Controller for the app home page.
    """

    # Get available Shapefiles and DEM files from app workspace and use them as options in drop down menus
    # shapefile_path = os.path.join(data_path, 'shapefiles')
    # dem_path = os.path.join(data_path, 'DEMfiles')
    # if(nasaaccess.get_user_workspace(request.user).path.split('/anonymous_user')):
    #     user_workspace_path = nasaaccess.get_user_workspace(request.user).path.split('/anonymous_user')[0]
    
    # if(nasaaccess.get_user_workspace(request.user).path.split('/admin')):
    #     user_workspace_path = nasaaccess.get_user_workspace(request.user).path.split('/admin')[0]
    user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path)
    # user_workspace_path = os.path.join(user_workspace.path)
    dem_options = []
    shp_options = []
    WORKSPACE = geoserver['workspace']
    REST_URL = ''
    try:
        engine_geo =  nasaaccess.get_spatial_dataset_service('ADPC', as_engine = True)
        REST_URL =  engine_geo.endpoint
        layers__all = engine_geo.list_stores(WORKSPACE,True)
        if layers__all['success'] == True:
            for layer in layers__all['result']:
                if layer['resource_type'] == 'dataStore':
                    shp_options.append((layer['name'],layer['name']))
                if layer['resource_type'] == 'coverageStore':
                    dem_options.append((layer['name'],layer['name']))

    except Exception as e:
        print(e)

    select_watershed = SelectInput(display_text='',
                            name='select_watershed',
                            multiple=False,
                            original=False,
                            options=shp_options,
                            select2_options={'placeholder': 'Select Boundary Shapefile',
                                            'allowClear': False},
                            )

    select_dem = SelectInput(display_text='',
                                name='select_dem',
                                multiple=False,
                                original=False,
                                options=dem_options,
                                select2_options={'placeholder': 'Select DEM',
                                                    'allowClear': False},
                                )
    context = {
        'select_watershed': select_watershed,
        'select_dem': select_dem,
        'geoserver_url': REST_URL,
        'geoserver_workspace': WORKSPACE
    }



    return render(request, 'nasaaccess/home.html', context)