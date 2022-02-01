import os

data_path = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/nasaaccess_data/')

nasaaccess_py3 = os.path.join('/home/gio/anaconda3/envs/tethys/bin/python3')

nasaaccess_script = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.py')

nasaaccess_log = os.path.join('/home/gio/tethysdev/tethys_nasaaccess/subprocesses/nasaaccess.log')

geoserver = {'rest_url':'http://localhost:8081/geoserver/rest/',
             'wms_url':'http://localhost:8081/geoserver/wms/',
             'user':'admin',
             'password':'geoserver',
             'workspace':'nasaaccess',
             'URI': 'nasaaccess'}