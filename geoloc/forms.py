from django import forms
from geoloc import widgets

class Location(object):
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon


class LocationField(forms.MultiValueField):
    widget = widgets.GMapLocation

    def __init__(self, *args, **kw):
        name_field = forms.CharField(*args, **kw)
        lat_field = forms.FloatField()
        lon_field = forms.FloatField()
        super(LocationField, self).__init__(
                fields=(name_field, lat_field, lon_field,))

    def compress(self, data):
        return Location(data[0], data[1], data[2])
