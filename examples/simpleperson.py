from SQLObject import *

## Use one of these to define your connection:
"""
## Snippet "connections"
conn = MySQLConnection(user='test', db='testdb')
conn = PostgresConnection('user=test dbname=testdb')
conn = SQLiteConnect('database.db')
conn = DBMConnection('database/')
## End snippet
"""
conn = DBMConnection('database/')
conn = MySQLConnection(user='test', db='test')

## Snippet "simpleaddress-person1"
class Person(SQLObject):

    _connection = conn

    firstName = StringCol()
    middleInitial = StringCol(length=1, default=None)
    lastName = StringCol()
## end snippet

## We create a table like this: (for MySQL)
"""
## Snippet "simpleaddress-schema-person1"
CREATE TABLE person (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT,
    middle_initial CHAR(1),
    last_name TEXT
);
## end snippet
"""

def reset():
    Person.dropTable(ifExists=True)
    Person.createTable()


## Get rid of any tables we have left over...
Person.dropTable(ifExists=True)
## Now we create new tables...
## Snippet "simpleaddress-person1-create"
Person.createTable()
## End snippet

## Snippet "simpleaddress-person1-use"
p = Person.new(firstName="John", lastName="Doe")
print p
#>> <Person 1 firstName='John' middleInitial=None lastName='Doe'>
print p.firstName
#>> 'John'
p.middleInitial = 'Q'
print p.middleInitial
#>> 'Q'
p2 = Person(1)
print p2
#>> <Person 1 firstName='John' middleInitial='Q' lastName='Doe'>
print p is p2
#>> True
## End snippet

reset()
print '-'*60

conn.debug = 1
## Snippet "simpleaddress-person1-use-debug"
p = Person.new(firstName="John", lastName="Doe")
#>> QueryIns:
#   INSERT INTO person (last_name, middle_initial, first_name)
#   VALUES ('Doe', NULL, 'John')
#
#-- Not quite optimized, we don't remember the values we used to
#-- create the object, so they get re-fetched from the database:
#>> QueryOne:
#   SELECT last_name, middle_initial, first_name
#   FROM person
#   WHERE id = 1
print p
#>> <Person 1 firstName='John' middleInitial=None lastName='Doe'>
print p.firstName
#-- Now we've saved cached the column values, so we don't fetch
#-- it again.
#>> 'John'
p.middleInitial = 'Q'
#>> Query   :
#   UPDATE person
#   SET middle_initial = 'Q'
#   WHERE id = 1
print p.middleInitial
#>> 'Q'
p2 = Person(1)
#-- Again, no database access, since we're just grabbing the same
#-- instance we already had.
print p2
#>> <Person 1 firstName='John' middleInitial='Q' lastName='Doe'>
print p is p2
#>> True
## End snippet

## Snippet "simpleaddress-person1-use-set"
p.set(firstName='Bob', lastName='Dole')
## end snippet
