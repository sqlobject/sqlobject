from py.test import raises
from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

def first_position():
    employees = Employee.select()
    if employees.count():
        return employees[0].position
    else:
        return "Lackey"

def first_floor():
    janitors = Janitor.select()
    if janitors.count():
        return janitors[0].floor
    else:
        return 0


class InheritablePerson(InheritableSQLObject):
    firstName = StringCol()
    lastName = StringCol(alternateID=True, length=255)

class Employee(InheritablePerson):
    position = StringCol(default=first_position)

class Janitor(Employee):
    _inheritable = False
    floor = IntCol(default=first_floor)

def setup():
    setupClass(InheritablePerson)
    setupClass(Employee)
    setupClass(Janitor)

def test_liveness():

    setup()
    emp = Employee(firstName='Igor', lastName='Humpback')
    assert emp.position == "Lackey"
    emp.position = "Grunt"
    
    emp = Employee(firstName='Frank', lastName='Furter')
    assert emp.position == "Grunt"

    jan = Janitor(firstName="George", lastName="Bush")
    assert jan.floor == 0
