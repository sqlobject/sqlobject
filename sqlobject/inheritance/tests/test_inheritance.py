from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

########################################
## Inheritance
########################################


class InherPerson(InheritableSQLObject):
    _inheritable = 1        # I want this class to be inherited
    firstName = StringCol()
    lastName = StringCol()

class Employee(InherPerson):
    _inheritable = 0        # If I don't want this class to be inherited
    position = StringCol()

def setup():
    setupClass(InherPerson)
    setupClass(Employee)

    Employee(firstName='Ian', lastName='Bicking', position='Project leader')
    InherPerson(firstName='Daniel', lastName='Savard')


def test_inheritance():
    setup()

    persons = InherPerson.select() # all
    for person in persons:
        assert isinstance(person, InherPerson)
        if isinstance(person, Employee):
            assert not hasattr(person, "childName")
        else:
            assert hasattr(person, "childName")
            assert not person.childName


def test_inheritance_select():
    setup()

    persons = InherPerson.select(InherPerson.q.firstName <> None)
    assert persons.count() == 2

    employees = Employee.select(Employee.q.firstName <> None)
    assert employees.count() == 1

    employees = Employee.select(Employee.q.position <> None)
    assert employees.count() == 1
