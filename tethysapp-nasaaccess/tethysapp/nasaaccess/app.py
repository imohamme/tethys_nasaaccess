from tethys_sdk.base import TethysAppBase, url_map_maker

from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, SpatialDatasetServiceSetting

class nasaaccess(TethysAppBase):
    """
    Tethys app class for nasaaccess.
    """

    name = 'nasaaccess'
    index = 'nasaaccess:home'
    icon = 'nasaaccess/images/nasaaccess.png'
    package = 'nasaaccess'
    root_url = 'nasaaccess'
    color = '#3e557a'
    description = 'Web interface for downloading precipitation and air temperature data from NASA&#39;s EarthData website'
    tags = '&quot;Hydrology&quot;, &quot;GLDAS&quot;, &quot;GPM&quot;, &quot;SWAT&quot;'
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
            )
        )

        return url_maps

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