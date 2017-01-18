from django_rest_model.db import helpers
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

    def create(self, *args, **kwargs):
        self._create(*args, **kwargs)

    def filter(self, *args, **kwargs):
        existing_query_copy = dict(self.filter_query)
        existing_query_copy.update(self._get_filter_args(args, kwargs))
        self.filter_query = existing_query_copy
        return self

    def get(self, *args, **kwargs):
        self.filter(*args,**kwargs)

        result = self._get_data()
        number_of_results = len(result)
        if number_of_results == 1:
            return result[0]
        if not number_of_results:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." %
                type(self.model)
            )
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s!" %
            (type(self.model), number_of_results)
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

    def _create(self, *args, **kwargs):
        raise NotImplementedError

class RestQuerySet(BaseQuerySet):

    def __init__(self, *args, **kwargs):
        super(RestQuerySet, self).__init__(*args, **kwargs)
        self.identifier = None

    def _get_data(self):
        if not self._cache:
            if ['id'] in self.filter_query:
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

    def _create(self, instance = None, **kwargs):

        # todo maybe refactor serializer/get_serializer
        #instance passed
        if instance:
            if not isinstance(instance,type(self.model)):
                raise TypeError('Wrong Type passed for creating a new instance. %s was provided, %s was required' % (type(instance),type(self.model)))
            data = instance.get_serializer().data
        else:
            data = kwargs

        response = self._send_data('POST',data)
        serializer = self.model.get_serializer()(data=response)
        if not serializer.is_valid():
            raise Exception('Invalid deserialization for %s model: %s' % (type(self.model), serializer.errors))
        new_instance = helpers.create_instance(self.model.__class__,serializer.validated_data)
        return new_instance

    def _send_data(self,operation,data):
        pass



    def _get_detail_url(self):
        if self.identifier:
            return '%s%s/' % (self.model._base_url, self.identifier)
        raise Exception('no Identifier provided (id or pk missing in Query)')

    def _get_filter_args(self, args, kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))

        if 'id' in filter_args:
            self.identifier = filter_args['id']
            filter_args.pop('id')
        if 'pk' in filter_args:
            self.identifier = filter_args['pk']
            filter_args.pop('pk')

        return filter_args

    @property
    def url(self):
        return self._build_request('GET').url

    def _build_request(self, operation):
        request_url = self.model._base_url
        params = self.filter_query

        if self.identifier:
            request_url = self._get_detail_url()

        request = Request(operation, request_url, params=params, headers=None)
        return request.prepare()

class PaginatedRestQuerySet(RestQuerySet):
    #Todo
    def count(self):
        raise NotImplementedError

    def _get_data(self):
        raise NotImplementedError
