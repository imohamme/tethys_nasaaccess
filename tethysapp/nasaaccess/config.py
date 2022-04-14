from .app import nasaaccess as app

try:
    data_path = app.get_custom_setting("data_path")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    data_path = ""

try:
    nasaaccess_R = app.get_custom_setting("nasaaccess_R")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    nasaaccess_R = ""
try:
    R_script = app.get_custom_setting("nasaaccess_script")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    R_script = ""
try:
    nasaaccess_log = app.get_custom_setting("nasaaccess_log")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    nasaaccess_log = ""
try:
    geoserver_workspace = app.get_custom_setting("geoserver_workspace")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_workspace = ""
try:
    geoserver_URI = app.get_custom_setting("geoserver_URI")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_URI = ""

try:
    geoserver_user = app.get_custom_setting("geoserver_user")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_user = ""
try:
    geoserver_password = app.get_custom_setting("geoserver_password")
except Exception as e:
    print(e)
    print("Please specify the custom settings")
    geoserver_password = ""

nasa_user = "jonesj93"

nasa_password = "ED!1z0m5tgb"
geoserver = {
    "user": geoserver_user,
    "password": geoserver_password,
    "workspace": geoserver_workspace,
    "URI": geoserver_URI,
}
