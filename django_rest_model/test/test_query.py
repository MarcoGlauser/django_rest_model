from unittest import TestCase
from unittest import mock

import requests
from django.db import models
from django_rest_model.db.models import  RestModel
from django_rest_model.db.query import RestQuerySet, BaseQuerySet
from rest_framework import serializers
from rest_framework.exceptions import APIException

base_url = 'http://test.com/'



class RestTestQueryModel(RestModel):
    _base_url = base_url

    name = models.CharField(max_length=1234)
    id = models.IntegerField(primary_key=True)

    @classmethod
    def get_serializer(self):
        return RestTestModelSerializer


class RestTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestTestQueryModel
        fields = ['id','name']

class RestTestAlternatePKModel(RestModel):
    _base_url = base_url

    name = models.CharField(max_length=1234)
    other_identifier = models.IntegerField(primary_key=True)


class TestGet(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_id(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.get(id=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_pk(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_other_pk(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestAlternatePKModel)
        queryset.get(other_identifier=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_pk_with_filter(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.filter(name='Test')
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_only_filters(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.filter(name='Test')
        queryset.get()
        self.assertEqual(base_url + '?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.BaseQuerySet._get_data')
    def test_multiple_objects_returned(self, mock_get_data):
        mock_get_data.return_value = [1,2]
        queryset = BaseQuerySet(model=RestTestQueryModel)
        with self.assertRaises(RestTestQueryModel.MultipleObjectsReturned):
            queryset.get()

    @mock.patch('django_rest_model.db.query.BaseQuerySet._get_data')
    def test_does_not_exist(self, mock_get_data):
        mock_get_data.return_value = []
        queryset = BaseQuerySet(model=RestTestQueryModel)
        with self.assertRaises(RestTestQueryModel.DoesNotExist):
            queryset.get()


class TestFilter(TestCase):
    def test_simple(self):
        request_url = RestQuerySet(model=RestTestQueryModel).filter(name='test').url
        self.assertEqual(request_url,base_url + '?name=test')

    def test_chain(self):
        expected = [base_url + '?name=test&test__id=1',base_url + '?test__id=1&name=test']

        request_url = RestQuerySet(model=RestTestQueryModel).filter(name='test', test__id=1).url
        self.assertIn(request_url,expected)

        request_url = RestQuerySet(model=RestTestQueryModel).filter(name='test').filter(test__id=1).url
        self.assertIn(request_url,expected)


class TestAll(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_simple(self, mock_get_data):
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.all()
        self.assertEqual(base_url , queryset.url)


class TestCount(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_simple(self, mock_get_data):
        mock_get_data.return_value = [1, 2]
        queryset = RestQuerySet(model=RestTestQueryModel)
        self.assertEqual(2 , queryset.count())


class TestCreate(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_simple(self, mock_send_data):
        mock_send_data.return_value = {'id':1,'name':'asdf'}
        queryset = RestQuerySet(model=RestTestQueryModel)
        new_instance = queryset.create(id=1,name="Test")
        self.assertEqual(new_instance.id,mock_send_data.return_value['id'])
        self.assertEqual(new_instance.name, mock_send_data.return_value['name'])

    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_invalid_return(self, mock_send_data):
        mock_send_data.return_value = {'name': 'asdf'}
        queryset = RestQuerySet(model=RestTestQueryModel)
        with self.assertRaises(APIException):
            queryset.create(id=1, name="Test")

    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_creation_from_instance(self, mock_send_data):
        name = 'test'
        mock_send_data.return_value = {'id': 1, 'name': name}
        instance = RestTestQueryModel(name=name)
        queryset = RestQuerySet(model=RestTestQueryModel)
        new_instance = queryset.create(instance)
        mock_send_data.assert_called_with('POST',{'id': None, 'name':name})
        self.assertEqual(new_instance.id,mock_send_data.return_value['id'])
        self.assertEqual(new_instance.name, mock_send_data.return_value['name'])

class TestDelete(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_pk(self, mock_send_data):
        mock_send_data.return_value = None
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.delete(pk=1)
        mock_send_data.assert_called_with('DELETE')
        self.assertEqual(queryset.identifier,1)

    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_instance(self, mock_send_data):
        instance = RestTestQueryModel(id=1,name="Test")
        mock_send_data.return_value = None
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.delete(instance)
        mock_send_data.assert_called_with('DELETE')
        self.assertEqual(queryset.identifier,1)

    @mock.patch('django_rest_model.db.query.RestQuerySet._send_data')
    def test_nothing(self, mock_send_data):
        mock_send_data.return_value = None
        queryset = RestQuerySet(model=RestTestQueryModel)
        with self.assertRaises(ValueError):
            queryset.delete()


class TestGetData(TestCase):
    @mock.patch('requests.sessions.Session.send')
    @mock.patch('requests.Response.json')
    def test_get(self, response_json_mock, session_mock):
        response = requests.Response()
        response.status_code = 200
        session_mock.return_value=response
        response_json_mock.return_value = {'name': 'Test', 'id':1}
        queryset = RestQuerySet(model=RestTestQueryModel)
        queryset.identifier = 1
        single_instance = queryset._get_data()
        self.assertIsInstance(single_instance[0],RestTestQueryModel)

    @mock.patch('requests.sessions.Session.send')
    @mock.patch('requests.Response.json')
    def test_list(self, response_json_mock, session_mock):
        response = requests.Response()
        response.status_code = 200
        session_mock.return_value=response
        response_json_mock.return_value = [{'name': 'Test', 'id': 1},{'name': 'Test', 'id': 2}]
        queryset = RestQuerySet(model=RestTestQueryModel)
        multiple_instances = queryset._get_data()
        self.assertIsInstance(multiple_instances[0], RestTestQueryModel)
        self.assertIsInstance(multiple_instances[1], RestTestQueryModel)
        self.assertEqual(multiple_instances[0].id,1)
        self.assertEqual(multiple_instances[1].id,2)
