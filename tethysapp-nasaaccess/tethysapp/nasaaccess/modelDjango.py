from django.db import models
import os, logging
from .config import *


logging.basicConfig(filename=nasaaccess_log,level=logging.INFO)



# Model for the Upload Shapefiles form
class Shapefiles(models.Model):
    shapefile = models.FileField(upload_to=os.path.join(data_path, 'temp', 'shapefiles'),max_length=500)

    class Meta:
        app_label = 'nasaaccess'

# Model for the Upload DEM files form
class DEMfiles(models.Model):
    DEMfile = models.FileField(upload_to=os.path.join(data_path, 'temp', 'DEMfiles'),max_length=500)
    class Meta:
        app_label = 'nasaaccess'
# Model for data access form
class accessCode(models.Model):
    access_code = models.CharField(max_length=6)

    class Meta:
        app_label = 'nasaaccess'
