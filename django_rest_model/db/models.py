import inspect

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db.models.base import ModelState
from django.db.models.fields.related import ForeignObjectRel
from django_rest_model.db.options import RestOptions

from .managers import RestManager, PaginatedRestManager


class Constructor(type):
    def __new__(cls, name, bases, attrs):

        module = attrs.pop('__module__')

        super_new = super(Constructor, cls).__new__

        parents = [b for b in bases if isinstance(b, Constructor)]
        if not parents:
            return super_new(cls, name, bases, attrs)


        new_attrs = {'__module__': module}
        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        new_class = super_new(cls, name, bases, new_attrs)

        '''
        print('-------------------------------------------------------------------')
        print('repr',repr(new_class))
        print(' ')
        print('type',type(new_class))
        print(' ')
        print('attrs',attrs)
        print(' ')
        print('new_attrs', new_attrs)
        print(' ')
        print('_default_manager', new_class._default_manager)
        print(' ')
        print('-------')
        '''

        #######
        #
        #  add default manager
        #
        #######

        try:
            dm = attrs.pop('_default_manager')
            new_class._default_manager = dm(new_class)
        except KeyError:
            if hasattr(new_class,'_default_manager'):
                new_class._default_manager.model = new_class

        new_class.objects = new_class._default_manager


        #######
        #
        #  attach meta attributes
        #
        #######
        attrs.pop('Meta', None)
        meta = getattr(new_class, 'Meta', None)

        app_config = apps.get_containing_app_config(module)
        app_label = None
        if getattr(meta, 'app_label', None) is None:
            if app_config is None:
                raise RuntimeError(
                    "Model class %s.%s doesn't declare an explicit "
                    "app_label and isn't in an application in "
                    "INSTALLED_APPS." % (module, name)
                )
            else:
                app_label = app_config.label
        _meta = RestOptions(meta,app_label)
        new_class.add_to_class('_meta',_meta)

        #######
        #
        #  attach fields
        #
        #######

        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        new_class._meta.concrete_model = new_class
        new_class._meta.apps.register_model(new_class._meta.app_label, new_class)

        return new_class

    def add_to_class(cls, name, value):
        '''
        copied from https://github.com/django/django/blob/master/django/db/models/base.py to add fields to the class
        :param name:
        :param value:
        :return:
        '''
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def __init__(self, name, bases, attrs, **kwargs):
        super(Constructor, self).__init__(name, bases, attrs)


class BaseModel (object,metaclass=Constructor):
    _deferred = False
    _state = ModelState()
    objects = None #IDE Autocompletion

    class DoesNotExist(ObjectDoesNotExist):pass
    class MultipleObjectsReturned(ObjectDoesNotExist):pass

    class Meta:pass

class RestModel(BaseModel):

    _default_manager = RestManager

    def __init__(self, *args, **kwargs):
        self.process_fields(*args, **kwargs)

    def process_fields(self,*args, **kwargs):
        '''
        copied from https://github.com/django/django/blob/master/django/db/models/base.py to add the values of the fields to the class
        :param args:
        :param kwargs:
        :return:
        '''

        _DEFERRED = self._deferred
        _setattr = setattr
        opts = self._meta

        # There is a rather weird disparity here; if kwargs, it's set, then args
        # overrides it. It should be one or the other; don't duplicate the work
        # The reason for the kwargs check is that standard iterator passes in by
        # args, and instantiation for iteration is 33% faster.
        if len(args) > len(opts.concrete_fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")

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
                if rel_obj is not _DEFERRED:
                    _setattr(self, field.name, rel_obj)
            else:
                if val is not _DEFERRED:
                    _setattr(self, field.attname, val)

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    def save(self):
        new_instance = self.objects.create(self)
        for field in new_instance._meta.get_fields():
            if getattr(new_instance,field.attname):
                value = getattr(new_instance,field.attname)
                setattr(self,field.attname,value)
        self._state.adding = False

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

    def _get_pk_val(self, meta=None):
        if not meta:
            meta = self._meta
        return getattr(self, meta.pk.attname)

    def _set_pk_val(self, value):
        return setattr(self, self._meta.pk.attname, value)

    pk = property(_get_pk_val, _set_pk_val)

    @property
    def _serializer(self):
        raise NotImplementedError

    def get_serializer(self):
        return self._serializer


class PaginatedDRFModel(RestModel):
    _default_manager = PaginatedRestManager