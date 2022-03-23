from tethys_sdk.base import TethysAppBase, url_map_maker

from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, SpatialDatasetServiceSetting,CustomSetting

class nasaaccess(TethysAppBase):
    """
    Tethys app class for nasaaccess.
    """

    name = 'Nasaaccess'
    index = 'nasaaccess:home'
    icon = 'nasaaccess/images/nasaaccess.png'
    package = 'nasaaccess'
    root_url = 'nasaaccess'
    color = '#3e557a'
    description = 'Web interface for downloading precipitation and air temperature data from NASA&#39;s EarthData website'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='nasaaccess',
                controller='nasaaccess.controllers.home'
            ),
            UrlMap(
                name='download_files',
                url='run/',
                controller='nasaaccess.ajax_controllers.run_nasaaccess'
            ),
            UrlMap(
                name='upload_shapefiles',
                url='nasaaccess/upload_shp',
                controller='nasaaccess.ajax_controllers.upload_shapefiles'
            ),
            UrlMap(
                name='upload_tiffiles',
                url='nasaaccess/upload_dem',
                controller='nasaaccess.ajax_controllers.upload_tiffiles'
            ),
            UrlMap(
                name='download',
                url='nasaaccess/download',
                controller='nasaaccess.ajax_controllers.download_data'
            ),
            UrlMap(
                name='plot',
                url='nasaaccess/plot',
                controller='nasaaccess.ajax_controllers.plot_data'
            ),
            UrlMap(
                name='getValues',
                url='nasaaccess/getValues',
                controller='nasaaccess.ajax_controllers.getValues'
            )
        )

        return url_maps
   
    ## custom settings ##
    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name='data_path',
                type=CustomSetting.TYPE_STRING,
                description='Data Directory for Downloads',
                required=False
            ),
            CustomSetting(
                name='nasaaccess_R',
                type=CustomSetting.TYPE_STRING,
                description='R interpreter',
                required=False
            ),
            CustomSetting(
                name='nasaaccess_script',
                type=CustomSetting.TYPE_STRING,
                description='Path to the nasaaccess R script file',
                required=False
            ),
            CustomSetting(
                name='nasaaccess_log',
                type=CustomSetting.TYPE_STRING,
                description='Path to the nasaaccess log file',
                required=False
            ),
            CustomSetting(
                name='geoserver_workspace',
                type=CustomSetting.TYPE_STRING,
                description='Geoserver Workspace',
                required=False
            ),
            CustomSetting(
                name='geoserver_URI',
                type=CustomSetting.TYPE_STRING,
                description='Geoserver URI',
                required=False
            ),
            CustomSetting(
                name='geoserver_user',
                type=CustomSetting.TYPE_STRING,
                description='Geoserver User',
                required=False
            ),
            CustomSetting(
                name='geoserver_password',
                type=CustomSetting.TYPE_STRING,
                description='Geoserver Password',
                required=False
            ),
        )

        return custom_settings

    #### Persistant storage ###
    def persistent_store_settings(self):
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='catalog_db',
                description='forms database',
                initializer='nasaaccess.init_stores.init_db',
                required=True
            ),
        )
        return ps_settings

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name='ADPC',
                description='GeoServer service for the shapefiles and DEMS files.',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
        )

        return sds_settings