from .app import nasaaccess as app


try:
    data_path = app.get_custom_setting('data_path')
except Exception as e:
    print("Please specify the custom settings")
    data_path = ''

try:
    nasaaccess_R = app.get_custom_setting('nasaaccess_R')
except Exception as e:
    print("Please specify the custom settings")
    nasaaccess_R = ''
try:
    R_script = app.get_custom_setting('nasaaccess_script')
except Exception as e:
    print("Please specify the custom settings")
    R_script = ''
try:
    nasaaccess_log = app.get_custom_setting('nasaaccess_log')
except Exception as e:
    print("Please specify the custom settings")
    nasaaccess_log = ''
try:
    geoserver_workspace = app.get_custom_setting('geoserver_workspace')
except Exception as e:
    print("Please specify the custom settings")
    geoserver_workspace = ''
try:
    geoserver_URI = app.get_custom_setting('geoserver_URI')
except Exception as e:
    print("Please specify the custom settings")
    geoserver_URI = ''

try:
    geoserver_user = app.get_custom_setting('geoserver_user')
except Exception as e:
    print("Please specify the custom settings")
    geoserver_store = ''
try:
    geoserver_password = app.get_custom_setting('geoserver_password')
except Exception as e:
    print("Please specify the custom settings")
    geoserver_store = ''

nasa_user = 'jonesj93'

nasa_password = 'ED!1z0m5tgb'
geoserver = {'user': geoserver_user,
             'password': geoserver_password,
             'workspace':geoserver_workspace,
             'URI': geoserver_URI} 


# data_path = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/nasaaccess_data/')

# nasaaccess_py3 = os.path.join('/home/gio/anaconda3/envs/tethys/bin/python3')

# nasaaccess_script = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.py')

# nasaaccess_log = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.log')
# geoserver_workspace = 'nasaaccess'
# geoserver_URI = 'nasaaccess'

# geoserver = {'rest_url':'http://localhost:8081/geoserver/rest/',
#              'wms_url':'http://localhost:8081/geoserver/wms/',
#              'user':'admin',
#              'password':'geoserver',
#              'workspace':'nasaaccess',
#              'URI': 'nasaaccess'}
# try:
#     nasaaccess_R = os.path.join('/home/gio/anaconda3/envs/tethys/bin/Rscript')
# except Exception as e:
#     print("Please specify the custom settings")
#     nasaaccess_R = ''
# try:
#     # R_script = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.R')
#     R_script = app.get_custom_setting('R_script')

# except Exception as e:
#     print("Please specify the custom settings")
#     R_script = ''

# try:
#     R_log = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.log')
# except Exception as e:
#     print("Please specify the custom settings")
#     R_log = ''    



# nasaaccess_R = os.path.join('/home/gio/anaconda3/envs/tethys/bin/Rscript')

# R_script = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.R')

# R_log = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.log')