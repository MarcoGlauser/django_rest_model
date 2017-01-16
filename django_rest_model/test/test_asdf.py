from django.db import models
from django.test import TestCase

from django_rest_model.db.managers import RestManager
from django_rest_model.db.models import PaginatedDRFModel, RestModel


class Bla(PaginatedDRFModel):
    _base_url = 'http://test.com/'

    id = models.IntegerField()
    name = models.CharField(max_length=256)

    class Meta:
        app_label = "test"
        fields = ['id','name']

class NormalDBModel(models.Model):
    name = models.CharField(max_length=256)
    Test = models.ForeignKey(Bla)

    class Meta:
        app_label = 'tests'




class TestFilter(TestCase):
    def test_simple(self):
        request_url = Bla.objects.filter(name='test').url
        self.assertEqual(request_url,'http://test.com/?name=test')

    def test_chain(self):
        request_url = Bla.objects.filter(name='test',test__id=1).url
        self.assertIn(request_url,['http://test.com/?name=test&test__id=1','http://test.com/?test__id=1&name=test'])

    def test_FK(self):
        Bla(id=1)
        NormalDBModel()
        request_url = Bla.objects.filter(name='test', test__id=1).url

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

#Bla.objects..filter(name__contains='asdf').values()
#Bla.objects..filter(name__contains='asdf').values('id','name')
#Bla.objects.bulk_create([
    # Bla(name='test'),
    # Bla(name='another')
    # ])

#Bla.objects.count()