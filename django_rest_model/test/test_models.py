from unittest import mock

from django.db import models
from django.test import TestCase

from django_rest_model.db.models import PaginatedDRFModel

base_url = 'http://test.com/'

class RestTestModel(PaginatedDRFModel):
    _base_url = base_url

    id = models.IntegerField()
    name = models.CharField(max_length=256)

    class Meta:
        app_label = "test"
        fields = ['id','name']


'''class NormalDBModel(models.Model):
    name = models.CharField(max_length=256)
    #Test = models.ForeignKey(Bla)

    class Meta:
        app_label = 'tests'
'''

class TestGet(TestCase):

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_id(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestTestModel.objects.get_queryset()
        queryset.get(id=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_pk(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestTestModel.objects.get_queryset()
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_pk_with_filter(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestTestModel.objects.get_queryset()
        queryset.filter(name='Test')
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_only_filters(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestTestModel.objects.get_queryset()
        queryset.filter(name='Test')
        queryset.get()
        self.assertEqual(base_url + '?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_multiple_objects_returned(self, mock_get_data):
        mock_get_data.return_value = [1,2]
        queryset = RestTestModel.objects.get_queryset()
        with self.assertRaises(RestTestModel.MultipleObjectsReturned):
            queryset.get()

    @mock.patch('django_rest_model.db.query.PaginatedRestQuerySet._get_data')
    def test_does_not_exist(self, mock_get_data):
        mock_get_data.return_value = []
        queryset = RestTestModel.objects.get_queryset()
        with self.assertRaises(RestTestModel.DoesNotExist):
            queryset.get()


class TestFilter(TestCase):

    def test_simple(self):
        request_url = RestTestModel.objects.filter(name='test').url
        self.assertEqual(request_url,base_url + '?name=test')

    def test_chain(self):
        expected = [base_url + '?name=test&test__id=1',base_url + '?test__id=1&name=test']

        request_url = RestTestModel.objects.filter(name='test', test__id=1).url
        self.assertIn(request_url,expected)

        request_url = RestTestModel.objects.filter(name='test').filter(test__id=1).url
        self.assertIn(request_url,expected)


'''    def test_FK(self):
        Bla(id=1)
        NormalDBModel()
        request_url = Bla.objects.filter(name='test', test__id=1).url
'''

#Bla.objects.get(pk=1) -> GET /1/ or GET http://test.com/bla/?pk=1
#Bla.objects.filter(name__contains='asdf') -> GET /?name__contains='asdf'

#asdf = Test.objects.get(1)
#Bla.objects.filter(test=asdf) -> GET /?test__pk=1

#print asdf.bla_set.all() -> GET /?test__pk=1

#zsdf = Bla.objects.create(name='foo',test=asdf) -> POST / { "name":"foo", "test_id":1}
#zsdf.delete() -> DELETE /pk/  or DELETE /?pk=pk

#asdf.bla_set.create(name='foo',test=asdf) -> POST / { "name":"foo", "test_id":1}

#Bla.objects.all() -> get /

#Bla.objects.filter(name__contains='asdf') -> GET /?name__contains='asdf'&ordering=name
#Bla.objects.filter(name__contains='asdf') -> GET /?name__contains='asdf'&ordering=-name

#Bla.objects.filter(name__contains='asdf').values()
#Bla.objects.filter(name__contains='asdf').values('id','name')
#Bla.objects.bulk_create([
    # Bla(name='test'),
    # Bla(name='another')
    # ])

#Bla.objects.count()