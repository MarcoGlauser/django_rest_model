from unittest import mock

from django.apps import apps
from django.db import models
from django.test import TestCase

from django_rest_model.db.models import PaginatedDRFModel
from rest_framework import serializers

base_url = 'http://test.com/'




class RestTestModel(PaginatedDRFModel):
    _base_url = base_url

    @classmethod
    def get_serializer(self):
        return RestTestModelSerializer

    name = models.CharField(max_length=256)

    class Meta:
        app_label = "test"
        fields = ['id','name']

class RestTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestTestModel

class TestSerializer(TestCase):
    def test_get_serializer(self):
        test = RestTestModel(name='Test')
        test.get_serializer()

'''class NormalDBModel(models.Model):
    name = models.CharField(max_length=256)
    #Test = models.ForeignKey(Bla)

    class Meta:
        app_label = 'tests'



class TestRestModel(TestCase):

    def test_init(self):
        RestTestModel(name='Test')



    def test_FK(self):
        RestTestModel(id=1)
        NormalDBModel()
        request_url = RestTestModel.objects.filter(name='test', test__id=1).url
'''

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

