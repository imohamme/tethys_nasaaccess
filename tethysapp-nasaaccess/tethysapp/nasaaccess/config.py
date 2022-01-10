import os

data_path = os.path.join('/Users/imohamme/Documents/Web_NASAaccess/nasaaccess_data/')

nasaaccess_py3 = os.path.join('/Users/imohamme/anaconda3/envs/tethys/bin/python3')

nasaaccess_script = os.path.join('/Users/imohamme/Documents/Web_NASAaccess/subprocesses/nasaaccess.py')

nasaaccess_log = os.path.join('/Users/imohamme/Documents/Web_NASAaccess/subprocesses/nasaaccess.log')

geoserver = {'rest_url':'http://localhost:8080/geoserver/rest/',
             'wms_url':'http://localhost:8080/geoserver/wms/',
             'user':'admin',
             'password':'geoserver',
             'workspace':'nasaaccess',
             'URI': 'nasaaccess'}