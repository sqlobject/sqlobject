from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.inheritance import InheritableSQLObject

########################################
## Inheritance
########################################


class InherPerson(InheritableSQLObject):
    _inheritable = 1        # I want this class to be inherited
    firstName = StringCol()
    lastName = StringCol(alternateID=True)

class Employee(InherPerson):
    _inheritable = 0        # If I don't want this class to be inherited
    position = StringCol()

def setup():
    setupClass(InherPerson)
    setupClass(Employee)

    Employee(firstName='Project', lastName='Leader', position='Project leader')
    InherPerson(firstName='Oneof', lastName='Authors')


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

    persons = InherPerson.select(InherPerson.q.firstName == "phd")
    assert persons.count() == 0

    employees = Employee.select(Employee.q.firstName <> None)
    assert employees.count() == 1

    employees = Employee.select(Employee.q.firstName == "phd")
    assert employees.count() == 0

    employees = Employee.select(Employee.q.position <> None)
    assert employees.count() == 1

    persons = InherPerson.selectBy(firstName="Project")
    assert persons.count() == 1
    assert isinstance(persons[0], Employee)

    persons = Employee.selectBy(firstName="Project")
    assert persons.count() == 1

    try:
        person = InherPerson.byLastName("Oneof")
    except:
        pass
    else:
        raise RuntimeError, "unknown person %s" % person

    person = InherPerson.byLastName("Leader")
    assert person.firstName == "Project"

    person = Employee.byLastName("Leader")
    assert person.firstName == "Project"
