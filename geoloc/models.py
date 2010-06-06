from django.db import models
from fields import LocationField

# Create your models here.


class LocationMixin(object):
    location_name = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    gmap_zoom = models.IntegerField(null=True, blank=True)
    gmap_type = models.CharField(max_length=32, null=True, blank=True)


class GeoTag(object):
    class Meta:
        abstract = True

    location = LocationField(null=True, max_length=255, blank=True)
    map_type = models.CharField(max_length=32, null=True, blank=True)
    map_zoom = models.IntegerField(null=True, blank=True)
