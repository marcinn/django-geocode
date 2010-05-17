from django.db import models

# Create your models here.


class LocationMixin(object):
    location_name = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    gmap_zoom = models.IntegerField(null=True, blank=True)
    gmap_type = models.CharField(max_length=32, null=True, blank=True)

