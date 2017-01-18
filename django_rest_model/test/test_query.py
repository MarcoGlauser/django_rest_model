from unittest import TestCase
from unittest import mock

from django_rest_model.db.models import RestModel
from django_rest_model.db.query import RestQuerySet, BaseQuerySet

base_url = 'http://test.com/'


class RestTestModel(RestModel):
    _base_url = base_url

    class Meta:
        app_label = "test"


class TestGet(TestCase):
    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_id(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestModel)
        queryset.get(id=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_pk(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestModel)
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_pk_with_filter(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestModel)
        queryset.filter(name='Test')
        queryset.get(pk=1)
        self.assertEqual(base_url + '1/?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.RestQuerySet._get_data')
    def test_only_filters(self, mock_get_data):
        mock_get_data.return_value = [1]
        queryset = RestQuerySet(model=RestTestModel)
        queryset.filter(name='Test')
        queryset.get()
        self.assertEqual(base_url + '?name=Test', queryset.url)

    @mock.patch('django_rest_model.db.query.BaseQuerySet._get_data')
    def test_multiple_objects_returned(self, mock_get_data):
        mock_get_data.return_value = [1,2]
        queryset = BaseQuerySet(model=RestTestModel)
        with self.assertRaises(RestTestModel.MultipleObjectsReturned):
            queryset.get()

    @mock.patch('django_rest_model.db.query.BaseQuerySet._get_data')
    def test_does_not_exist(self, mock_get_data):
        mock_get_data.return_value = []
        queryset = BaseQuerySet(model=RestTestModel)
        with self.assertRaises(RestTestModel.DoesNotExist):
            queryset.get()


class TestFilter(TestCase):
    def test_simple(self):
        request_url = RestQuerySet(model=RestTestModel).filter(name='test').url
        self.assertEqual(request_url,base_url + '?name=test')

    def test_chain(self):
        expected = [base_url + '?name=test&test__id=1',base_url + '?test__id=1&name=test']

        request_url = RestQuerySet(model=RestTestModel).filter(name='test', test__id=1).url
        self.assertIn(request_url,expected)

        request_url = RestQuerySet(model=RestTestModel).filter(name='test').filter(test__id=1).url
        self.assertIn(request_url,expected)