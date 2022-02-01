from tethys_sdk.gizmos import *
from django.shortcuts import render
import os, datetime
from .forms import UploadShpForm, UploadDEMForm, accessCodeForm
from .config import *
from .app import nasaaccess
# from tethys_sdk.workspaces import user_workspace

def home(request):
    """
    Controller for the app home page.
    """

    # Get available Shapefiles and DEM files from app workspace and use them as options in drop down menus
    shapefile_path = os.path.join(data_path, 'shapefiles')
    dem_path = os.path.join(data_path, 'DEMfiles')
    if(nasaaccess.get_user_workspace(request.user).path.split('/anonymous_user')):
        user_workspace_path = nasaaccess.get_user_workspace(request.user).path.split('/anonymous_user')[0]
    
    if(nasaaccess.get_user_workspace(request.user).path.split('/admin')):
        user_workspace_path = nasaaccess.get_user_workspace(request.user).path.split('/admin')[0]
    # user_workspace = os.path.join(nasaaccess.get_user_workspace(request.user).path)

    # user_workspace_path = os.path.join(user_workspace.path)


    print(user_workspace_path)
    shp_options = []
    shp_files_sys = os.listdir(shapefile_path)
    # for f in shp_files_sys:
    #     name = f.split(".")[0]
    #     if name not in shp_options:
    #         shp_options.append((name,name))
    # if os.path.exists(os.path.join(user_workspace, 'shapefiles')):
    if os.path.exists(os.path.join(user_workspace_path, 'shapefiles')):

        shp_files_user = os.listdir(os.path.join(user_workspace_path, 'shapefiles'))
        for f in shp_files_user:
            name = f.split(".")[0]
            if name not in shp_options:
                shp_options.append((name,name))

    dem_options = []
    # dem_files_sys = os.listdir(dem_path)
    # for f in dem_files_sys:
    #     name = f.split(".")[0]
    #     if name not in dem_options:
    #         dem_options.append((name, name))
    # if os.path.exists(os.path.join(user_workspace, 'DEMfiles')):
    if os.path.exists(os.path.join(user_workspace_path, 'DEMfiles')):

        # dem_files_user = os.listdir(os.path.join(user_workspace, 'DEMfiles'))
        dem_files_user = os.listdir(os.path.join(user_workspace_path, 'DEMfiles'))

        for f in dem_files_user:
            name = f.split(".")[0]
            if name not in dem_options:
                dem_options.append((name, name))

    shpform = UploadShpForm()
    demform = UploadDEMForm()
    accesscodeform = accessCodeForm()


    # Set date picker options
    start = 'Jan 01, 2000'
    end = datetime.datetime.now().strftime("%b %d, %Y")
    format = 'M d, yyyy'
    startView = 'decade'
    minView = 'days'

    start_pick = DatePicker(name='start_pick',
                            autoclose=True,
                            format=format,
                            min_view_mode=minView,
                            start_date=start,
                            end_date=end,
                            start_view=startView,
                            today_button=False,
                            initial='Start Date')

    end_pick = DatePicker(name='end_pick',
                          autoclose=True,
                          format=format,
                          min_view_mode=minView,
                          start_date=start,
                          end_date=end,
                          start_view=startView,
                          today_button=False,
                          initial='End Date'
                          )


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
        'start_pick': start_pick,
        'end_pick': end_pick,
        'shpform': shpform,
        'demform': demform,
        'accesscodeform': accesscodeform,
        'select_watershed': select_watershed,
        'select_dem': select_dem
    }

    return render(request, 'nasaaccess/home.html', context)