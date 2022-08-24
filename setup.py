from setuptools import find_namespace_packages, setup
from tethys_apps.app_installation import find_resource_files

### Apps Definition ###
app_package = "nasaaccess"
release_package = "tethysapp-" + app_package

### Python Dependencies ###
dependencies = []

# -- Get Resource File -- #
resource_files = find_resource_files(
    "tethysapp/" + app_package + "/templates", "tethysapp/" + app_package
)
resource_files += find_resource_files(
    "tethysapp/" + app_package + "/public", "tethysapp/" + app_package
)
resource_files += find_resource_files(
    "tethysapp/" + app_package + "/scripts", "tethysapp/" + app_package
)

resource_files += find_resource_files(
    "tethysapp/" + app_package + "/workspaces", "tethysapp/" + app_package
)


setup(
    name=release_package,
    version="2.0.1",
    description="Web interface for accessing and visualizing climate and weather data from NASA's Earth Observing System Data and Information System (EOSDIS)",
    long_description="",
    keywords='"Hydrology", "GLDAS", "GPM"',
    author="Spencer McDonald, Ibrahim Mohammed, Giovanni Romero",
    author_email="ibrahim.mohammed@nasa.gov",
    url="https://github.com/imohamme/tethys_nasaaccess",
    license="NASA OPEN SOURCE AGREEMENT VERSION 1.3",
    packages=find_namespace_packages(),
    package_data={"": resource_files},
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
)
