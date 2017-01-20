from django.db.models.options import Options



class RestOptions(Options):
    auto_created = False
    abstract = False
    swapped = False
    managed = False
    virtual_fields = []

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta,*args,**kwargs)

        self.auto_created = False
        self.abstract = False
        self.swapped = False
        self.managed = False
        self.virtual_fields = []

    def can_migrate(self, connection=None):
        return False

