from unittest import mock

from django.db import models
from django.test import TestCase
from django_rest_model.db.models import PaginatedDRFModel
from rest_framework import serializers

base_url = 'http://test.com/'



class RestTestModel(PaginatedDRFModel):
    _base_url = base_url

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)

    @classmethod
    def get_serializer(self):
        return RestTestModelSerializer


class RestFKTestModel(PaginatedDRFModel):
    _base_url = base_url

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    fk_test = models.ForeignKey(RestTestModel)

    @classmethod
    def get_serializer(self):
        return RestTestModelSerializer


class NormalDBModel(models.Model):
    name = models.CharField(max_length=256)
    fk_test = models.ForeignKey(RestTestModel,db_constraint=False)

    class Meta:
        app_label = 'tests'


class RestFKToDBModel(PaginatedDRFModel):
    _base_url = base_url

    id = models.IntegerField(primary_key=True)
    fk_test = models.ForeignKey(NormalDBModel)

class RestTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestTestModel
        fields = ['id','name']


class RestFKTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestFKTestModel
        fields = ['id','name','fk_test']

class RestFKToDBModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestFKToDBModel
        fields = ['id','fk_test']


class TestSerializer(TestCase):
    def test_get_serializer(self):
        test = RestTestModel(name='Test')
        test.get_serializer()

class TestRestModel(TestCase):
    def test_init(self):
        RestTestModel(name='Test')

    @mock.patch('django_rest_model.db.query.RestQuerySet.create')
    def test_save(self,queryset_mock):
        rest_model_instance = RestTestModel(name="Test")
        queryset_mock.return_value = RestFKTestModel(id=1,name="Test")
        rest_model_instance.save()
        queryset_mock.assert_called_with(rest_model_instance)
        self.assertEqual(rest_model_instance.id,1)
        self.assertEqual(rest_model_instance.name, "Test")

    @mock.patch('django_rest_model.db.query.RestQuerySet.create')
    def test_create_fk(self,queryset_mock):
        rest_model_instance = RestTestModel(id=1, name="Test")
        rest_fk_model_instance = RestFKTestModel(name="TestFK", fk_test=rest_model_instance)
        saved_fk_model_instance = RestFKTestModel(id=1,name="TestFK",fk_test_id=rest_model_instance.id)
        queryset_mock.return_value = saved_fk_model_instance
        rest_fk_model_instance.save()
        self.assertEqual(rest_fk_model_instance.fk_test_id, 1)
        self.assertEqual(rest_fk_model_instance.fk_test, rest_model_instance)


    @mock.patch('django_rest_model.db.query.RestQuerySet.create')
    def test_create_fk_to_db(self,queryset_mock):
        db_model_instance = NormalDBModel(id=1, name="Test")
        rest_fk_model_instance = RestFKToDBModel(name="TestFK", fk_test=db_model_instance)
        saved_fk_model_instance = RestFKToDBModel(id=1,name="TestFK",fk_test_id=db_model_instance.id)
        queryset_mock.return_value = saved_fk_model_instance
        rest_fk_model_instance.save()
        self.assertEqual(rest_fk_model_instance.fk_test_id, 1)
        self.assertEqual(rest_fk_model_instance.fk_test, db_model_instance)

    '''
    # Not yet working. More research required
    @mock.patch('django_rest_model.db.query.RestQuerySet.create')
    def test_create_db_fk_to_rest(self,queryset_mock):
        rest_model_instance = RestTestModel(id=1, name="Test")
        db_model_instance = NormalDBModel(id=1, name="Test",fk_test=rest_model_instance)
        db_model_instance.save()
    '''

    @mock.patch('django_rest_model.db.query.RestQuerySet.delete')
    def test_delete(self,queryset_mock):
        rest_model_instance = RestTestModel(id=1, name="Test")
        rest_model_instance.delete()
        queryset_mock.assert_called_with(rest_model_instance,None)

##Bla.objects.get(pk=1) -> GET /1/ or GET http://test.com/bla/?pk=1
##asdf = Test.objects.get(1)
##Bla.objects.filter(name__contains='asdf') -> GET /?name__contains='asdf'
##Bla.objects.all() -> get /
##Bla.objects.count()

#Bla.objects.filter(test=asdf) -> GET /?test__pk=1

#print asdf.bla_set.all() -> GET /?test__pk=1

#zsdf = Bla.objects.create(name='foo',test=asdf) -> POST / { "name":"foo", "test_id":1}
#zsdf.delete() -> DELETE /pk/  or DELETE /?pk=pk

#asdf.bla_set.create(name='foo',test=asdf) -> POST / { "name":"foo", "test_id":1}


#Bla.objects.filter(name__contains='asdf').order_by('name') -> GET /?name__contains='asdf'&ordering=name
#Bla.objects.filter(name__contains='asdf').order_by('-name') -> GET /?name__contains='asdf'&ordering=-name

#Bla.objects.filter(name__contains='asdf').values()
#Bla.objects.filter(name__contains='asdf').values('id','name')
#Bla.objects.bulk_create([
    # Bla(name='test'),
    # Bla(name='another')
    # ])

