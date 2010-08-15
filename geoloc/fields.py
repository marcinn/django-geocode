from django import forms
from django.db import models
from geoloc import forms as geoforms

__all__ = ['PositionField', 'LocationField',]


_lat_field_name = lambda x: '%s_lat' % x
_lon_field_name = lambda x: '%s_lon' % x



class Position(object):
    def __init__(self, instance, lat_field_name, lon_field_name):
        self.instance = instance
        assert lat_field_name
        assert lon_field_name
        self.lat_field_name = lat_field_name
        self.lon_field_name = lon_field_name

    def _get_lat(self):
        return self.instance.__dict__[self.lat_field_name]

    def _set_lat(self, lat):
        setattr(self.instance, self.lat_field_name, lat)

    def _get_lon(self):
        return self.instance.__dict__[self.lon_field_name]

    def _set_lon(self, lon):
        setattr(self.instance, self.lon_field_name, lon)

    def _get_name(self):
        return ''

    def _set_name(self, val):
        pass

    name = property(_get_name, _set_name)
    lat = property(_get_lat, _set_lat)
    lon = property(_get_lon, _set_lon)


class Location(Position):
    def __init__(self, instance, lat_field, lon_field, location_field):
        self.location_field_name = location_field
        super(Location, self).__init__(instance, lat_field, lon_field)
    def _get_name(self):
        return self.instance.__dict__[self.location_field_name]
    def _set_name(self, name):
        self.instance.__dict__[self.location_field_name] = name
    name = property(_get_name, _set_name)

    def __unicode__(self):
        return self.name or ''



class PositionDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.lat_column = field._lat_field_name or _lat_field_name(field.name)
        self.lon_column = field._lon_field_name or _lon_field_name(field.name)

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')
        return Position(instance, self.lat_column, self.lon_column)
   
    def __set__(self, obj, value):
        if hasattr(value, 'lat') and hasattr(value, 'lon'):
            lat, lon = value.lat, value.lon
        elif isinstance(value, tuple):
            lat, lon = value
        elif value is None:
            lat, lon = None, None
        else:
            obj.__dict__[self.lat_column] = value
            return
            raise TypeError('Invalid position value type. Use Position or tuple.')
        obj.__dict__[self.lat_column] = lat
        obj.__dict__[self.lon_column] = lon


class LocationDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.lat_column = field.db_column_lat
        self.lon_column = field.db_column_lon

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')
        return Location(instance, self.lat_column, self.lon_column, self.field.db_column)
   
    def __set__(self, obj, value):
        if hasattr(value, 'name') and hasattr(value, 'lat')\
                and hasattr(value, 'lon'):
            lat, lon = value.lat, value.lon
            name = value.name
        elif value is None:
            lat, lon, name = None, None, None
        elif isinstance(value, (str, unicode)):
            name, lat, lon = value, None, None
        else:
            raise TypeError('Invalid location value type.')
        obj.__dict__[self.lat_column] = lat
        obj.__dict__[self.lon_column] = lon
        obj.__dict__[self.field.db_column] = name

            
class PositionField(models.FloatField):
    def __init__(self, *args, **kw):
        self._lat_field_name = kw.get('db_column')
        self._lon_field_name = kw.pop('db_column_lon', None)
        super(PositionField, self).__init__(*args, **kw)

    @property
    def db_column_lat(self):
        return self._lat_field_name or _lat_field_name(self.name)

    @property
    def db_column_lon(self):
        return self._lon_field_name or _lon_field_name(self.name)


    def contribute_to_class(self, cls, name):
        lon_field = models.FloatField(null=True, blank=True, editable=False,
                db_index=self.db_index)
        lon_field.creation_counter = self.creation_counter + 1
        cls.add_to_class(self._lon_field_name or _lon_field_name(name), lon_field)
        super(PositionField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, PositionDescriptor(self))

    def pre_save(self, model_instance, add):
        position = super(PositionField, self).pre_save(model_instance, add)
        lon = position.lon
        setattr(model_instance, self.db_column_lon, lon)
        return position.lat

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.lat

    def get_db_prep_value(self, value):
        try:
            return value.lat
        except AttributeError:
            return value

    def get_internal_type(self):
        return "FloatField"

    def to_python(self, value):
        if value is None:
            return None
        return value

    def formfield(self, **kw):
        defaults = {
                'form_class': geoforms.PositionField,
                'required': False,
        }
        defaults.update(kw)
        return super(PositionField, self).formfield(**defaults) 


class LocationField(models.CharField):
    def __init__(self, *args, **kw):
        self.add_lat_lon_fields = True
        self._lat_field_name = kw.pop('db_column_lat', None)
        self._lon_field_name = kw.pop('db_column_lon', None)
        super(LocationField, self).__init__(*args, **kw)

    @property
    def db_column_lat(self):
        return self._lat_field_name or _lat_field_name(self.name)

    @property
    def db_column_lon(self):
        return self._lon_field_name or _lon_field_name(self.name)

    def contribute_to_class(self, cls, name):
        if self.add_lat_lon_fields:
            lon_field = models.FloatField(null=self.null,editable=False,
                    db_index=self.db_index)
            lon_field.creation_counter = self.creation_counter + 1
            lat_field = models.FloatField(null=self.null,editable=False,
                    db_index=self.db_index)
            lat_field.creation_counter = self.creation_counter + 1
            cls.add_to_class(self._lon_field_name or _lon_field_name(name), lon_field)
            cls.add_to_class(self._lat_field_name or _lat_field_name(name), lat_field)
        super(LocationField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, LocationDescriptor(self))

    def pre_save(self, model_instance, add):
        value = super(LocationField, self).pre_save(model_instance, add)
        lon = value.lon
        lat = value.lat
        setattr(model_instance, self.db_column_lat, lat)
        setattr(model_instance, self.db_column_lon, lon)
        return value.name

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.name

    def get_db_prep_value(self, value):
        try:
            return value.name
        except AttributeError:
            return value

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        if value is None:
            return None
        return value

    def formfield(self, **kw):
        defaults = {
                'max_length': 255,
                'form_class': geoforms.LocationField,
                'required': False,
        }
        defaults.update(kw)
        return super(LocationField, self).formfield(**defaults) 


# south support
try:
    import south
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[((PositionField,),
            [], {
                'db_column': ('_lat_field_name', {}),
                'db_column_lon': ('_lon_field_name', {}),
            })],
            patterns=['geoloc\.fields\.'])
    add_introspection_rules(rules=[((LocationField,),
            [], {
                'db_column_lat': ('_lat_field_name', {}),
                'db_column_lon': ('_lon_field_name', {}),
            })],
            patterns=['geoloc\.fields\.'])

except:
    pass
