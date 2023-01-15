{% set ALLOWED_HOST = salt['environ.get']('ALLOWED_HOST') %}
{% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
{% set CONDA_ENV_NAME = salt['environ.get']('CONDA_ENV_NAME') %}
{% set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') %}
{% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
{% set TETHYSAPP_DIR = salt['environ.get']('TETHYSAPP_DIR') %}
{% set APP_DB_HOST = salt['environ.get']('TETHYS_DB_HOST') %}
{% set APP_DB_PASSWORD = salt['environ.get']('TETHYS_DB_SUPERUSER_PASS') %}
{% set APP_DB_PORT = salt['environ.get']('TETHYS_DB_PORT') %}
{% set APP_DB_USERNAME = salt['environ.get']('TETHYS_DB_SUPERUSER') %}
{% set BYPASS_TETHYS_HOME_PAGE = salt['environ.get']('BYPASS_TETHYS_HOME_PAGE') %}
{% set ENABLE_OPEN_PORTAL = salt['environ.get']('ENABLE_OPEN_PORTAL') %}

{% set TETHYS_GS_HOST = salt['environ.get']('TETHYS_GS_HOST') %}
{% set TETHYS_GS_PASSWORD = salt['environ.get']('TETHYS_GS_PASSWORD') %}
{% set TETHYS_GS_PORT = salt['environ.get']('TETHYS_GS_PORT') %}
{% set TETHYS_GS_USERNAME = salt['environ.get']('TETHYS_GS_USERNAME') %}
{% set TETHYS_GS_PROTOCOL = salt['environ.get']('TETHYS_GS_PROTOCOL') %}
{% set TETHYS_GS_HOST_PUB = salt['environ.get']('TETHYS_GS_HOST_PUB') %}
{% set TETHYS_GS_PORT_PUB = salt['environ.get']('TETHYS_GS_PORT_PUB') %}
{% set TETHYS_GS_PROTOCOL_PUB = salt['environ.get']('TETHYS_GS_PROTOCOL_PUB') %}

{% set GEOSERVER_WORKSPACE = salt['environ.get']('GEOSERVER_WORKSPACE') %}
{% set GEOSERVER_URI = salt['environ.get']('GEOSERVER_URI') %}


# {% set TETHYS_CLUSTER_IP = salt['environ.get']('TETHYS_CLUSTER_IP') %}
# {% set TETHYS_CLUSTER_USERNAME = salt['environ.get']('TETHYS_CLUSTER_USERNAME') %}
# {% set TETHYS_CLUSTER_PKEY_FILE = salt['environ.get']('TETHYS_CLUSTER_PKEY_FILE') %}
# {% set TETHYS_CLUSTER_PKEY_PASSWORD = salt['environ.get']('TETHYS_CLUSTER_PKEY_PASSWORD') %}

{% set GEOSERVER_SERVICE_NAME = 'tethys_geoserver' %}
{% set GEOSERVER_SERVICE_URL = TETHYS_GS_USERNAME  + ':' + TETHYS_GS_PASSWORD  + '@' + TETHYS_GS_PROTOCOL + '://' + TETHYS_GS_HOST + ':' + TETHYS_GS_PORT %}
{% set GEOSERVER_SERVICE_PUB_URL = TETHYS_GS_PROTOCOL_PUB + '://' + TETHYS_GS_HOST_PUB + ':' + TETHYS_GS_PORT_PUB %}

{% set PS_SERVICE_NAME = 'nasaaccess' %}

Pre_WaterDataExplorer_Settings:
  cmd.run:
    - name: cat {{ TETHYS_HOME }}/tethys/tethys_portal/settings.py
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Sync_Apps:
  cmd.run:
    - name: tethys db sync
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Remove_Persistent_Stores_Database:
  cmd.run:
    - name: tethys services remove persistent {{ PS_SERVICE_NAME }} -f
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

# Create_Persistent_Stores_Database:
#   cmd.run:
#     - name: tethys services create persistent -n {{ PS_SERVICE_NAME }} -c {{ APP_DB_USERNAME }}:{{ APP_DB_PASSWORD }}@{{ APP_DB_HOST }}:{{ APP_DB_PORT }}
#     - shell: /bin/bash
#     - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

# Link_Persistent_Stores_Database:
#   cmd.run:
#     - name: tethys link persistent:{{ PS_SERVICE_NAME }} nasaaccess:ps_database:catalog_db
#     - shell: /bin/bash
#     - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

# Sync_App_Persistent_Stores:
#   cmd.run:
#     - name: tethys syncstores all
#     - shell: /bin/bash
#     - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Create_Spatial_Dataset_Service:
  cmd.run:
    - name: tethys services create spatial -t GeoServer -n {{ GEOSERVER_SERVICE_NAME }} -c {{ GEOSERVER_SERVICE_URL }} -p {{ GEOSERVER_SERVICE_PUB_URL }}
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"
Link_Geospatial_Services:
  cmd.run:
    - name: >
        tethys link spatial:{{ GEOSERVER_SERVICE_NAME }} nasaaccess:ds_spatial:ADPC
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

Setting_Extra_Middleware:
  cmd.run:
    - name: tethys settings --set MIDDLEWARE "['tethys_portal.custom_middleware.HealthCheckMiddleware']"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Making_Portal_Open:
  cmd.run:
    - name: tethys settings --set BYPASS_TETHYS_HOME_PAGE "${BYPASS_TETHYS_HOME_PAGE}" --set ENABLE_OPEN_PORTAL "${ENABLE_OPEN_PORTAL}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Changing_Upload_Size:
  cmd.run:
    - name: tethys settings --set DATA_UPLOAD_MAX_MEMORY_SIZE "${DATA_UPLOAD_MAX_MEMORY_SIZE}" --set DATA_UPLOAD_MAX_NUMBER_FIELDS "${DATA_UPLOAD_MAX_NUMBER_FIELDS}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Add_analitycal_config:
  cmd.run:
    - name: tethys settings --set ANALYTICS_CONFIG.GOOGLE_ANALYTICS_GTAG_PROPERTY_ID "${GOOGLE_ANALYTICS_GTAG_PROPERTY_ID}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/nasaaccess_setup_complete" ];"

Set_Custom_Settings:
  cmd.run:
    - name: >
        tethys app_settings set nasaaccess data_path {{ TETHYS_HOME }}/data_nasa &
        tethys app_settings set nasaaccess nasaaccess_R {{ CONDA_HOME }}/envs/{{ CONDA_ENV_NAME }}/bin/Rscript &
        tethys app_settings set nasaaccess nasaaccess_script {{ TETHYS_HOME }}/tethys_nasaaccess/nasaaccess/scripts/nasaaccess.R &
        tethys app_settings set nasaaccess geoserver_workspace {{ GEOSERVER_WORKSPACE }} & 
        tethys app_settings set nasaaccess geoserver_URI {{ GEOSERVER_URI }} & 
        tethys app_settings set nasaaccess geoserver_user {{ TETHYS_GS_USERNAME }} & 
        tethys app_settings set nasaaccess geoserver_password {{ TETHYS_GS_PASSWORD }} &

    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/nasaaccess_setup_complete" ];

Flag_Complete_Setup:
  cmd.run:
    - name: touch ${TETHYS_PERSIST}/nasaaccess_setup_complete
    - shell: /bin/bash
