from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

########################################
## Inheritance
########################################


class Person(InheritableSQLObject):
    _inheritable = 1        # I want this class to be inherited
    firstName = StringCol()
    lastName = StringCol()

class Employee(Person):
    _inheritable = 0        # If I don't want this class to be inherited
    position = StringCol()

def setup():
    setupClass(Person)
    setupClass(Employee)

    Employee(firstName='Ian', lastName='Bicking', position='Project leader')
    Person(firstName='Daniel', lastName='Savard')


def test_inheritance():
    setup()

    persons = Person.select() # all
    for person in persons:
        assert isinstance(person, Person)
        if isinstance(person, Employee):
            assert not hasattr(person, "childName")
        else:
            assert hasattr(person, "childName")
            assert not person.childName


def test_inheritance_select():
    setup()

    persons = Person.select(Person.q.firstName <> None)
    assert persons.count() == 2

    employees = Employee.select(Employee.q.firstName <> None)
    assert employees.count() == 1

    employees = Employee.select(Employee.q.position <> None)
    assert employees.count() == 1
