from django_rest_model.db.query import RestQuerySet, PaginatedRestQuerySet


class BaseManager:

    def __init__(self, model, **kwargs):
        self.model = model
        self.initial_filter_query = kwargs.get('initial_filter_query', {})

    def order_by(self, *args, **kwargs):
        return self

    def using(self, *args, **kwargs):
        return self

    def iterator(self):
        return iter(self.get_queryset())

    def none(self, *args, **kwargs):
        return self.get_queryset().none()

    def all(self):
        return self.get_queryset().all()

    def count(self):
        return self.get_queryset().count()

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get_queryset(self):
        return self.queryset(
            model=self.model,
            filter_query=self.initial_filter_query,
        )

    @property
    def queryset(self):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)

    def create(self,*args, **kwargs):
        return self.get_queryset().create(*args, **kwargs)

    def delete(self, instance=None,pk=None):
        return self.get_queryset().delete(instance,pk)

class RestManager(BaseManager):
    queryset = RestQuerySet

class PaginatedRestManager(RestManager):
    queryset = PaginatedRestQuerySet