#!/usr/bin/python2.2

from slides import Lecture, NumSlide, Slide, Bullet, SubBullet, PRE, URL

lecture = Lecture(
	"High-Level Database Interaction with SQLObject",

	Slide("What is SQLObject?",
		  Bullet("YAORM -- Yet Another Object-Relational Mapper"),
		  Bullet("Allows you to map your Python classes to your database schema"),
		  Bullet("Takes the 'SQL' out of 'Database Programming'"),
		  Bullet("No special XML files to create, just normal Python classes")),
	Slide("Why Do I Care?",
		  Bullet("Storing things in databases is fairly common in day-to-day programming"),
		  Bullet("SQL is the standard language used to manipulate data in a database"),
		  Bullet("Writing SQL is boring, repetitive and depressing"),
		  Bullet("SQLObject relieves you of the burden of writing SQL"),
		  Bullet("...but still lets you write SQL when you need to")),
	Slide("How does SQLObject differ from other ORM's?",
		  Bullet("Simple is better than complex; SQLObject is very simple to use"),
		  Bullet("Mappings are defined using normal Python classes"),
		  Bullet("Uses properties instead of wordy get/set methods for column attributes"),
		  Bullet("No awkward auto-generation of Python classes/files from an external format"),
		  Bullet("Can generate the database schema directly from your Python classes, and vice versa"),
		  Bullet("Overloading magic provides convenient high-level SQL conditionals (dot q magic, stay tuned)")),
	Slide("A Simple Example",
		  Bullet("To create a table that looks like this in SQL:",
				 PRE("""\
CREATE TABLE person (
    id SERIAL,
    first_name VARCHAR(100) NOT NULL,
    middle_initial CHAR(1),
    last_name VARCHAR(150) NOT NULL
);""")),
		  Bullet("You would write this Python code:",
				 PRE("""\
class Person(SQLObject):
    firstName = StringCol(length = 100)
    middleInitial = StringCol(length = 1)
    lastName = StringCol(length = 150)""")),
		  Bullet("No, you're not dreaming :P")),
	Slide("Declaring the Class",
		  PRE("""\
from SQLObject import *

conn = PostgresConnection(db = 'testdb', user = 'testuser', passwd = 'testpass')

class Person(SQLObject):
    _connection = conn
	
    firstName = StringCol(length = 100)
    middleInitial = StringCol(length = 1)
    lastName = StringCol(length = 150)"""),
		  Bullet("Use one of MySQLConnection, PostgresConnection, SQLiteConnection or DBMConnection as your _connection"),

		  Bullet("Use StudlyCaps for your classes and mixedCase for your columns"),
		  Bullet("SQLObject will map TableName to table_name and columnName to column_name"),
	      Bullet("In the above example, class Person becomes table person with columns first_name, middle_initial and last_name")),
	Slide("Creating and Dropping Tables",
		  Bullet("Use the createTable class method to create the table, and two optional keyword arguments",SubBullet(
	Bullet("ifNotExists: only try to create the table if it doesn't exist"),
	Bullet("createJoinTables: will create the intermediate tables for many-to-many relationships"))),
		  Bullet("Conversely, use dropTable, passing in optional ifExists and dropJoinTables keyword arguments")),

	Slide("More on Column Syntax",
		  Bullet("Columns are implemented as properties"),
		  Bullet("Columns supported: StringCol, IntCol, FloatCol, EnumCol, DateTimeCol, ForeignKey, DecimalCol, CurrencyCol"),
		  Bullet("The first argument is the column name"),
		  Bullet("Keyword arguments specify additional information (e.g. notNone, default, length, etc)"),
		  Bullet("SQLObject lets the database do type checking and coercion"),
		  Bullet("An id column is implicitly created")),
	Slide("Keyword Arguments for Col Classes",
		  Bullet("dbName: the column name in the database"),
		  Bullet("default: the default value (can be a callable that returns a value)"),
		  Bullet("alternateID: set this to True if you want a byColumnName method to lookup rows based on this column"),
		  Bullet("unique: declare this column as UNIQUE in the database"),
		  Bullet("notNone: when True, column cannot be None/NULL"),
		  Bullet("sqlType: to specify the column type manually")),
	Slide("Special Class Attributes",
		  Bullet("_connection: the database connection for this class"),
		  Bullet("_table: the database name of the table behind this class"),
		  Bullet("_joins: a list of join relationships to other classes"),
		  Bullet("_cacheValues: you'll want to set this false if you're using SQLObject classes from multiple processes"),
		  Bullet("_idName: the name of the PK (defaults to id)"),
		  Bullet("_style: a style object that provides a custom Python to DB name mapping algorithm")),
	Slide("Using SQLObject classes",
		  Bullet("Create a new row with the .new() class method:",
				 PRE("""Person.new(firstName = "Brad", middleInitial = "E", lastName = "Bollenbach")""")),
		  Bullet("The row is inserted into the database as soon as you call .new()"),
		  Bullet("Access an existing row by passing an ID to the class constructor",
				 PRE("""\
>>> me = Person(1)
>>> me.firstName
'Brad'
>>> me.lastName
'Bollenbach'""")),
		  Bullet("Modify column values by modifying property values"),
		  Bullet("Changes to your object's properties are updated immediately in the database"),
		  Bullet("...but transactions are there if you need them (as long as the database supports them)")),
	Slide("Relating Your Classes with Joins",
		  Bullet("Use a ForeignKey to point a column's value at an instance of another class"),
		  Bullet("To relate the PK class back to the FK class, use MultipleJoin"),
		  Bullet("Let's give a Person some PhoneNumbers:",
				 PRE("""\
from SQLObject import *
conn = PostgresConnection(db = 'testdb', user = 'testuser', passwd = 'testpass')

class Person(SQLObject):
    _connection = conn
    
    firstName = StringCol(length = 100)
    middleInitial = StringCol(length = 1)
    lastName = StringCol(length = 150)
    phoneNumbers = MultipleJoin("PhoneNumber") 

class PhoneNumber(SQLObject):
    _connection = conn

    person = ForeignKey('Person')
    phoneNumber = StringCol(length = 10)"""))),
	Slide("Many-to-Many Relationships",
		  Bullet("A Person might have many Roles"),
		  Bullet("A Role might be associated to more than one Person"),
		  Bullet("Use a RelatedJoin to specify this many-to-many relation:",
				 PRE("""\
class Role(SQLObject):
    _connection = conn

    name = StringCol(length = 20)
    people = RelatedJoin('Person')

class Person(SQLObject):
    _connection = conn

    firstName = StringCol(length = 100)
    middleInitial = StringCol(length = 1)
    lastName = StringCol(length = 150)
    phoneNumbers = MultipleJoin("PhoneNumber")

    roles = RelatedJoin('Role')
	
me = Person.new(firstName = "Brad", middleInitial = "E", lastName = "Bollenbach")
pg = Role.new(name = "Python Geek")
me.addRole(pg)
""")),
		  Bullet("SQLObject added .addRole() and .removeRole() methods to Person, and .addPerson() and .removePerson() methods to Role"),
		  Bullet("...and created the person_role table by combining the table names of the classes alphabetically")),
	Slide("Selecting Multiple Objects",
		  Bullet("The class's .select() method can be used to return multiple objects of a given class"),
		  Bullet("Here comes that dot q magic!"),
		  Bullet("Every SQLObject derived class has a special .q attribute, which uses some funky operator overloading to construct queries using Python:",
				 PRE("""\
>>> from person import Person
>>> brads = Person.select(Person.q.firstName == 'Brad')
>>> list(brads)
[<Person 1 lastName='Bollenbach' middleInitial='E' firstName='Brad'>]
>>> brads[0].lastName
'Bollenbach'
""")),
		  Bullet("select accepts orderBy and groupBy arguments, which are strings (or lists of strings) referring to the database column name")),
	Slide("Selects using AND",
		  Bullet("Use the AND function for more specific queries:",
				 PRE("""\
>>> from SQLObject import AND
>>> from person import Person
>>> bradbs = Person.select(AND(
...     Person.q.firstName == "Brad",
...     Person.q.lastName.startswith("B")
... ))
""")),
		  Bullet("Notice that columns-as-properties behave much like their regular Python brethren (e.g. the startswith method used above)")),
	Slide("Customizing Column Behaviour",
		  Bullet("SQLObject uses metaclasses to generate the classes that map to your database tables"),
		  Bullet("Because of this, you need to take care when overriding property get/set methods"),
		  Bullet("You cannot simply override the get or set method and then call the parent's get/set"),
		  Bullet("Your class was created on-the-fly by SQLObject, so there is no parent! :)"),
		  Bullet("SQLObject gives you special _SO_set_foo and _SO_get_foo methods to call after you've done something special in the normal setter/getter"),
		  Bullet("An (admittedly contrived) example:",
				 PRE("""\
class Person(SQLObject):
    ...
    def _set_lastName(self, value):
        print "you changed the lastName"
        self._SO_set_lastName(value)
"""))),
	Slide("Better Living Through Transactions",
		  Bullet("Sometimes you need indivisibility"),
		  Bullet("SQLObject lets you use transactions when the database supports it",
				 PRE("""\
trans = Person._connection.transaction()
me = Person(1, trans)
me.firstName = "Bradley"
trans.commit()
me.firstName = "Yada"
trans.rollback()"""))),
	Slide("Automatic Class Generation",
		  Bullet("Laziness is a virtue"),
		  Bullet("If you've already got a database schema, why not make SQLObject create the classes for you?",
				 PRE("""\
class Person(SQLObject):

    _fromDatabase = True""")),
		  Bullet("You can still specify additional columns, as normal"),
		  Bullet("Currently this only works with MySQL")),
	Slide("SQLObject in the Wild -- Who's Using It?",
		  Bullet("BBnet.ca used SQLObject to develop a time tracking and invoicing system for a consultancy firm"),
		  Bullet("XSOLI (my current employer) is using SQLObject to drive an online merchant proxy system"),
		  Bullet("Future projects will probably include porting a sales application for a fixed-rate long distance provider onto the SQLObject framework"),
		  Bullet("There's an active community of SQLObject developers on the mailing list")),
	Slide("Future Plans for SQLObject",
		  Bullet("Add support for more databases"),
		  Bullet("Improved transaction handling, so that even non-transaction aware backends can support them"),
		  Bullet("Hooks into a validation and form generation package"),
		  Bullet("More powerful joins")),
	Slide("Summing Up",
		  Bullet("SQLObject is a framework that can make your (programming) life easier"),
		  Bullet("It provides a high-level Python interface to things you'd normally suffer through in SQL"),
		  Bullet("It offers advanced features like automatic class generation, dot q magic, and various ways of relating your classes"),
		  Bullet("There's an active developer base, so you're sure to find help when you need it")),
	Slide("Resources",
		  Bullet("SQLObject homepage -- ", URL("http://www.sqlobject.org")),
		  Bullet("Join the mailing list -- ", URL("http://lists.sourceforge.net/lists/listinfo/sqlobject-discuss")),
		  Bullet("Contact me -- brad@bbnet.ca")),
	Slide("Questions?",
		  Bullet("Questions?"),
		  Bullet("Comments?"),
		  Bullet("Free beer?")))

lecture.renderHTML(".", "slide-%02d.html", css="main.css")
