#!/usr/bin/env python
from sqlobject import *
import os

from setup import *
__connection__ = conn

############################################################
## Define classes:
############################################################

class Person(SQLObject):

    _columns = [StringCol('username', length=20, alternateID=True,
                          notNull=1),
                StringCol('firstName', length=30,
                          notNull=1),
                StringCol('middleInitial', length=1, default=None),
                StringCol('lastName', length=50, notNull=1)]
    _joins = [RelatedJoin('Role'), MultipleJoin('PhoneNumber')]

    def imageFilename(self):
        return 'images/person-%s.jpg' % self.id

    def _get_image(self):
        if not os.path.exists(self.imageFilename()):
            return None
        f = open(self.imageFilename())
        v = f.read()
        f.close()
        return v

    def _set_image(self, value):
        # assume we get a string for the image
        f = open(self.imageFilename(), 'w')
        f.write(value)
        f.close()

    def _del_image(self, value):
        # I usually wouldn't include a method like this, but for
        # instructional purposes...
        os.unlink(self.imageFilename())

    _doc_image = 'The headshot for the person'

class PhoneNumber(SQLObject):

    _columns = [KeyCol('personID', foreignKey='Person'),
                StringCol('phoneNumber', length=14, notNull=1),
                EnumCol('phoneType',
                        enumValues=['home', 'work', 'mobile'], notNull=1)]

class Role(SQLObject):

    _columns = [StringCol('name', length=30)]
    _joins = [RelatedJoin('Person')]


tableClasses = [Person, PhoneNumber, Role]

############################################################
## Process command-line arguments:
############################################################

import sys
args = sys.argv[1:]

if 'drop' in args:
    for table in tableClasses:
        table.dropTable(ifExists=True)

if 'create' in args:
    for table in tableClasses:
        table.createTable(ifNotExists=True)

if 'clear' in args:
    for table in tableClasses:
        table.clearTable(ifExists=True)


############################################################
## Define tests:
############################################################

test1 = """
>>> p = Person(firstName="John", lastName="Doe", username="johnd")
>>> print p
<Person 1 firstName='John' middleInitial=None lastName='Doe'>
>>> print p.firstName
John
>>> p.middleInitial = 'Q'
>>> print p.middleInitial
Q
>>> p2 = Person.get(p.id)
>>> print p2
<Person 1 firstName='John' middleInitial='Q' lastName='Doe'>
>>> print p is p2
1
>>> p3 = Person.byUsername("johnd")
>>> print p3
<Person 1 firstName='John' middleInitial='Q' lastName='Doe'>
"""

test2 = """
>>> r = Role(name="editor")
>>> p = list(Person.select('all'))[-1]
>>> p.addRole(r)
>>> print p.roles
[<Role 1 name='editor'>]
>>> print r.persons
[<Person 1 firstName='John' middleInitial='Q' lastName='Doe'>]
>>> r.removePerson(p)
>>> print p.roles
[]
>>> phone = PhoneNumber(person=p, phoneNumber='773-555-1023', phoneType='home')
>>> print p.phoneNumbers
"""

test3 = """
>>> peeps1 = Person.select(Person.q.firstName=="John")
>>> print [p.id for p in peeps1]
>>> peeps2 = Person.select(AND(PhoneNumber.q.personID == Person.q.id, PhoneNumber.q.phoneNumber.startswith('612')))
>>> print [p.id for p in peeps2]
>>> peeps3 = Person.select("phone_number.id = person.id AND phone_number.phone_number LIKE '773%'", clauseTables=['phone_number'])[2:5]
>>> print [p.id for p in peeps3]
"""


############################################################
## Run tests:
############################################################

def runTest(s):
    lines = s.split('\n')
    for line in lines:
        if line.startswith('>>> '):
            print line
            exec line[4:]

runTest(test1)
runTest(test2)
runTest(test3)
