from sqlobject import *
from config import conn

__connection__ = conn

## Snippet "address-person"
class Person(SQLObject):

    firstName = StringCol()
    middleInitial = StringCol(length=1, default=None)
    lastName = StringCol()

    addresses = MultipleJoin('Address')
## end snippet

## Snippet "address-address"
class Address(SQLObject):

    street = StringCol()
    city = StringCol()
    state = StringCol(length=2)
    zip = StringCol(length=9)
    person = ForeignKey('Person')
## end snippet

def reset():
    Person.dropTable(ifExists=True)
    Person.createTable()
    Address.dropTable(ifExists=True)
    Address.createTable()

reset()

## Snippet "address-use1"
p = Person(firstName='John', lastName='Doe')
print p.addresses
#>> []
a1 = Address(street='123', city='Smallsville',
                 state='IL', zip='50484', person=p)
print [a.street for a in p.addresses]
#>> ['123']
## end snippet

# We'll add some more data to make the results more interesting:
add1 = Person(firstName='Jane', lastName='Doe')
add2 = Person(firstName='Tom', lastName='Brown')
Address(street='5839', city='Eckersville',
            state='IL', zip='50482', person=add1)
Address(street='4', city='Whinging',
            state='AZ', zip='49378', person=add2)

## Snippet "person-select1"
peeps = Person.select(Person.q.firstName=="John")
print list(peeps)
#>> [<Person 1 lastName='Doe' middleInitial=None firstName='John'>]
#        SELECT person.id FROM person WHERE person.first_name = 'John';
## end snippet

## Snippet "person-select-by"
peeps = Person.selectBy(firstName="John", lastName="Doe")
## end snippet
list(peeps)

## Snippet "person-select2"
peeps = Person.select(
            AND(Address.q.personID == Person.q.id,
                Address.q.zip.startswith('504')))
print list(peeps)
#        SELECT person.id FROM person, address
#        WHERE (address.person_id = person.id AND
#               address.zip LIKE '612%');
## end snippet

## Snippet "person-select3"
peeps = Person.select("""address.id = person.id AND
                         address.zip LIKE '504%'""",
                      clauseTables=['address'])
## end snippet
list(peeps)
