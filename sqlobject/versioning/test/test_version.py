from py.test import raises
from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.versioning import Versioning

from datetime import datetime


def setup():
    setupClass(MyClass)
    setupClass(Base)
    setupClass(Child)
    setupClass(Government)
    setupClass(Monarchy)
    setupClass(VChild)

class MyClass(SQLObject):
     name = StringCol()
     versions = Versioning()

class Base(InheritableSQLObject):
     name = StringCol()
     versions = Versioning()

class Child(Base):
     toy = StringCol()


class Government(InheritableSQLObject):
     name = StringCol()

class Monarchy(Government):
     monarch = StringCol()
     versions = Versioning()

class VChild(Base):
    weapon = StringCol()
    versions = Versioning()

def test_versioning():

    #the simple case
    setup()
    mc = MyClass(name='fleem')
    mc.set(name='morx')
    assert len(list(mc.versions)) == 1
    assert mc.versions[0].name == "fleem"

    assert len(list(MyClass.select())) == 1

def test_inheritable_versioning():
    setup()

    #base versioned, child unversioned
    base = Base(name='fleem')
    base.set(name='morx')
    assert len(list(base.versions)) == 1
    assert base.versions[0].name == "fleem"
    assert len(list(Base.select())) == 1

    child = Child(name='child', toy='nintendo')
    child.set(name='teenager', toy='guitar')
    assert len(list(child.versions)) == 0


    #child versioned, base unversioned
    government = Government(name='canada')
    assert not hasattr(government, 'versions')

    monarchy = Monarchy(name='UK', monarch='king george iv')
    monarchy.set(name='queen elisabeth ii')
    assert len(list(monarchy.versions)) == 1
    assert monarchy.versions[0].name == "UK"
    assert len(list(Monarchy.select())) == 1

    #both parent and child versioned
    num_base_versions = len(list(base.versions))
    vchild = VChild(name='kid', weapon='slingshot')
    vchild.set(name='toon', weapon='dynamite')
    assert len(list(base.versions)) == num_base_versions
    assert len(list(vchild.versions)) == 1

def test_restore():
    setup()
    base = Base(name='fleem')
    base.set(name='morx')
    assert base.name == "morx"
    base.versions[0].restore()
    assert base.name == "fleem"

    monarchy = Monarchy(name='USA', monarch='Emperor Norton I')
    monarchy.set(name='morx')
    assert monarchy.name == "morx"
    monarchy.versions[0].restore()
    assert monarchy.name == "USA"
    assert monarchy.monarch == "Emperor Norton I"
