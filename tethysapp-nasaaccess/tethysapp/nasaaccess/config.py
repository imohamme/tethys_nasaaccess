from .app import nasaaccess as app
import os


# data_path = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/nasaaccess_data/')

# nasaaccess_py3 = os.path.join('/home/gio/anaconda3/envs/tethys/bin/python3')

# nasaaccess_script = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.py')

# nasaaccess_log = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.log')

# geoserver = {'rest_url':'http://localhost:8081/geoserver/rest/',
#              'wms_url':'http://localhost:8081/geoserver/wms/',
#              'user':'admin',
#              'password':'geoserver',
#              'workspace':'nasaaccess',
#              'URI': 'nasaaccess'}

data_path = app.get_custom_setting('data_path')
nasaaccess_py3 = app.get_custom_setting('nasaaccess_py3')
nasaaccess_script = app.get_custom_setting('nasaaccess_script')
nasaaccess_log = app.get_custom_setting('nasaaccess_log')
geoserver_workspace = app.get_custom_setting('geoserver_workspace')
geoserver_URI = app.get_custom_setting('geoserver_URI')

geoserver = {'rest_url':'http://localhost:8081/geoserver/rest/',
             'wms_url':'http://localhost:8081/geoserver/wms/',
             'user':'admin',
             'password':'geoserver',
             'workspace':geoserver_workspace,
             'URI': geoserver_URI}

