
from django.core.exceptions import FieldDoesNotExist
from django.db.models.options import Options


class RestOptions(Options):
    has_auto_field = True
    auto_created = False
    abstract = False
    swapped = False
    managed = False
    virtual_fields = []

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta,*args,**kwargs)
        self._gmail_other_fields = {}

    def add_field(self, *args, **kwargs):
        pass

    def _bind(self):
        for field_name, field in self._gmail_fields.iteritems():
            setattr(self, field_name, field)
            field.set_attributes_from_name(field_name)
        self.pk = self._gmail_fields[self._gmail_pk_field]

    def get_fields(self, **kwargs):
        return self._get_fields()

    def get_field(self, field_name):
        try:
            return self._gmail_fields[field_name]
        except KeyError:
            try:
                return self._gmail_other_fields[field_name]
            except KeyError:
                raise FieldDoesNotExist()


