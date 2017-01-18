from django.core.exceptions import FieldDoesNotExist
from django.db.models import AutoField
from django.db.models.base import ModelState
from django.db.models.fields.related import ForeignObjectRel


from .managers import RestManager, PaginatedRestManager


class Constructor(type):
    def __new__(cls, name, bases, attrs):

        klass = super(Constructor, cls).__new__(cls, name, bases, attrs)
        try:
            dm = attrs.pop('_default_manager')
            klass._default_manager = dm
        except KeyError:
            pass # _default_manager already set from inheritance

        klass.objects = klass._default_manager(klass)

        #stuff for foreign Key
        #Todo: Options

        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(klass, 'Meta', None)
        else:
            meta = attr_meta

        setattr(klass,'_meta', meta)

        setattr(klass._meta,'model_name',name)
        if not getattr(klass,'id',False):
            auto = AutoField(verbose_name='ID', primary_key=True, auto_created=True)
            setattr(klass,'id', auto)
        setattr(klass._meta, 'pk',getattr(klass,'id'))
        setattr(klass._meta, 'object_name',name)
        setattr(klass._meta, 'label', name)

        return klass

    def __init__(self, name, bases, attrs, **kwargs):
        super(Constructor, self).__init__(name, bases, attrs)


class RestModel(object,metaclass = Constructor):
    _deferred = False
    _state = ModelState()
    _default_manager = RestManager
    objects = None #IDE Autocompletion

    class DoesNotExist(Exception):pass
    class MultipleObjectsReturned(Exception):pass

    class Meta:pass

    def __init__(self,*args, **kwargs):
        pass

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    def save(self):
        self.objects.create(self)

    def __eq__(self, other):
        if isinstance(other, RestModel):
            return self.pk == other.pk
        return False

    def full_clean(self, *args, **kwargs):
        pass

    def validate_unique(self, *args, **kwargs):
        pass

    def _get_unique_checks(self, *args, **kwargs):
        return ([], [],)

    def _get_pk_val(self):
        return None

    @property
    def _serializer(self):
        raise NotImplementedError

    def get_serializer(self):
        return self._serializer


class PaginatedDRFModel(RestModel):
    _default_manager = PaginatedRestManager