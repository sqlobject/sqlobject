from sqlobject import *
from sqlobject.tests.dbtest import *
from test_basic import TestSO1, setupGetters

########################################
## Delete during select
########################################

def testSelect():
    setupGetters(TestSO1)
    for obj in TestSO1.select('all'):
        obj.destroySelf()
    assert list(TestSO1.select('all')) == []

########################################
## Delete without caching
########################################

class NoCache(SQLObject):
    name = StringCol()

def testDestroySelf():
    setupClass(NoCache)
    old = NoCache._connection.cache
    NoCache._connection.cache = cache.CacheSet(cache=False)
    value = NoCache(name='test')
    value.destroySelf()
    NoCache._connection.cache = old

########################################
## Delete from related joins
########################################

class Service(SQLObject):
    groups = RelatedJoin("ServiceGroup")

class ServiceGroup(SQLObject):
    services = RelatedJoin("Service")

def testDeleteRelatedJoins():
    setupClass([Service, ServiceGroup])
    service = Service()
    service_group = ServiceGroup()
    service.addServiceGroup(service_group)
    service.destroySelf()
    service_group = ServiceGroup.get(1)
    assert len(service_group.services) == 0
