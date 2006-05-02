from py.test import raises
from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

########################################
## Deep Inheritance
########################################

class DIPerson(InheritableSQLObject):
    firstName = StringCol()
    lastName = StringCol(alternateID=True, length=255)
    manager = ForeignKey("DIManager", default=None)

class DIEmployee(DIPerson):
    position = StringCol()

class DIManager(DIEmployee):
    subdudes = MultipleJoin("DIPerson", joinColumn="manager_id")

def test_creation_fail():
    """
    Try to creae an Manager without specifying a position.
    this should fail without leaving any partial records in
    the database.
    """

    setupClass(DIManager)
    setupClass(DIEmployee)
    setupClass(DIPerson)

    kwargs ={'firstName':'John', 'lastname':'Doe'}
    raises(TypeError, DIManager, **kwargs)
    #what we really need to check for is partial records in the database.
    #the following is not really adaquate.
    persons = DIEmployee.select(DIPerson.q.firstName == 'John')
    assert persons.count() == 0

def test_deep_inheritance():

    cache = getConnection().cache

    setupClass(DIManager)
    setupClass(DIEmployee)
    setupClass(DIPerson)

    manager = DIManager(firstName='Project', lastName='Manager',
        position='Project Manager')
    manager_id = manager.id
    employee_id = DIEmployee(firstName='Project', lastName='Leader',
        position='Project leader', manager=manager).id
    person_id = DIPerson(firstName='Oneof', lastName='Authors',
        manager=manager).id
    cache.clear()

    managers = list(DIManager.select())
    assert len(managers) == 1
    cache.clear()

    employees = list(DIEmployee.select())
    assert len(employees) == 2
    cache.clear()

    persons = list(DIPerson.select())
    assert len(persons) == 3
    cache.clear()

    person = DIPerson.get(employee_id)
    assert isinstance(person, DIEmployee)

    person = DIPerson.get(manager_id)
    assert isinstance(person, DIEmployee)
    assert isinstance(person, DIManager)
    cache.clear()

    person = DIEmployee.get(manager_id)
    assert isinstance(person, DIManager)
