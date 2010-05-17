from django import forms
from django.utils.safestring import mark_safe
from geoloc import settings

class GMapLocation(forms.MultiWidget):
    class Media:
        js = ('http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GMAP_API_KEY,)

    def __init__(self, attrs=None):
        widgets = (forms.TextInput,
            forms.HiddenInput(attrs={'class':'gmap_lat'}), 
            forms.HiddenInput(attrs={'class':'gmap_lon'}),
        )
        super(GMapLocation, self).__init__(widgets,
                attrs)

    def decompress(self, location):
        if location:
            return location.name, location.lat, location.lon
        return '', None, None

    def render(self, name, value, attrs=None):
        result = super(GMapLocation, self).render(name, value, attrs)
        if not isinstance(value, (list, tuple)):
            value = self.decompress(value)
        location, lat, lon = value
        result = result + u'''
        <input type="button" id="%(name)s_search" value="%(search_label)s" />
        <div id="%(name)s_map_box" class="map-overlay">
            <div id="%(name)s_map_message"></div>
            <div id="%(name)s_map"></div>
            </div>
            <script type="text/javascript">
            $(document).ready(function() {
                var map_%(name)s_types = [G_NORMAL_MAP, G_SATELLITE_MAP, G_PHYSICAL_MAP];
                map_%(name)s = new GMap2(document.getElementById('%(name)s_map'),
                    {mapTypes: map_%(name)s_types});
                map_%(name)s.addControl(new GLargeMapControl());
                map_%(name)s.addControl(new GScaleControl());
                map_%(name)s.addControl(new GMapTypeControl());
                map_%(name)s.message_box = $('#id_%(name)s_map_message');
                map_%(name)s.store_zoom = true;
                map_%(name)s.lat_input = $('#id_%(name)s_1');
                map_%(name)s.lon_input = $('#id_%(name)s_2');
                map_%(name)s.geocoder = new GClientGeocoder();
                map_%(name)s.geocoder.setCache(new GGeocodeCache());
                map_%(name)s.loc_marker = new GMarker(
                    new GLatLng(%(lat)s, %(lon)s), {draggable: true});
                map_%(name)s.accept_point = function(ev) {
                    var map = this;
                    if(!$('#id_%(name)s_0').val()) {
                        $('#id_%(name)s_0').val(ev.getTitle());
                    }
                    map.store_zoom = true;
                    $('#id_%(name)s_1').val(ev.getLatLng().lat());
                    $('#id_%(name)s_2').val(ev.getLatLng().lng());
                };
                map_%(name)s.on_change_location = function(keyword) {
                    var bounds = new GLatLngBounds();
                    var map = this;
                    if(!keyword) return;
                    map.geocoder.getLocations(keyword, function(points) {
                        map.clearOverlays();
                        if($(points.Placemark).length==1) {
                            var _p = points.Placemark[0].Point.coordinates;
                            map.lat_input.val(_p[1]);
                            map.lon_input.val(_p[0]);
                            map.store_zoom = true;
                        } else {
                            map.store_zoom = false;
                            map.message_box.html('%(many_places_message)s').show();
                        }

                        $(points.Placemark).each(function() {
                            var map = map_%(name)s;
                            var point = new GLatLng(this.Point.coordinates[1],
                                this.Point.coordinates[0]);
                            bounds.extend(point);
                            var address = this.address;
                            var marker = new GMarker(point, {draggable: true, title: address});
                            map.addOverlay(marker);
                            function _on_multi_accept(ev) {
                                map.message_box.hide();
                                map.setCenter(this.getLatLng());
                                map.clearOverlays();
                                var marker = new GMarker(this.getLatLng(), {draggable: true, title: address});
                                map.addOverlay(marker);
                                GEvent.addListener(marker, 'dragend', function() {
                                    map.accept_point(this);
                                });
                                map.accept_point(this);
                                if(map.getZoom()<11) {
                                    map.setZoom(11);
                                    }
                            }
                            GEvent.addListener(marker, "click", _on_multi_accept);
                            GEvent.addListener(marker, "dragend", _on_multi_accept);
                        });

                        if(points.Placemark.length>1) {
                            map.setCenter(bounds.getCenter(), map.getBoundsZoomLevel(bounds));
                        } else if(points.Placemark.length==1){
                            map.setCenter(bounds.getCenter(), 12);
                        }
                    });
                };

                $('#id_%(name)s_0').change(function() {
                    if(!map_%(name)s.lat_input.val() || 
                        !map_%(name)s.lon_input.val()) {
                        map_%(name)s.on_change_location($(this).val());
                    }
                });

                $('#%(name)s_search').click(function(ev) {
                    map_%(name)s.on_change_location($('#id_%(name)s_0').val());
                });

                GEvent.addListener(map_%(name)s.loc_marker, 'dragend', function() {
                    map_%(name)s.accept_point(this);
                });

                map_%(name)s.addOverlay(map_%(name)s.loc_marker);
                map_%(name)s.setCenter(new GLatLng(%(lat)s, %(lon)s), %(zoom)d);
            });
                    
            </script>
            ''' % {
                    'name': name, 
                    'location': location,
                    'search_label': 'Search on map', 
                    'many_places_message': 'Select only one location from result',
                    'lat': lat or settings.MAP_DEFAULT_COORDS[0], 
                    'lon': lon or settings.MAP_DEFAULT_COORDS[1],
                    'zoom': settings.GMAP_DEFAULT_ZOOM,
                }

        return mark_safe(result)
