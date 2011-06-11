from django import forms
from django.utils.safestring import mark_safe
from geoloc import settings
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings as django_settings


class GMapLocation(forms.MultiWidget):
    class Media:
        js = ('http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GMAP_API_KEY,)

    def __init__(self, attrs=None, template_name='geoloc/gmap_location_field.html'):
        self.template_name = template_name
        widgets = (
            forms.TextInput(),
            forms.HiddenInput(attrs={'class':'gmap_lat'}), 
            forms.HiddenInput(attrs={'class':'gmap_lon'}),
        )
        attrs = attrs or {}

        self.zoom_input = attrs.pop('zoom_input', None)
        super(GMapLocation, self).__init__(widgets,
                attrs=attrs)

    def decompress(self, location):
        if location:
            return location.name, location.lat, location.lon
        return '', None, None

    def render(self, name, value, attrs=None):
        result = super(GMapLocation, self).render(name, value, attrs)
        if not isinstance(value, (list, tuple)):
            value = self.decompress(value)
        location, lat, lon = value
        zoom_input = self.zoom_input or '%s_zoom' % name
        zoom = attrs.pop('zoom', settings.GMAP_DEFAULT_ZOOM)

        result = result + render_to_string(self.template_name, {
            'MEDIA_URL': django_settings.MEDIA_URL,
            'name': name, 
            'location': location,
            'search_label': _('Search on map'), 
            'many_places_message': _('Select only one location from result'),
            'lat': lat or settings.MAP_DEFAULT_COORDS[0], 
            'lon': lon or settings.MAP_DEFAULT_COORDS[1],
            'zoom': zoom,
            'zoom_input': zoom_input,
        })

        return mark_safe(result)

