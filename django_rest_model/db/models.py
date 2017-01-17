from django.core.exceptions import FieldDoesNotExist
from django.db.models import AutoField
from django.db.models.base import ModelState
from django.db.models.fields.related import ForeignObjectRel


from .managers import RestManager


class Constructor(type):
    def __new__(cls, name, bases, attrs):

        klass = super(Constructor, cls).__new__(cls, name, bases, attrs)
        try:
            dm = attrs.pop('_default_manager')
            klass._default_manager = dm
        except KeyError:
            pass # _default_manager already instantiated from inheritance

        klass.objects = klass._default_manager(klass)

        class DoesNotExist(Exception):
            pass
        class MultipleObjectsReturned(Exception):
            pass

        klass.DoesNotExist = DoesNotExist
        klass.MultipleObjectsReturned = MultipleObjectsReturned

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
        setattr(klass._meta, 'object_name',"asdf")
        setattr(klass._meta, 'label', "asdf")

        return klass

    def __init__(self, name, bases, attrs, **kwargs):
        super(Constructor, self).__init__(name, bases, attrs)


class RestModel(object,metaclass = Constructor):
    _deferred = False
    _state = ModelState()
    _default_manager = RestManager
    objects = None #IDE Autocompletion

    class Meta:
        pass

    def __init__(self,*args, **kwargs):
        opts = self._meta
        if not kwargs:
            fields_iter = iter(opts.concrete_fields)
            # The ordering of the zip calls matter - zip throws StopIteration
            # when an iter throws it. So if the first iter throws it, the second
            # is *not* consumed. We rely on this, so don't change the order
            # without changing the logic.
            for val, field in zip(args, fields_iter):
                setattr(self, field.attname, val)
        else:
            # Slower, kwargs-ready version.
            fields_iter = iter(opts.fields)
            for val, field in zip(args, fields_iter):
                setattr(self, field.attname, val)
                kwargs.pop(field.name, None)

        for field in fields_iter:
            is_related_object = False
            # Virtual field
            if field.attname not in kwargs and field.column is None:
                continue
            if kwargs:
                if isinstance(field.remote_field, ForeignObjectRel):
                    try:
                        # Assume object instance was passed in.
                        rel_obj = kwargs.pop(field.name)
                        is_related_object = True
                    except KeyError:
                        try:
                            # Object instance wasn't passed in -- must be an ID.
                            val = kwargs.pop(field.attname)
                        except KeyError:
                            val = field.get_default()
                    else:
                        # Object instance was passed in. Special case: You can
                        # pass in "None" for related objects if it's allowed.
                        if rel_obj is None and field.null:
                            val = None
                else:
                    try:
                        val = kwargs.pop(field.attname)
                    except KeyError:
                        # This is done with an exception rather than the
                        # default argument on pop because we don't want
                        # get_default() to be evaluated, and then not used.
                        # Refs #12057.
                        val = field.get_default()
            else:
                val = field.get_default()

            if is_related_object:
                # If we are passed a related instance, set it using the
                # field.name instead of field.attname (e.g. "user" instead of
                # "user_id") so that the object gets properly cached (and type
                # checked) by the RelatedObjectDescriptor.
                setattr(self, field.name, rel_obj)
            else:
                setattr(self, field.attname, val)


        if kwargs:
            property_names = opts._property_names
            for prop in tuple(kwargs):
                try:
                    # Any remaining kwargs must correspond to properties or
                    # virtual fields.
                    if prop in property_names or opts.get_field(prop):
                        setattr(self, prop, kwargs[prop])
                        del kwargs[prop]
                except (AttributeError, FieldDoesNotExist):
                    pass
            if kwargs:
                raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    @property
    def pk(self):
        return self.id

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



class PaginatedDRFModel(RestModel):
    pass