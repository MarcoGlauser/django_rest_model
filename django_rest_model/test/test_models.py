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


class RestTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestTestModel
        fields = ['id','name']

class RestFKTestModel(PaginatedDRFModel):
    _base_url = base_url

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    fk_test = models.ForeignKey(RestTestModel)

    @classmethod
    def get_serializer(self):
        return RestTestModelSerializer

class RestFKTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestFKTestModel
        fields = ['id','name','fk_test']

'''
class NormalDBModel(models.Model):
    name = models.CharField(max_length=256)
    #fk_test = models.ForeignKey(RestTestModel)

    class Meta:
        app_label = 'tests'
'''

class TestSerializer(TestCase):
    def test_get_serializer(self):
        test = RestTestModel(name='Test')
        test.get_serializer()

class TestRestModel(TestCase):
    def test_init(self):
        RestTestModel(name='Test')

    @mock.patch('django_rest_model.db.query.RestQuerySet.create')
    def test_create_FK(self,queryset_mock):
        rest_model_instance = RestTestModel(id=1, name="Test")
        rest_fk_model_instance = RestFKTestModel(name="TestFK", fk_test=rest_model_instance)
        saved_fk_model_instance = RestFKTestModel(id=1,name="TestFK",fk_test=rest_model_instance)
        queryset_mock.return_value = saved_fk_model_instance
        rest_fk_model_instance.save()
        queryset_mock.assert_called_with(rest_fk_model_instance)
        self.assertEqual(rest_fk_model_instance.id,1)
        self.assertEqual(rest_fk_model_instance.fk_test_id, 1)
        self.assertEqual(rest_fk_model_instance.name, "TestFK")


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

