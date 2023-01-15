.. .. |nasaAccess_logo| image:: images/nasaaccess.png
..    :scale: 5%

.. |github| image:: images/github30x30.png
            :target: https://github.com/imohamme/tethys_nasaaccess
            :scale: 70%
            :align: middle
            
.. |gmail| image:: images/gmail-logo-30x30.png
           :target: gromero@aquaveo.com
           :scale: 70%
           


=============================================
NASAaccess Web Application
=============================================

Overview
********

NASAaccess is an application build using the Tethys Platform framework, which uses the NASAaccess R package. The NASAaccess R package is available in conda, and it can generate gridded ascii tables of climate CMIP5, CMIP6, and weather data (GPM, TRMM, GLDAS) needed to drive various hydrological models (e.g., SWAT, VIC, RHESSys, …etc.).
The NASAaccess application provides the following functionalities for the NASA GPM, GLDAS,NEX-GDDP :

-  **NASA GLDAS**
    - **GLDASpolyCentroid**: Generate air temperature input files as well as air temperature stations file from *NASA GLDAS* remote sensing products.

    - **GLDASwat**: Generate SWAT air temperature input files as well as air temperature stations file from *NASA GLDAS* remote sensing products.

- **NASA GPM**
    - **GPM_NRT**: Generate Near Real Time (NRT) rainfall from *NASA GPM* remote sensing products.

    - **GPMpolyCentroid**: Generate rainfall input files as well as rain station file from *NASA GPM* remote sensing products.

    - **GPMswat**: Generate SWAT rainfall input files as well as rain stations file from *NASA GPM* remote sensing products.
- **NASA NEX_GDDP**
    - **NEX_GDDP_CMIP5**: Generate rainfall or air temperature as well as climate input stations file from NASA NEX-GDDP remote sensing climate change data products needed to drive various hydrological models.

    - **NEX_GDDP_CMIP6**: Generate rainfall or air temperature as well as climate input stations file from NASA NEX-GDDP-CMIP6 remote sensing climate change data products needed to drive various hydrological models.

Developers
----------
- **Spencer McDonald** - *Initial work*  |github|
- **Ibrahim Mohammed** - *Initial & Finishing work* |github|
- **Giovanni Romero** - *Finishing work* - |github|


