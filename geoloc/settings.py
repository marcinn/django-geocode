from django.conf import settings

MAP_DEFAULT_COORDS = getattr(settings, 'GEOLOC_MAP_DEFAULT_COORDS', (51.919438, 19.145136))
GMAP_DEFAULT_ZOOM = getattr(settings, 'GEOLOC_GMAP_DEFAULT_ZOOM', 8)

GMAP_API_KEY = getattr(settings, 'GOOGLE_MAPS_API_KEY')
