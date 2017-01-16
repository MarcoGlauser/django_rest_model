from requests import Request


class RestQuery:
    select_related = False
    order_by = tuple()


class BaseQuerySet:
    def using(self, db):
        return self

    def __init__(self, *args, **kwargs):
        self._cache = None
        self.ordered = True
        self.model = kwargs.pop('model')
        self.filter_query = kwargs.pop('filter_query', {})
        self.query = RestQuery()

    def order_by(self, *args, **kwargs):
        return self

    def none(self, *args, **kwargs):
        cloned_query = self._clone()
        cloned_query.filter_query = {}
        return cloned_query

    def _clone(self, *args, **kwargs):
        return self.__class__(
            model=self.model,
            filter_query=self.filter_query
        )

    def count(self):
        return len(self._get_data())

    def __getitem__(self, k):
        return self._get_data()[k]


    def __iter__(self):
        return iter(self._get_data())

    def all(self):
        return self._get_data()

    def __len__(self):
        return self.count()

    def filter(self, *args, **kwargs):
        self.filter_query = self._get_filter_args(args, kwargs)
        return self

    def get(self, *args, **kwargs):
        result = self._get_data()
        number_of_results = len(result)
        if number_of_results == 1:
            return result[0]
        if not number_of_results:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." %
                self.model._meta.object_name
            )
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s!" %
            (self.model._meta.object_name, number_of_results)
        )

    def _set_model_attrs(self, instance):
        instance._meta = self.model._meta
        instance._state = self.model._state
        return instance

    def _get_filter_args(self, args, kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))
        return filter_args

    def _get_data(self):
        raise NotImplementedError

    def _create(self, instance):
        raise NotImplementedError


class RestQuerySet(BaseQuerySet):
    def _get_data(self):
        if not self._cache:
            if 'id' in self.filter_query:
                #thread = self.mailer.get_thread_by_id(self.credentials,
                #                                      self.filter_query['id'],
                #                                      cls=self.model)
                #self._cache = [self._set_model_attrs(thread)]
                self._cache= self.filter_query
            else:
                #to = (self.filter_query['to__icontains']
                #      if 'to__icontains' in self.filter_query
                #      else None)
                #all_threads = self.mailer.get_all_threads(self.credentials,
                #                                          to=to, cls=self.model)
                #self._cache = map(self._set_model_attrs, all_threads)
                self._cache = self.filter_query
        return self._cache

    def _create(self, instance):
        pass

    @property
    def url(self):
        request = Request('GET', self.model._base_url, params=self.filter_query, headers=None)
        return request.prepare().url