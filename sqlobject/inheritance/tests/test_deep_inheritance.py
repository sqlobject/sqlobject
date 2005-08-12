from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

########################################
## Deep Inheritance
########################################


class DIPerson(InheritableSQLObject):
    firstName = StringCol()
    lastName = StringCol(alternateID=True)
    manager = ForeignKey("DIManager", default=None)

class DIEmployee(DIPerson):
    position = StringCol()

class DIManager(DIEmployee):
    subdudes = MultipleJoin("DIPerson", joinColumn="manager_id")

def test_deep_inheritance():
    setupClass(DIManager)
    setupClass(DIEmployee)
    setupClass(DIPerson)

    manager = DIManager(firstName='Project', lastName='Manager',
        position='Project Manager')
    employee = DIEmployee(firstName='Project', lastName='Leader',
        position='Project leader', manager=manager)
    person = DIPerson(firstName='Oneof', lastName='Authors', manager=manager)

    managers = list(DIManager.select())
    assert len(managers) == 1

    employees = list(DIEmployee.select())
    assert len(employees) == 2

    persons = list(DIPerson.select())
    assert len(persons) == 3
