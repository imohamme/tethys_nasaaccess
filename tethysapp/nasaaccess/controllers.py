from django.shortcuts import render
from tethys_sdk.gizmos import SelectInput
from tethys_sdk.routing import controller

from .app import nasaaccess
# from .config import geoserver

Persistent_Store_Name = "catalog_db"
try:
    geoserver_password = nasaaccess.get_custom_setting("geoserver_password")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_password = ""   

try:
    geoserver_user = nasaaccess.get_custom_setting("geoserver_user")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_user = ""   

try:
    geoserver_URI = nasaaccess.get_custom_setting("geoserver_URI")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_URI = ""   

try:
    geoserver_workspace = nasaaccess.get_custom_setting("geoserver_workspace")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_workspace = ""   

try:
    nasaaccess_R = nasaaccess.get_custom_setting("nasaaccess_R")
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

@controller(name='home', url='nasaaccess')
def home(request):
    """
    Controller for the app home page.
    """

    # Get available Shapefiles and DEM files from app workspace and use them as options in drop down menus

    dem_options = []
    shp_options = []
    WORKSPACE = geoserver["workspace"]
    REST_URL = ""
    error_str = ""
    try:
        engine_geo = nasaaccess.get_spatial_dataset_service("ADPC", as_engine=True)
        # REST_URL = engine_geo.endpoint
        REST_URL=engine_geo.get_wms_endpoint().replace("wms","rest")
        layers__all = engine_geo.list_stores(WORKSPACE, True)
        print(layers__all)
        if layers__all["success"] is True:
            for layer in layers__all["result"]:
                if layer["resource_type"] == "dataStore":
                    shp_options.append((layer["name"], layer["name"]))
                if layer["resource_type"] == "coverageStore":
                    dem_options.append((layer["name"], layer["name"]))

    except Exception as e:
        error_str = (
            "Start the GeoServer Service or connect a different GeoServer service"
        )
        print(e)

    select_watershed = SelectInput(
        display_text="",
        name="select_watershed",
        multiple=False,
        original=False,
        options=shp_options,
        select2_options={
            "placeholder": "Select Boundary Shapefile",
            "allowClear": False,
        },
    )

    select_dem = SelectInput(
        display_text="",
        name="select_dem",
        multiple=False,
        original=False,
        options=dem_options,
        select2_options={"placeholder": "Select DEM", "allowClear": False},
    )
    context = {
        "select_watershed": select_watershed,
        "select_dem": select_dem,
        "geoserver_url": REST_URL,
        "geoserver_workspace": WORKSPACE,
        "error_str": error_str,
    }

    return render(request, "nasaaccess/home.html", context)
