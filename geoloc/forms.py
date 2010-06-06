from django import forms
from geoloc import widgets

class Position(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.name = ''

    def __unicode__(self):
        return unicode(self.lat)


class Location(object):
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon


class LocationField(forms.MultiValueField):

    def __init__(self, *args, **kw):
        name_field = forms.CharField(*args, **kw)
        lat_field = forms.FloatField()
        lon_field = forms.FloatField()
        widget = kw.pop('widget', widgets.GMapLocation)
        super(LocationField, self).__init__(
                fields=(name_field, lat_field, lon_field,),
                widget=widget, required=kw.get('required', False))

    def compress(self, data):
        if not data:
            return None
        return Location(data[0], data[1], data[2])


class PositionField(forms.MultiValueField):
    widget = widgets.GMapLocation

    def __init__(self, *args, **kw):
        name_field = forms.CharField(*args, **kw)
        lat_field = forms.FloatField(required=False)
        lon_field = forms.FloatField(required=False)
        super(PositionField, self).__init__(
                fields=(lat_field, lon_field,), *args, **kw)

    def clean(self, value):
        return super(PositionField, self).clean(value[1:])

    def compress(self, data):
        if not data:
            return None
        return Position(data[0], data[1])
