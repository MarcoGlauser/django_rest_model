from requests import Request
from requests import Session
from rest_framework.exceptions import APIException


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
        return self._create(*args, **kwargs)

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

    def delete(self, instance=None, pk=None):
        if instance:
            if not isinstance(instance,self.model):
                raise TypeError('Wrong Type passed for deleting an instance. %s was provided, %s was required' % (type(instance),self.model))
            pk = instance.pk
        else:
            if not pk:
                raise ValueError('No instance and no pk set for deletion! please set either one')
        self.filter(pk=pk)
        self._delete()

    def exists(self):
        return self.count() > 0

    def _get_filter_args(self, args, kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))
        return filter_args

    def _get_data(self):
        raise NotImplementedError

    def _create(self, *args, **kwargs):
        raise NotImplementedError

    def _delete(self):
        raise NotImplementedError

class RestQuerySet(BaseQuerySet):

    def __init__(self, *args, **kwargs):
        super(RestQuerySet, self).__init__(*args, **kwargs)
        self.identifier = None
        self.session = Session()

    @property
    def url(self):
        return self._build_request('GET').url

    #TODO Pagination
    def _get_data(self):
        if not self._cache:
            request = self._build_request('GET')
            response = self.session.send(request)
            response.raise_for_status()
            instances = self._create_model_instance(response.json())
            self._cache = instances
        return self._cache

    def _send_data(self,operation,data=None):
        pass

    def _create(self, instance = None, **kwargs):
        if instance:
            if not isinstance(instance,self.model):
                raise TypeError('Wrong Type passed for creating a new instance. %s was provided, %s was required' % (type(instance),self.model))
            data = instance.get_serializer()(instance).data
        else:
            data = kwargs

        response = self._send_data('POST',data)
        return self._create_model_instance(response)[0]

    def _delete(self):
        self._send_data('DELETE')

    def _get_detail_url(self):
        if self.identifier:
            return '%s%s/' % (self.model._base_url, self.identifier)
        raise Exception('no Identifier provided (id or pk missing in Query)')

    def _get_filter_args(self, args, kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))

        for field in self.model._meta.get_fields():
            if field.primary_key and field.attname in filter_args:
                self.identifier = filter_args[field.attname]
                filter_args.pop(field.attname)

        if 'pk' in filter_args:
            self.identifier = filter_args['pk']
            filter_args.pop('pk')

        return filter_args

    def _build_request(self, operation):
        request_url = self.model._base_url
        params = self.filter_query

        if self.identifier:
            request_url = self._get_detail_url()

        request = Request(operation, request_url, params=params, headers=None)
        return request.prepare()

    def _create_model_instance(self, data):
        new_instances = []
        if not isinstance(data, list):
            data = [data]
        for element in data:
            serializer = self.model.get_serializer()(data=element)
            if not serializer.is_valid():
                raise APIException('Invalid Response from REST Server for creating a new %s model: %s' % (repr(self.model), serializer.errors))
            new_instance = self.model(**serializer.validated_data)
            new_instance._state.adding = False
            new_instance._state.db = None
            new_instances.append(new_instance)

        return new_instances

class PaginatedRestQuerySet(RestQuerySet):
    #Todo
    def count(self):
        raise NotImplementedError

    def _get_data(self):
        raise NotImplementedError
