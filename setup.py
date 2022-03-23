from setuptools import setup, find_packages
from tethys_apps.app_installation import find_resource_files

### Apps Definition ###
app_package = 'nasaaccess'
release_package = 'tethysapp-' + app_package

### Python Dependencies ###
dependencies = []

# -- Get Resource File -- #
resource_files = find_resource_files('tethysapp/' + app_package + '/templates', 'tethysapp/' + app_package)
resource_files += find_resource_files('tethysapp/' + app_package + '/public', 'tethysapp/' + app_package)
resource_files += find_resource_files('tethysapp/' + app_package + '/workspaces', 'tethysapp/' + app_package)


setup(
    name=release_package,
    version='1.0.0',
    description='Web interface for downloading precipitation and air temperature data from NASA&#39;s EarthData website',
    long_description='',
    keywords='"Hydrology", "GLDAS&quot", "GPM", "SWAT"',
    author='Spencer McDonald, Ibrahim Mohammed, Giovanni Romero',
    author_email='ibrahim.mohammed@nasa.gov',
    url='',
    license='NASA OPEN SOURCE AGREEMENT VERSION 1.3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies
)
