from sqlobject import *
from sqlobject.tests.dbtest import *

class Person(SQLObject):
    firstName = StringCol()
    lastName = StringCol()
    age = IntCol(alternateID=True)
    nameIndex = DatabaseIndex(firstName, lastName, unique=True)

def test_1():
    setupClass(Person)

    Person(firstName='Eric', lastName='Idle', age=62)
    Person(firstName='Terry', lastName='Gilliam', age=65)
    Person(firstName='John', lastName='Cleese', age=66)

    Person.get(1)
    Person.nameIndex.get('Terry', 'Gilliam')
    Person.nameIndex.get(firstName='John', lastName='Cleese')

    try:
        print Person.nameIndex.get(firstName='Graham', lastName='Chapman')
    except Exception, e:
        pass
    else:
        raise AssertError

    try:
        print Person.nameIndex.get('Terry', lastName='Gilliam')
    except Exception, e:
        pass
    else:
        raise AssertError

    try:
        print Person.nameIndex.get('Terry', 'Gilliam', 65)
    except Exception, e:
        pass
    else:
        raise AssertError

    try:
        print Person.nameIndex.get('Terry')
    except Exception, e:
        pass
    else:
        raise AssertError
