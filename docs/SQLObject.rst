`````````
SQLObject
`````````

.. contents:: Contents:

Credits
=======

SQLObject is by Ian Bicking (ianb@colorstudy.com) and `Contributors
<Authors.html>`_.  The website is `sqlobject.org
<http://sqlobject.org>`_.

License
=======

The code is licensed under the `Lesser General Public License`_
(LGPL).

.. _`Lesser General Public License`: https://www.gnu.org/copyleft/lesser.html

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

Introduction
============

SQLObject is an *object-relational mapper* for Python_ programming
language.  It allows you to translate RDBMS table rows into Python objects,
and manipulate those objects to transparently manipulate the database.

.. _Python: https://www.python.org/

In using SQLObject, you will create a class definition that will
describe how the object translates to the database table.  SQLObject
will produce the code to access the database, and update the database
with your changes.  The generated interface looks similar to any other
interface, and callers need not be aware of the database backend.

SQLObject also includes a novel feature to avoid generating,
textually, your SQL queries.  This also allows non-SQL databases to be
used with the same query syntax.

Requirements
============

Currently SQLObject supports MySQL_ and MariaDB_ via MySQLdb_ aka
MySQL-python (called mysqlclient_ for Python 3), `MySQL Connector`_,
PyMySQL_, `mariadb connector`_, PyODBC_ and PyPyODBC_. For
PostgreSQL_ psycopg_ and psycopg2_ are recommended, especially their
precompiled wheels psycopg-binary_ and psycopg2-binary_; see also optimized
psycopg-c_; PyGreSQL_ and pg8000_ are supported; SQLite_
has a built-in driver. Firebird_ is supported via fdb_ or kinterbasdb_;
pyfirebirdsql_ is supported but has problems. `MAX DB`_ (also known as SAP
DB) is supported via sapdb_. Sybase via Sybase_. `MSSQL Server`_ via
pymssql_ (+ FreeTDS_) or adodbapi_ (Win32). PyODBC_ and PyPyODBC_ are
supported for MySQL, PostgreSQL and MSSQL but have problems (not all tests
passed).

.. _MySQL: https://www.mysql.com/
.. _MariaDB: https://mariadb.org/
.. _MySQLdb: https://sourceforge.net/projects/mysql-python/
.. _mysqlclient: https://pypi.org/project/mysqlclient/
.. _`MySQL Connector`: https://pypi.org/project/mysql-connector/
.. _PyMySQL: https://pypi.org/project/PyMySQL/
.. _mariadb connector: https://pypi.org/project/mariadb/
.. _PostgreSQL: https://postgresql.org
.. _psycopg: https://pypi.org/project/psycopg/
.. _psycopg-binary: https://pypi.org/project/psycopg-binary/
.. _psycopg-c: https://pypi.org/project/psycopg-c/
.. _psycopg2: https://www.psycopg.org/
.. _psycopg2-binary: https://pypi.org/project/psycopg2-binary/
.. _PyGreSQL: http://www.pygresql.org/
.. _pg8000: https://pypi.org/project/pg8000/
.. _SQLite: https://sqlite.org/
.. _Firebird: http://www.firebirdsql.org/en/python-driver/
.. _fdb: http://www.firebirdsql.org/en/devel-python-driver/
.. _kinterbasdb: http://kinterbasdb.sourceforge.net/
.. _pyfirebirdsql: https://pypi.org/project/firebirdsql/
.. _`MAX DB`: http://maxdb.sap.com/
.. _sapdb: http://maxdb.sap.com/doc/7_8/50/01923f25b842438a408805774f6989/frameset.htm
.. _Sybase: http://www.object-craft.com.au/projects/sybase/
.. _`MSSQL Server`: http://www.microsoft.com/sql/
.. _pymssql: http://www.pymssql.org/en/latest/index.html
.. _FreeTDS: http://www.freetds.org/
.. _adodbapi: http://adodbapi.sourceforge.net/
.. _PyODBC: https://pypi.org/project/pyodbc/
.. _PyPyODBC: https://pypi.org/project/pypyodbc/

Python 2.7 or 3.4+ is required.

Compared To Other Database Wrappers
===================================

There are several object-relational mappers (ORM) for Python.  We
honestly can't comment deeply on the quality of those packages, but
we'll try to place SQLObject in perspective.

Objects have built-in magic -- setting attributes has side effects (it
changes the database), and defining classes has side effects (through
the use of metaclasses).  Attributes are generally exposed, not marked
private, knowing that they can be made dynamic or write-only later.

SQLObject creates objects that feel similar to normal Python objects. An
attribute attached to a column doesn't look different than an attribute
that's attached to a file, or an attribute that is calculated.  It is a
specific goal that you be able to change the database without changing
the interface, including changing the scope of the database, making it
more or less prominent as a storage mechanism.

This is in contrast to some ORMs that provide a dictionary-like
interface to the database (for example, PyDO_).  The dictionary
interface distinguishes the row from a normal Python object.  We also
don't care for the use of strings where an attribute seems more
natural -- columns are limited in number and predefined, just like
attributes.  (Note: newer version of PyDO apparently allow attribute
access as well)

.. _PyDO: http://skunkweb.sourceforge.net/pydo.html

SQLObject is, to my knowledge, unique in using metaclasses to
facilitate this seamless integration.  Some other ORMs use code
generation to create an interface, expressing the schema in a CSV or
XML file (for example, MiddleKit_, part of Webware_).  By using
metaclasses you are able to comfortably define your schema in the
Python source code.  No code generation, no weird tools, no
compilation step.

.. _MiddleKit: http://webware.sourceforge.net/Webware/MiddleKit/Docs/
.. _Webware: http://webware.sourceforge.net/Webware/Docs/

SQLObject provides a strong database abstraction, allowing
cross-database compatibility (so long as you don't sidestep
SQLObject).

SQLObject has joins, one-to-many, and many-to-many, something which
many ORMs do not have.  The join system is also intended to be
extensible.

You can map between database names and Python attribute and class
names; often these two won't match, or the database style would be
inappropriate for a Python attribute.  This way your database schema
does not have to be designed with SQLObject in mind, and the resulting
classes do not have to inherit the database's naming schemes.

Using SQLObject: An Introduction
================================

Let's start off quickly.  We'll generally just import everything from
the ``sqlobject`` class::

    >>> from sqlobject import *

Declaring a Connection
----------------------

The connection URI must follow the standard URI syntax::

    scheme://[user[:password]@]host[:port]/database[?parameters]

Scheme is one of ``sqlite``, ``mysql``, ``postgres``, ``firebird``,
``interbase``, ``maxdb``, ``sapdb``, ``mssql``, ``sybase``.

Examples::

    mysql://user:password@host/database
    mysql://host/database?debug=1
    postgres://user@host/database?debug=&cache=
    postgres:///full/path/to/socket/database
    postgres://host:5432/database
    sqlite:///full/path/to/database
    sqlite:/C:/full/path/to/database
    sqlite:/:memory:

Parameters are: ``debug`` (default: False), ``debugOutput`` (default: False),
``cache`` (default: True), ``autoCommit`` (default: True),
``debugThreading`` (default: False),
``logger`` (default: None), ``loglevel`` (default: None),
``schema`` (default: None).

If you want to pass True value in a connection URI - pass almost any
non-empty string, especially ``yes``, ``true``, ``on`` or ``1``; an
empty string or ``no``, ``false``, ``off`` or ``0`` for False.

There are also connection-specific parameters, they are listed in the
appropriate sections.

Lets first set up a connection::

    >>> import os
    >>> db_filename = os.path.abspath('data.db')
    >>> connection_string = 'sqlite:' + db_filename
    >>> connection = connectionForURI(connection_string)
    >>> sqlhub.processConnection = connection

The ``sqlhub.processConnection`` assignment means that all classes
will, by default, use this connection we've just set up.

Declaring the Class
-------------------

We'll develop a simple addressbook-like database.  We could create the
tables ourselves, and just have SQLObject access those tables, but
let's have SQLObject do that work.  First, the class:

    >>> class Person(SQLObject):
    ...
    ...     firstName = StringCol()
    ...     middleInitial = StringCol(length=1, default=None)
    ...     lastName = StringCol()

Many basic table schemas won't be any more complicated than that.
`firstName`, `middleInitial`, and `lastName` are all columns in the
database.  The general schema implied by this class definition is::

    CREATE TABLE person (
        id INT PRIMARY KEY AUTO_INCREMENT,
        first_name TEXT,
        middle_initial CHAR(1),
        last_name TEXT
    );

This is for SQLite or MySQL.  The schema for other databases looks
slightly different (especially the ``id`` column).  You'll notice the
names were changed from mixedCase to underscore_separated -- this is
done by the `style object`_.  There are a variety of ways to handle
names that don't fit conventions (see `Irregular Naming`_).

.. _`style object`: `Changing the Naming Style`_

Now we'll create the table in the database::

    >>> Person.createTable()
    []

We can change the type of the various columns by using something other
than `StringCol`, or using different arguments.  More about this in
`Column Types`_.

You'll note that the ``id`` column is not given in the class definition,
it is implied.  For MySQL databases it should be defined as ``INT
PRIMARY KEY AUTO_INCREMENT``, in Postgres ``SERIAL PRIMARY KEY``, in
SQLite as ``INTEGER PRIMARY KEY AUTOINCREMENT``, and for other backends
accordingly.  You can't use tables with SQLObject that don't have a
single primary key, and you must treat that key as immutable (otherwise
you'll confuse SQLObject terribly).

You can `override the id name`_ in the database, but it is
always called ``.id`` from Python.

.. _`override the id name`: `Class sqlmeta`_

Using the Class
---------------

Now that you have a class, how will you use it?  We'll be considering
the class defined above.

To create a new object (and row), use class instantiation, like::

    >>> Person(firstName="John", lastName="Doe")
    <Person 1 firstName='John' middleInitial=None lastName='Doe'>

.. note::

   In SQLObject NULL/None does *not* mean default.  NULL is a funny
   thing; it means very different things in different contexts and to
   different people.  Sometimes it means "default", sometimes "not
   applicable", sometimes "unknown".  If you want a default, NULL or
   otherwise, you always have to be explicit in your class
   definition.

   Also note that the SQLObject default isn't the same as the
   database's default (SQLObject never uses the database's default).

If you had left out ``firstName`` or ``lastName`` you would have
gotten an error, as no default was given for these columns
(``middleInitial`` has a default, so it will be set to ``NULL``, the
database equivalent of ``None``).

You can use the class method `.get()` to fetch instances that
already exist::

    >>> Person.get(1)
    <Person 1 firstName='John' middleInitial=None lastName='Doe'>

When you create an object, it is immediately inserted into the
database.  SQLObject uses the database as immediate storage, unlike
some other systems where you explicitly save objects into a database.

Here's a longer example of using the class::

    >>> p = Person.get(1)
    >>> p
    <Person 1 firstName='John' middleInitial=None lastName='Doe'>
    >>> p.firstName
    'John'
    >>> p.middleInitial = 'Q'
    >>> p.middleInitial
    'Q'
    >>> p2 = Person.get(1)
    >>> p2
    <Person 1 firstName='John' middleInitial='Q' lastName='Doe'>
    >>> p is p2
    True

Columns are accessed like attributes (This uses the ``property``
feature of Python, so that retrieving and setting these attributes
executes code).  Also note that objects are unique -- there is
generally only one ``Person`` instance of a particular id in memory at
any one time.  If you ask for a person by a particular ID more than
once, you'll get back the same instance.  This way you can be sure of
a certain amount of consistency if you have multiple threads accessing
the same data (though of course across processes there can be no
sharing of an instance).  This isn't true if you're using
transactions_, which are necessarily isolated.

To get an idea of what's happening behind the surface, we'll give the
same actions with the SQL that is sent, along with some commentary::

    >>> # This will make SQLObject print out the SQL it executes:
    >>> Person._connection.debug = True
    >>> p = Person(firstName='Bob', lastName='Hope')
     1/QueryIns:  INSERT INTO person (first_name, middle_initial, last_name) VALUES ('Bob', NULL, 'Hope')
     1/QueryR  :  INSERT INTO person (first_name, middle_initial, last_name) VALUES ('Bob', NULL, 'Hope')
     1/COMMIT  :  auto
     1/QueryOne:  SELECT first_name, middle_initial, last_name FROM person WHERE ((person.id) = (2))
     1/QueryR  :  SELECT first_name, middle_initial, last_name FROM person WHERE ((person.id) = (2))
     1/COMMIT  :  auto
    >>> p
    <Person 2 firstName='Bob' middleInitial=None lastName='Hope'>
    >>> p.middleInitial = 'Q'
     1/Query   :  UPDATE person SET middle_initial = ('Q') WHERE id = (2)
     1/QueryR  :  UPDATE person SET middle_initial = ('Q') WHERE id = (2)
     1/COMMIT  :  auto
    >>> p2 = Person.get(1)
    >>> # Note: no database access, since we're just grabbing the same
    >>> # instance we already had.

Hopefully you see that the SQL that gets sent is pretty clear and
predictable.  To view the SQL being sent, add ``?debug=true`` to your
connection URI, or set the ``debug`` attribute on the connection, and
all SQL will be printed to the console.  This can be reassuring, and we
would encourage you to try it.

As a small optimization, instead of assigning each attribute
individually, you can assign a number of them using the ``set``
method, like::

    >>> p.set(firstName='Robert', lastName='Hope Jr.')

This will send only one ``UPDATE`` statement.  You can also use `set`
with non-database properties (there's no benefit, but it helps hide
the difference between database and non-database attributes).

Selecting Multiple Objects
--------------------------

While the full power of all the kinds of joins you can do with a
relational database are not revealed in SQLObject, a simple ``SELECT``
is available.

``select`` is a class method, and you call it like (with the SQL
that's generated)::

    >>> Person._connection.debug = True
    >>> peeps = Person.select(Person.q.firstName=="John")
    >>> list(peeps)
     1/Select  :  SELECT person.id, person.first_name, person.middle_initial, person.last_name FROM person WHERE ((person.first_name) = ('John'))
     1/QueryR  :  SELECT person.id, person.first_name, person.middle_initial, person.last_name FROM person WHERE ((person.first_name) = ('John'))
     1/COMMIT  :  auto
    [<Person 1 firstName='John' middleInitial='Q' lastName='Doe'>]

This example returns everyone with the first name John.

Queries can be more complex::

    >>> peeps = Person.select(
    ...         OR(Person.q.firstName == "John",
    ...            LIKE(Person.q.lastName, "%Hope%")))
    >>> list(peeps)
     1/Select  :  SELECT person.id, person.first_name, person.middle_initial, person.last_name FROM person WHERE (((person.first_name) = ('John')) OR (person.last_name LIKE ('%Hope%')))
     1/QueryR  :  SELECT person.id, person.first_name, person.middle_initial, person.last_name FROM person WHERE (((person.first_name) = ('John')) OR (person.last_name LIKE ('%Hope%')))
     1/COMMIT  :  auto
    [<Person 1 firstName='John' middleInitial='Q' lastName='Doe'>, <Person 2 firstName='Robert' middleInitial='Q' lastName='Hope Jr.'>]


You'll note that classes have an attribute ``q``, which gives access
to special objects for constructing query clauses.  All attributes
under ``q`` refer to column names and if you construct logical
statements with these it'll give you the SQL for that statement.  You
can also create your SQL more manually::

    >>> Person._connection.debug = False  # Need for doctests
    >>> peeps = Person.select("""person.first_name = 'John' AND
    ...                          person.last_name LIKE 'D%'""")


You should use `MyClass.sqlrepr` to quote any values you use if you
create SQL manually (quoting is automatic if you use ``q``).

.. _orderBy:

You can use the keyword arguments `orderBy` to create ``ORDER BY`` in the
select statements: `orderBy` takes a string, which should be the *database*
name of the column, or a column in the form ``Person.q.firstName``.  You
can use ``"-colname"`` or ``DESC(Person.q.firstName``) to specify
descending order (this is translated to DESC, so it works on non-numeric
types as well), or call ``MyClass.select().reversed()``. orderBy can also
take a list of columns in the same format: ``["-weight", "name"]``.

You can use the `sqlmeta`_ class variable `defaultOrder` to give a
default ordering for all selects.  To get an unordered result when
`defaultOrder` is used, use ``orderBy=None``.

.. _`sqlmeta`: `Class sqlmeta`_

Select results are generators, which are lazily evaluated.  So the SQL
is only executed when you iterate over the select results, or if you
use ``list()`` to force the result to be executed.  When you iterate
over the select results, rows are fetched one at a time.  This way you
can iterate over large results without keeping the entire result set
in memory.  You can also do things like ``.reversed()`` without
fetching and reversing the entire result -- instead, SQLObject can
change the SQL that is sent so you get equivalent results.

You can also slice select results.  This modifies the SQL query, so
``peeps[:10]`` will result in ``LIMIT 10`` being added to the end of
the SQL query.  If the slice cannot be performed in the SQL (e.g.,
peeps[:-10]), then the select is executed, and the slice is performed
on the list of results.  This will generally only happen when you use
negative indexes.

In certain cases, you may get a select result with an object in it
more than once, e.g., in some joins.  If you don't want this, you can
add the keyword argument ``MyClass.select(..., distinct=True)``, which
results in a ``SELECT DISTINCT`` call.

You can get the length of the result without fetching all the results
by calling ``count`` on the result object, like
``MyClass.select().count()``.  A ``COUNT(*)`` query is used -- the
actual objects are not fetched from the database.  Together with
slicing, this makes batched queries easy to write:

    start = 20
    size = 10
    query = Table.select()
    results = query[start:start+size]
    total = query.count()
    print "Showing page %i of %i" % (start/size + 1, total/size + 1)

.. note::

   There are several factors when considering the efficiency of this
   kind of batching, and it depends very much how the batching is
   being used.  Consider a web application where you are showing an
   average of 100 results, 10 at a time, and the results are ordered
   by the date they were added to the database.  While slicing will
   keep the database from returning all the results (and so save some
   communication time), the database will still have to scan through
   the entire result set to sort the items (so it knows which the
   first ten are), and depending on your query may need to scan
   through the entire table (depending on your use of indexes).
   Indexes are probably the most important way to improve performance
   in a case like this, and you may find caching to be more effective
   than slicing.

   In this case, caching would mean retrieving the *complete* results.
   You can use ``list(MyClass.select(...))`` to do this.  You can save
   these results for some limited period of time, as the user looks
   through the results page by page.  This means the first page in a
   search result will be slightly more expensive, but all later pages
   will be very cheap.

For more information on the where clause in the queries, see the
`SQLBuilder documentation`_.

q-magic
~~~~~~~

Please note the use of the `q` attribute in examples above. `q` is an
object that returns special objects to construct SQL expressions.
Operations on objects returned by `q-magic` are not evaluated immediately
but stored in a manner similar to symbolic algebra; the entire expression
is evaluated by constructing a string that is sent then to the backend.

For example, for the code::

    >>> peeps = Person.select(Person.q.firstName=="John")

SQLObject doesn't evaluate firstName but stores the expression:

    Person.q.firstName=="John"

Later SQLObject converts it to the string ``first_name = 'John'`` and
passes the string to the backend.

selectBy Method
~~~~~~~~~~~~~~~

An alternative to ``.select`` is ``.selectBy``.  It works like:

    >>> peeps = Person.selectBy(firstName="John", lastName="Doe")

Each keyword argument is a column, and all the keyword arguments
are ANDed together.  The return value is a `SelectResults`, so you
can slice it, count it, order it, etc.


Lazy Updates
------------

By default SQLObject sends an ``UPDATE`` to the database for every
attribute you set, or every time you call ``.set()``.  If you want to
avoid this many updates, add ``lazyUpdate = True`` to your class `sqlmeta
definition`_.

.. _`sqlmeta definition`: `Class sqlmeta`_

Then updates will only be written to the database when
you call ``inst.syncUpdate()`` or ``inst.sync()``: ``.sync()`` also
refetches the data from the database, which ``.syncUpdate()`` does not
do.

When enabled instances will have a property ``.sqlmeta.dirty``, which
indicates if there are pending updates.  Inserts are still done
immediately; there's no way to do lazy inserts at this time.

One-to-Many Relationships
-------------------------

An address book is nothing without addresses.

First, let's define the new address table.  People can have multiple
addresses, of course::

    >>> class Address(SQLObject):
    ...
    ...     street = StringCol()
    ...     city = StringCol()
    ...     state = StringCol(length=2)
    ...     zip = StringCol(length=9)
    ...     person = ForeignKey('Person')
    >>> Address.createTable()
    []

Note the column ``person = ForeignKey("Person")``.  This is a
reference to a `Person` object.  We refer to other classes by name
(with a string).  In the address table there will be a ``person_id``
column, type ``INT``, which points to the ``person`` table.

.. note::

   The reason SQLObject uses strings to refer to other classes is
   because the other class often does not yet exist.  Classes in
   Python are *created*, not *declared*; so when a module is imported
   the commands are executed.  ``class`` is just another command; one
   that creates a class and assigns it to the name you give.

   If class ``A`` referred to class ``B``, but class ``B`` was defined
   below ``A`` in the module, then when the ``A`` class was created
   (including creating all its column attributes) the ``B`` class
   simply wouldn't exist.  By referring to classes by name, we can
   wait until all the required classes exist before creating the links
   between classes.

We want an attribute that gives the addresses for a person.  In a
class definition we'd do::

    class Person(SQLObject):
        ...
        addresses = MultipleJoin('Address')

But we already have the class.  We can add this to the class
in-place::

    >>> Person.sqlmeta.addJoin(MultipleJoin('Address',
    ...                        joinMethodName='addresses'))

.. note::

   In almost all cases you can modify SQLObject classes after they've
   been created.  Having attributes that contain ``*Col`` objects in
   the class definition is equivalent to calling certain class methods
   (like ``addColumn()``).

Now we can get the backreference with ``Person.addresses``, which
returns a list.  An example::

    >>> p.addresses
    []
    >>> Address(street='123 W Main St', city='Smallsville',
    ...         state='MN', zip='55407', person=p)
    <Address 1 ...>
    >>> p.addresses
    [<Address 1 ...>]

.. note::
  MultipleJoin, as well as RelatedJoin, returns a list of results.
  It is often preferable to get a `SelectResults`_ object instead, 
  in which case you should use
  SQLMultipleJoin and SQLRelatedJoin. The declaration of these joins is
  unchanged from above, but the returned iterator has many additional useful methods.

.. _`SelectResults` : SelectResults.html

Many-to-Many Relationships
--------------------------

For this example we will have user and role objects.  The two have a
many-to-many relationship, which is represented with the
`RelatedJoin`.

    >>> class User(SQLObject):
    ...
    ...     class sqlmeta:
    ...         # user is a reserved word in some databases, so we won't
    ...         # use that for the table name:
    ...         table = "user_table"
    ...
    ...     username = StringCol(alternateID=True, length=20)
    ...     # We'd probably define more attributes, but we'll leave
    ...     # that exercise to the reader...
    ...
    ...     roles = RelatedJoin('Role')

    >>> class Role(SQLObject):
    ...
    ...     name = StringCol(alternateID=True, length=20)
    ...
    ...     users = RelatedJoin('User')

    >>> User.createTable()
    []
    >>> Role.createTable()
    []

.. note::

  The sqlmeta class is used to store
  different kinds of metadata (and override that metadata, like table).
  This is new in SQLObject 0.7. See the section `Class sqlmeta`_ for more
  information on how it works and what attributes have special meanings.

And usage::

    >>> bob = User(username='bob')
    >>> tim = User(username='tim')
    >>> jay = User(username='jay')
    >>> admin = Role(name='admin')
    >>> editor = Role(name='editor')
    >>> bob.addRole(admin)
    >>> bob.addRole(editor)
    >>> tim.addRole(editor)
    >>> bob.roles
    [<Role 1 name='admin'>, <Role 2 name='editor'>]
    >>> tim.roles
    [<Role 2 name='editor'>]
    >>> jay.roles
    []
    >>> admin.users
    [<User 1 username='bob'>]
    >>> editor.users
    [<User 1 username='bob'>, <User 2 username='tim'>]

In the process an intermediate table is created, ``role_user``, which
references both of the other classes.  This table is never exposed as
a class, and its rows do not have equivalent Python objects -- this
hides some of the nuisance of a many-to-many relationship.

By the way, if you want to create an intermediate table of your own,
maybe with additional columns, be aware that the standard SQLObject
methods add/removesomething may not work as expected. Assuming that
you are providing the join with the correct joinColumn and otherColumn
arguments, be aware it's not possible to insert extra data via such
methods, nor will they set any default value.

Let's have an example: in the previous User/Role system,
you're creating a UserRole intermediate table, with the two columns
containing the foreign keys for the MTM relationship, and an additional
DateTimeCol defaulting to datetime.datetime.now : that column will
stay empty when adding roles with the addRole method.
If you want to get a list of rows from the intermediate table directly
add a MultipleJoin to User or Role class.

You may notice that the columns have the extra keyword argument
`alternateID`.  If you use ``alternateID=True``, this means that the
column uniquely identifies rows -- like a username uniquely identifies
a user.  This identifier is in addition to the primary key (``id``),
which is always present.

.. note::

   SQLObject has a strong requirement that the primary key be unique
   and *immutable*.  You cannot change the primary key through
   SQLObject, and if you change it through another mechanism you can
   cause inconsistency in any running SQLObject program (and in your
   data).  For this reason meaningless integer IDs are encouraged --
   something like a username that could change in the future may
   uniquely identify a row, but it may be changed in the future.  So
   long as it is not used to reference the row, it is also *safe* to
   change it in the future.

A alternateID column creates a class method, like ``byUsername`` for a
column named ``username`` (or you can use the `alternateMethodName`
keyword argument to override this).  Its use:

    >>> User.byUsername('bob')
    <User 1 username='bob'>
    >>> Role.byName('admin')
    <Role 1 name='admin'>


Selecting Objects Using Relationships
-------------------------------------

An select expression can refer to multiple classes, like::

    >>> Person._connection.debug = False # Needed for doctests
    >>> peeps = Person.select(
    ...         AND(Address.q.personID == Person.q.id,
    ...             Address.q.zip.startswith('504')))
    >>> list(peeps)
    []
    >>> peeps = Person.select(
    ...         AND(Address.q.personID == Person.q.id,
    ...             Address.q.zip.startswith('554')))
    >>> list(peeps)
    [<Person 2 firstName='Robert' middleInitial='Q' lastName='Hope Jr.'>]


It is also possible to use the ``q`` attribute when constructing complex
queries, like::

    >>> Person._connection.debug = False  # Needed for doctests
    >>> peeps = Person.select("""address.person_id = person.id AND
    ...                          address.zip LIKE '504%'""",
    ...                       clauseTables=['address'])

Note that you have to use ``clauseTables`` if you use tables besides
the one you are selecting from.  If you use the ``q`` attributes
SQLObject will automatically figure out what extra classes you might
have used.

Class sqlmeta
-------------

This new class is available starting with SQLObject 0.7 and allows
specifying metadata in a clearer way, without polluting the class
namespace with more attributes.

There are some special attributes that can be used inside this class
that will change the behavior of the class that contains it.  Those
values are:

`table`:
   The name of the table in the database.  This is derived from
   ``style`` and the class name if no explicit name is given.  If you
   don't give a name and haven't defined an alternative ``style``, then
   the standard `MixedCase` to `mixed_case` translation is performed.

`idName`:
   The name of the primary key column in the database.  This is
   derived from ``style`` if no explicit name is given.  The default name
   is ``id``.

`idType`:
   A type that coerces/normalizes IDs when setting IDs.  Must be ``int``
   or ``str``. This is ``int`` by default (all IDs are normalized to
   integers).

`idSize`:
   This sets the size of integer column ``id`` for MySQL and PostgreSQL.
   Allowed values are ``'TINY'``, ``'SMALL'``, ``'MEDIUM'``, ``'BIG'``,
   ``None``; default is ``None``. For Postgres mapped to
   ``smallserial``/``serial``/``bigserial``. For other backends it's
   currently ignored.

`style`:
   A style object -- this object allows you to use other algorithms
   for translating between Python attribute and class names, and the
   database's column and table names.  See `Changing the Naming
   Style`_ for more.  It is an instance of the `IStyle` interface.

`lazyUpdate`:
   A boolean (default false).  If true, then setting attributes on
   instances (or using ``inst.set(.)`` will not send ``UPDATE``
   queries immediately (you must call ``inst.syncUpdates()`` or
   ``inst.sync()`` first).

`defaultOrder`:
   When selecting objects and not giving an explicit order, this
   attribute indicates the default ordering.  It is like this value
   is passed to ``.select()`` and related methods; see those method's
   documentation for details.

`cacheValues`:
   A boolean (default true).  If true, then the values in the row are
   cached as long as the instance is kept (and ``inst.expire()`` is
   not called).

   If set to `False` then values for attributes from the database
   won't be cached.  So every time you access an attribute in the
   object the database will be queried for a value, i.e., a ``SELECT``
   will be issued.  If you want to handle concurrent access to the
   database from multiple processes then this is probably the way to
   do so.

`registry`:
   Because SQLObject uses strings to relate classes, and these
   strings do not respect module names, name clashes will occur if
   you put different systems together.  This string value serves
   as a namespace for classes.

`fromDatabase`:
   A boolean (default false).  If true, then on class creation the
   database will be queried for the table's columns, and any missing
   columns (possible all columns) will be added automatically. Please be
   warned that not all connections fully implement database
   introspection.

`dbEncoding`:
   UnicodeCol_ looks up `sqlmeta.dbEncoding` if `column.dbEncoding` is
   ``None`` (if `sqlmeta.dbEncoding` is ``None`` UnicodeCol_ looks up
   `connection.dbEncoding` and if `dbEncoding` isn't defined anywhere it
   defaults to ``"utf-8"``). For Python 3 there must be one encoding for
   connection - do not define different columns with different
   encodings, it's not implemented.

.. _UnicodeCol: `Column Types`_

The following attributes provide introspection but should not be set directly -
see `Runtime Column and Join Changes`_ for dynamically modifying these class
elements.

`columns`:
   A dictionary of ``{columnName: anSOColInstance}``.  You can get
   information on the columns via this read-only attribute.

`columnList`:
   A list of the values in ``columns``.  Sometimes a stable, ordered
   version of the columns is necessary; this is used for that.

`columnDefinitions`:
   A dictionary like ``columns``, but contains the original column
   definitions (which are not class-specific, and have no logic).

`joins`:
   A list of all the Join objects for this class.

`indexes`:
   A list of all the indexes for this class.

`createSQL`:
   SQL queries run after table creation. createSQL can be a string with a
   single SQL command, a list of SQL commands, or a dictionary with keys that
   are dbNames and values that are either single SQL command string or a list
   of SQL commands. This is usually for ALTER TABLE commands.

There is also one instance attribute:

`expired`:
   A boolean.  If true, then the next time this object's column
   attributes are accessed a query will be run.

While in previous versions of SQLObject those attributes were defined
directly at the class that will map your database data to Python and
all of them were prefixed with an underscore, now it is suggested that
you change your code to this new style.  The old way was removed
in SQLObject 0.8.

Please note: when using InheritedSQLObject, sqlmeta attributes don't
get inherited, e.g. you can't access via the sqlmeta.columns dictionary
the parent's class column objects.

Using sqlmeta
~~~~~~~~~~~~~

To use sqlmeta you should write code like this example::

    class MyClass(SQLObject):

        class sqlmeta:
            lazyUpdate = True
            cacheValues = False

        columnA = StringCol()
        columnB = IntCol()

        def _set_attr1(self, value):
            # do something with value

        def _get_attr1(self):
            # do something to retrieve value

The above definition is creating a table ``my_class`` (the name may be
different if you change the ``style`` used) with two columns called
columnA and columnB.  There's also a third field that can be accessed
using ``MyClass.attr1``.  The sqlmeta class is changing the behavior
of ``MyClass`` so that it will perform lazy updates (you'll have to call
the ``.sync()`` method to write the updates to the database) and it is
also telling that ``MyClass`` won't have any cache, so that every time
you ask for some information it will be retrieved from the database.

j-magic
~~~~~~~

There is a magic attribute `j` similar to q_ with attributes for
ForeignKey and SQLMultipleJoin/SQLRelatedJoin, providing a shorthand for
the SQLBuilder join expressions to traverse the given relationship. For
example, for a ForeignKey AClass.j.someB is equivalent to
(AClass.q.someBID==BClass.q.id), as is BClass.j.someAs for the matching
SQLMultipleJoin.

.. _q: q-magic_

SQLObject Class
---------------

There is one special attribute - `_connection`. It is the connection
defined for the table.

`_connection`:
    The connection object to use, from `DBConnection`.  You can also
    set the variable `__connection__` in the enclosing module and it
    will be picked up (be sure to define `__connection__` before your
    class).  You can also pass a connection object in at instance
    creation time, as described in transactions_.

    If you have defined `sqlhub.processConnection` then this attribute can
    be omitted from your class and the sqlhub will be used instead.  If
    you have several classes using the same connection that might be an
    advantage, besides saving a lot of typing.

Customizing the Objects
-----------------------

While we haven't done so in the examples, you can include your own
methods in the class definition.  Writing your own methods should be
obvious enough (just do so like in any other class), but there are
some other details to be aware of.

Initializing the Objects
~~~~~~~~~~~~~~~~~~~~~~~~

There are two ways SQLObject instances can come into existence: they
can be fetched from the database, or they can be inserted into the
database.  In both cases a new Python object is created.  This makes
the role of `__init__` a little confusing.

In general, you should not touch `__init__`.  Instead use the `_init`
method, which is called after an object is fetched or inserted.  This
method has the signature ``_init(self, id, connection=None,
selectResults=None)``, though you may just want to use ``_init(self,
*args, **kw)``.  **Note:** don't forget to call
``SQLObject._init(self, *args, **kw)`` if you override the method!

Adding Magic Attributes (properties)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use all the normal techniques for defining methods in this
class, including `classmethod`, `staticmethod`, and `property`, but you
can also use a shortcut.  If you have a method that's name starts with
``_set_``, ``_get_``, ``_del_``, or ``_doc_``, it will be used to create
a property.  So, for instance, say you have images stored under the ID
of the person in the ``/var/people/images`` directory::

    class Person(SQLObject):
        # ...

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
            # We usually wouldn't include a method like this, but for
            # instructional purposes...
            os.unlink(self.imageFilename())


Later, you can use the ``.image`` property just like an attribute, and
the changes will be reflected in the filesystem by calling these
methods.  This is a good technique for information that is better to
keep in files as opposed to the database (such as large, opaque data
like images).

You can also pass an ``image`` keyword argument to the constructor
or the `set` method, like ``Person(..., image=imageText)``.

All of the methods (``_get_``, ``_set_``, etc) are optional -- you can
use any one of them without using the others.  So you could define
just a ``_get_attr`` method so that ``attr`` was read-only.

Overriding Column Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's a little more complicated if you want to override the behavior of
an database column attribute.  For instance, imagine there's special
code you want to run whenever someone's name changes.  In many systems
you'd do some custom code, then call the superclass's code.  But the
superclass (``SQLObject``) doesn't know anything about the column in
your subclass.  It's even worse with properties.

SQLObject creates methods like ``_set_lastName`` for each of your
columns, but again you can't use this, since there's no superclass to
reference (and you can't write ``SQLObject._set_lastName(...)``,
because the SQLObject class doesn't know about your class's columns).
You want to override that ``_set_lastName`` method yourself.

To deal with this, SQLObject creates two methods for each getter and
setter, for example: ``_set_lastName`` and ``_SO_set_lastName``.  So
to intercept all changes to ``lastName``::

    class Person(SQLObject):
        lastName = StringCol()
        firstName = StringCol()

        def _set_lastName(self, value):
            self.notifyLastNameChange(value)
            self._SO_set_lastName(value)

Or perhaps you want to constrain a phone numbers to be actual
digits, and of proper length, and make the formatting nice::

    import re

    class PhoneNumber(SQLObject):
        phoneNumber = StringCol(length=30)

        _garbageCharactersRE = re.compile(r'[\-\.\(\) ]')
        _phoneNumberRE = re.compile(r'^[0-9]+$')
        def _set_phoneNumber(self, value):
            value = self._garbageCharactersRE.sub('', value)
            if not len(value) >= 10:
                raise ValueError(
                    'Phone numbers must be at least 10 digits long')
            if not self._phoneNumberRE.match(value):
                raise ValueError, 'Phone numbers can contain only digits'
            self._SO_set_phoneNumber(value)

        def _get_phoneNumber(self):
            value = self._SO_get_phoneNumber()
            number = '(%s) %s-%s' % (value[0:3], value[3:6], value[6:10])
            if len(value) > 10:
                number += ' ext.%s' % value[10:]
            return number

.. note::

   You should be a little cautious when modifying data that gets set
   in an attribute.  Generally someone using your class will expect
   that the value they set the attribute to will be the same value
   they get back.  In this example we removed some of the characters
   before putting it in the database, and reformatted it on the way
   out.  One advantage of methods (as opposed to attribute access) is
   that the programmer is more likely to expect this disconnect.

   Also note while these conversions will take place when getting and
   setting the column, in queries the conversions will not take place.
   So if you convert the value from a "Pythonic" representation to a
   "SQLish" representation, your queries (when using ``.select()`` and
   ``.selectBy()``) will have to be in terms of the SQL/Database
   representation (as those commands generate SQL that is run on the
   database).

Undefined attributes
~~~~~~~~~~~~~~~~~~~~

There's one more thing  worth telling, because you may something get
strange results when making a typo. SQLObject won't ever complain or
raise any error when setting a previously undefined attribute; it will
simply set it, without making any change to the database, i.e: it will
work as any other attribute you set on any Python class, it will
'forget' it is a SQLObject class.

This may sometimes be a problem: if you have got a 'name' attribute and
you you write ``a.namme="Victor"`` once, when setting it, you'll get no
error, no warning, nothing at all, and you may get crazy at understanding
why you don't get that value set in your DB.


Reference
=========

The instructions above should tell you enough to get you started, and
be useful for many situations.  Now we'll show how to specify the
class more completely.

Col Class: Specifying Columns
-----------------------------

The list of columns is a list of `Col` objects.  These objects don't
have functionality in themselves, but give you a way to specify the
column.

`dbName`:
    This is the name of the column in the database.  If you don't
    give a name, your Pythonic name will be converted from
    mixed-case to underscore-separated.
`default`:
    The default value for this column.  Used when creating a new row.
    If you give a callable object or function, the function will be
    called, and the return value will be used.  So you can give
    ``DateTimeCol.now`` to make the default value be the current time.
    Or you can use ``sqlbuilder.func.NOW()`` to have the database use
    the ``NOW()`` function internally.  If you don't give a default
    there will be an exception if this column isn't specified in the
    call to `new`.
`defaultSQL`:
    ``DEFAULT`` SQL attribute.
`alternateID`:
    This boolean (default False) indicates if the column can be used
    as an ID for the field (for instance, a username), though it is
    not a primary key.  If so a class method will be added, like
    ``byUsername`` which will return that object.  Use
    `alternateMethodName` if you don't like the ``by*`` name
    (e.g. ``alternateMethodName="username"``).

    The column should be declared ``UNIQUE`` in your table schema.
`unique`:
    If true, when SQLObject creates a table it will declare this
    column to be ``UNIQUE``.
`notNone`:
    If true, None/``NULL`` is not allowed for this column.  Useful if
    you are using SQLObject to create your tables.
`sqlType`:
    The SQL type for this column (like ``INT``, ``BOOLEAN``, etc).
    You can use classes (defined below) for this, but if those don't
    work it's sometimes easiest just to use `sqlType`.  Only necessary
    if SQLObject is creating your tables.
`validator`:
    formencode_-like validator_. Making long story short, this is
    an object that provides ``to_python()`` and ``from_python()``
    to validate *and* convert (adapt or cast) the values when they are
    read/written from/to the database. You should see formencode_
    validator_ documentation for more details. This validator is appended
    to the end of the list of the list of column validators. If the column
    has a list of validators their ``from_python()`` methods are ran from
    the beginnig of the list to the end; ``to_python()`` in the reverse
    order. That said, ``from_python()`` method of this validator is called
    last, after all validators in the list; ``to_python()`` is called first.
`validator2`:
    Another validator. It is inserted in the beginning of the list of the
    list of validators, i.e. its ``from_python()`` method is called first;
    ``to_python()`` last.

.. _formencode: http://formencode.org/
.. _validator: http://www.formencode.org/en/latest/Validator.html

Column Types
~~~~~~~~~~~~

The `ForeignKey` class should be used instead of `Col` when the column
is a reference to another table/class.  It is generally used like
``ForeignKey('Role')``, in this instance to create a reference to a
table `Role`.  This is largely equivalent to ``Col(foreignKey='Role',
sqlType='INT')``.  Two attributes will generally be created, ``role``,
which returns a `Role` instance, and ``roleID``, which returns an
integer ID for the related role.

There are some other subclasses of `Col`.  These are used to indicate
different types of columns, when SQLObject creates your tables.

`BLOBCol`:
    A column for binary data. Presently works only with MySQL, PostgreSQL
    and SQLite backends.

`BoolCol`:
    Will create a ``BOOLEAN`` column in Postgres, or ``INT`` in other
    databases.  It will also convert values to ``"t"/"f"`` or ``0/1``
    according to the database backend.

`CurrencyCol`:
    Equivalent to ``DecimalCol(size=10, precision=2)``.
    WARNING: as DecimalCol MAY NOT return precise numbers, this column
    may share the same behavior. Please read the DecimalCol warning.

`DateTimeCol`:
    A date and time (usually returned as an datetime or mxDateTime object).

`DateCol`:
    A date (usually returned as an datetime or mxDateTime object).

`TimeCol`:
    A time (usually returned as an datetime or mxDateTime object).

`TimestampCol`:
    Supports MySQL TIMESTAMP type.

`DecimalCol`:
    Base-10, precise number.  Uses the keyword arguments `size` for
    number of digits stored, and `precision` for the number of digits
    after the decimal point.
    WARNING: it may happen that DecimalCol values, although correctly
    stored in the DB, are returned as floats instead of decimals. For
    example, due to the `type affinity`_ SQLite stores decimals as integers
    or floats (NUMERIC storage class).
    You should test with your database adapter, and you should try
    importing the Decimal type and your DB adapter before importing
    SQLObject.

.. _`type affinity`: http://sqlite.org/datatype3.html#affinity

`DecimalStringCol`:
    Similar to `DecimalCol` but stores data as strings to work around
    problems in some drivers and type affinity problem in SQLite. As it
    stores data as strings the column cannot be used in SQL expressions
    (column1 + column2) and probably will has problems with ORDER BY.

`EnumCol`:
    One of several string values -- give the possible strings as a
    list, with the `enumValues` keyword argument.  MySQL has a native
    ``ENUM`` type, but will work with other databases too (storage
    just won't be as efficient).

    For PostgreSQL, EnumCol's are implemented using check constraints.
    Due to the way PostgreSQL handles check constraints involving NULL,
    specifying None as a member of an EnumCol will effectively mean that,
    at the SQL level, the check constraint will be ignored (see
    http://archives.postgresql.org/pgsql-sql/2004-12/msg00065.php for
    more details).

`SetCol`:
    Supports MySQL SET type.

`FloatCol`:
    Floats.

`ForeignKey`:
    A key to another table/class.  Use like ``user = ForeignKey('User')``. It
    can check for referential integrity using the keyword argument `cascade`,
    please see ForeignKey_ for details.

`IntCol`:
    Integers.

`JsonbCol`:
    A column for jsonb objects. Only supported on Postgres.
    Any Python object that can be serialized with json.dumps can be stored.

`JSONCol`:
    A universal json column that converts simple Python objects (None,
    bool, int, float, long, dict, list, str/unicode to/from JSON using
    json.dumps/loads. A subclass of StringCol. Requires ``VARCHAR``/``TEXT``
    columns at backends, doesn't work with ``JSON`` columns.

`PickleCol`:
    An extension of BLOBCol; this column can store/retrieve any Python object;
    it actually (un)pickles the object from/to string and stores/retrieves the
    string. One can get and set the value of the column but cannot search
    (use it in WHERE).

`StringCol`:
    A string (character) column.  Extra keywords:

    `length`:
        If given, the type will be something like ``VARCHAR(length)``.
        If not given, then ``TEXT`` is assumed (i.e., lengthless).
    `varchar`:
        A boolean; if you have a length, differentiates between
        ``CHAR`` and ``VARCHAR``, default True, i.e., use
        ``VARCHAR``.

`UnicodeCol`:
    A subclass of `StringCol`.  Also accepts a `dbEncoding` keyword
    argument, it defaults to ``None`` which means to lookup `dbEncoding`
    in sqlmeta_ and connection, and if `dbEncoding` isn't defined
    anywhere it defaults to ``"utf-8"``.  Values coming in and out from
    the database will be encoded and decoded.  **Note**: there are some
    limitations on using UnicodeCol in queries:

    - only simple q-magic fields are supported; no expressions;
    - only == and != operators are supported;

    The following code works::

        MyTable.select(u'value' == MyTable.q.name)
        MyTable.select(MyTable.q.name != u'value')
        MyTable.select(OR(MyTable.q.col1 == u'value1', MyTable.q.col2 != u'value2'))
        MyTable.selectBy(name = u'value')
        MyTable.selectBy(col1=u'value1', col2=u'value2')
        MyTable.byCol1(u'value1') # if col1 is an alternateID

    The following does not work::

        MyTable.select((MyTable.q.name + MyTable.q.surname) == u'value')

    In that case you must apply the encoding yourself::

        MyTable.select((MyTable.q.name + MyTable.q.surname) == u'value'.encode(dbEncoding))

`UuidCol`:
    A column for UUID. On Postgres uses 'UUID' data type, on all other
    backends uses VARCHAR(36).


Relationships Between Classes/Tables
------------------------------------

ForeignKey
~~~~~~~~~~

You can use the `ForeignKey` to handle foreign references in a table,
but for back references and many-to-many relationships you'll use
joins.

`ForeignKey` allows you to specify referential integrity using the keyword
`cascade`, which can have these values:

`None`:
    No action is taken on related deleted columns (this is the default).
    Following the Person/Address example, if you delete the object `Person` with
    id 1 (John Doe), the `Address` with id 1 (123 W Main St) will be kept
    untouched (with ``personID=1``).
`False`:
    Deletion of an object that has other objects related to it using a
    `ForeignKey` will fail (sets ``ON DELETE RESTRICT``).
    Following the Person/Address example, if you delete the object `Person` with
    id 1 (John Doe) a `SQLObjectIntegrityError` exception will be raised,
    because the `Address` with id 1 (123 W Main St) has a reference
    (``personID=1``) to it.
`True`:
    Deletion of an object that has other objects related to it using a
    `ForeignKey` will delete all the related objects too (sets ``ON DELETE
    CASCADE``).
    Following the Person/Address example, if you delete the object `Person` with
    id 1 (John Doe), the `Address` with id 1 (123 W Main St) will be deleted too.
`'null'`:
    Deletion of an object that has other objects related to it using a
    `ForeignKey` will set the `ForeignKey` column to `NULL`/`None` (sets
    ``ON DELETE SET NULL``).
    Following the Person/Address example, if you delete the object `Person` with
    id 1 (John Doe), the `Address` with id 1 (123 W Main St) will be kept but
    the reference to person will be set to `NULL`/`None` (``personID=None``).


MultipleJoin and SQLMultipleJoin: One-to-Many
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See `One-to-Many Relationships`_ for an example of one-to-many
relationships.

MultipleJoin returns a list of results, while SQLMultipleJoin returns a
SelectResults object.

Several keyword arguments are allowed to the `MultipleJoin` constructor:

.. _`Multiple Join Keywords`:

`joinColumn`:
    The column name of the key that points to this table.  So, if you
    have a table ``Product``, and another table has a column
    ``ProductNo`` that points to this table, then you'd use
    ``joinColumn="ProductNo"``. WARNING: the argument you pass must
    conform to the column name in the database, not to the attribute in the
    class. So, if you have a SQLObject containing the ``ProductNo``
    column, this will probably be translated into ``product_no_id`` in
    the DB (``product_no`` is the normal uppercase- to-lowercase +
    underscores SQLO Translation, the added _id is just because the
    column referring to the table is probably a ForeignKey, and SQLO
    translates foreign keys that way). You should pass that parameter.
`orderBy`:
    Like the `orderBy`_ argument to `select()`, you can specify
    the order that the joined objects should be returned in.  `defaultOrder`
    will be used if not specified; ``None`` forces unordered results.
`joinMethodName`:
    When adding joins dynamically (using the class method `addJoin`_),
    you can give the name of the accessor for the join.  It can also be
    created automatically, and is normally implied (i.e., ``addresses =
    MultipleJoin(...)`` implies ``joinMethodName="addresses"``).

RelatedJoin and SQLRelatedJoin: Many-to-Many
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See `Many-to-Many Relationships`_ for examples of using many-to-many joins.

RelatedJoin returns a list of results, while SQLRelatedJoin returns a
SelectResults object.


`RelatedJoin` has all the keyword arguments of `MultipleJoin`__, plus:

__ `Multiple Join Keywords`_

`otherColumn`:
    Similar to `joinColumn`, but referring to the joined class. Same
    warning about column name.
`intermediateTable`:
    The name of the intermediate table which references both classes.
    WARNING: you should pass the database table name, not the SQLO
    class representing.
`addRemoveName`:
    In the `user/role example`__, the methods `addRole(role)` and
    `removeRole(role)` are created.  The ``Role`` portion of these
    method names can be changed by giving a string value here.
`createRelatedTable`:
    default: ``True``. If ``False``, then the related table won't be
    automatically created; instead you must manually create it (e.g.,
    with explicit SQLObject classes for the joins). New in 0.7.1.

.. note::
   Let's suppose you have SQLObject-inherited classes Alpha and Beta,
   and an AlphasAndBetas used for the many-to-many relationship.
   AlphasAndBetas contains the alphaIndex Foreign Key column referring
   to Alpha, and the betaIndex FK column referring to Beta.
   if you want a 'betas' RelatedJoin in Alpha, you should add it to
   Alpha passing 'Beta' (class name!) as the first parameter, then
   passing 'alpha_index_id' as joinColumn, 'beta_index_id' as
   otherColumn, and 'alphas_and_betas' as intermediateTable.

__ `Many-to-Many Relationships`_

An example schema that requires the use of `joinColumn`, `otherColumn`,
and `intermediateTable`::

    CREATE TABLE person (
        id SERIAL,
        username VARCHAR(100) NOT NULL UNIQUE
    );

    CREATE TABLE role (
        id SERIAL,
        name VARCHAR(50) NOT NULL UNIQUE
    );

    CREATE TABLE assigned_roles (
        person INT NOT NULL,
        role INT NOT NULL
    );

Then the usage in a class::

    class Person(SQLObject):
        username = StringCol(length=100, alternateID=True)
        roles = RelatedJoin('Role', joinColumn='person', otherColumn='role',
                            intermediateTable='assigned_roles')
    class Role(SQLObject):
        name = StringCol(length=50, alternateID=True)
        roles = RelatedJoin('Person', joinColumn='role', otherColumn='person',
                            intermediateTable='assigned_roles')

SingleJoin: One-to-One
~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to `MultipleJoin`, but returns just one object, not a list.


Connection pooling
------------------

Connection object acquires a new low-level DB API connection from the pool
and stores it; the low-level connection is removed from the pool;
"releasing" means "return it to the pool". For single-threaded programs
there is one connection in the pool.

If the pool is empty a new low-level connection opened; if one has
disabled pooling (by setting conn._pool = None) the connection will be
closed instead of returning to the pool.


Transactions
------------

Transaction support in SQLObject is left to the database.
Transactions can be used like::

    conn = DBConnection.PostgresConnection('yada')
    trans = conn.transaction()
    p = Person.get(1, trans)
    p.firstName = 'Bob'
    trans.commit()
    p.firstName = 'Billy'
    trans.rollback()

The ``trans`` object here is essentially a wrapper around a single
database connection, and `commit` and `rollback` just pass that
message to the low-level connection.

One can call as much ``.commit()``'s, but after a ``.rollback()`` one
has to call ``.begin()``. The last ``.commit()`` should be called as
``.commit(close=True)`` to release low-level connection back to the
connection pool.

You can use SELECT FOR UPDATE in those databases that support it::

    Person.select(Person.q.name=="value", forUpdate=True, connection=trans)

Method ``sqlhub.doInTransaction`` can be used to run a piece of code in
a transaction. The method accepts a callable and positional and keywords
arguments. It begins a transaction using its ``processConnection`` or
``threadConnection``, calls the callable, commits the transaction and
closes the underlying connection; it returns whatever the callable
returned. If an error occurs during call to the callable it rolls the
transaction back and reraise the exception.

Automatic Schema Generation
---------------------------

All the connections support creating and dropping tables based on the
class definition.  First you have to prepare your class definition,
which means including type information in your columns.

Indexes
~~~~~~~

You can also define indexes for your tables, which is only meaningful
when creating your tables through SQLObject (SQLObject relies on the
database to implement the indexes).  You do this again with attribute
assignment, like::

    firstLastIndex = DatabaseIndex('firstName', 'lastName')

This creates an index on two columns, useful if you are selecting a
particular name.  Of course, you can give a single column, and you can
give the column object (``firstName``) instead of the string name.
Note that if you use ``unique`` or ``alternateID`` (which implies
``unique``) the database may make an index for you, and primary keys
are always indexed.

If you give the keyword argument ``unique`` to `DatabaseIndex` you'll
create a unique index -- the combination of columns must be unique.

You can also use dictionaries in place of the column names, to add
extra options.  E.g.::

    lastNameIndex = DatabaseIndex({'expression': 'lower(last_name)'})

In that case, the index will be on the lower-case version of the
column.  It seems that only PostgreSQL supports this.  You can also
do::

    lastNameIndex = DatabaseIndex({'column': lastName, 'length': 10})

Which asks the database to only pay attention to the first ten
characters.  Only MySQL supports this, but it is ignored in other
databases.

Creating and Dropping Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a table call `createTable`.  It takes two arguments:

`ifNotExists`:
    If the table already exists, then don't try to create it.  Default
    False.
`createJoinTables`:
    If you used `Many-to-Many relationships`_, then the intermediate tables
    will be created (but only for one of the two involved classes).
    Default True.

`dropTable` takes arguments `ifExists` and `dropJoinTables`,
self-explanatory.

Dynamic Classes
===============

SQLObject classes can be manipulated dynamically.  This leaves open
the possibility of constructing SQLObject classes from an XML file,
from database introspection, or from a graphical interface.

Automatic Class Generation
---------------------------

SQLObject can read the table description from the database, and fill
in the class columns (as would normally be described in the `_columns`
attribute).  Do this like::

    class Person(SQLObject):
        class sqlmeta:
            fromDatabase = True

You can still specify columns (in `_columns`), and only missing
columns will be added.

Runtime Column and Join Changes
-------------------------------

You can add and remove columns to your class at runtime.  Such changes
will effect all instances, since changes are made in place to the
class.  There are two methods of the `class sqlmeta object`_,
`addColumn` and `delColumn`, both of
which take a `Col` object (or subclass) as an argument.  There's also
an option argument `changeSchema` which, if True, will add or drop the
column from the database (typically with an ``ALTER`` command).

When adding columns, you must pass the name as part of the column
constructor, like ``StringCol("username", length=20)``.  When removing
columns, you can either use the Col object (as found in `sqlmeta.columns`, or
which you used in `addColumn`), or you can use the column name (like
``MyClass.delColumn("username")``).

.. _`class sqlmeta object`: `Class sqlmeta`_

.. _addJoin:

You can also add Joins_, like
``MyClass.addJoin(MultipleJoin("MyOtherClass"))``, and remove joins with
`delJoin`.  `delJoin` does not take strings, you have to get the join
object out of the `sqlmeta.joins` attribute.

.. _Joins : `Relationships between Classes/Tables`_

Legacy Database Schemas
=======================

Often you will have a database that already exists, and does not use
the naming conventions that SQLObject expects, or does not use any
naming convention at all.

SQLObject requirements
----------------------

While SQLObject tries not to make too many requirements on your
schema, some assumptions are made.  Some of these may be relaxed in
the future.

All tables that you want to turn into a class need to have an integer
primary key.  That key should be defined like:

MySQL:
    ``INT PRIMARY KEY AUTO_INCREMENT``
Postgres:
    ``SERIAL PRIMARY KEY``
SQLite:
    ``INTEGER PRIMARY KEY AUTOINCREMENT``

SQLObject does not support primary keys made up of multiple columns (that
probably won't change).  It does not generally support tables with primary
keys with business meaning -- i.e., primary keys are assumed to be
immutable (that won't change).

At the moment foreign key column names must end in ``"ID"``
(case-insensitive).  This restriction will probably be removed in the
next release.

Workaround for primary keys made up of multiple columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the database table/view has ONE NUMERIC Primary Key then sqlmeta - idName
should be used to map the table column name to SQLObject id column.

If the Primary Key consists only of number columns it is possible to create a
virtual column ``id`` this way:

Example for Postgresql:

   select '1'||lpad(PK1,max_length_of_PK1,'0')||lpad(PK2,max_length_of_PK2,'0')||...||lpad(PKn,max_length_of_PKn,'0') as "id",
   column_PK1, column_PK2, .., column_PKn, column... from table;

Note:

* The arbitrary '1' at the beginning of the string to allow for leading zeros
  of the first PK.

* The application designer has to determine the maximum length of each Primary
  Key.

This statement can be saved as a view or the column can be added to the
database table, where it can be kept up to date with a database trigger.

Obviously the "view" method does generally not allow insert, updates or
deletes. For Postgresql you may want to consult the chapter "RULES" for
manipulating underlying tables.

For an alphanumeric Primary Key column a similar method is possible:

Every character of the lpaded PK has to be transfered using ascii(character)
which returns a 3digit number which can be concatenated as shown above.

Caveats:

* this way the ``id`` may become a very large integer number which may cause
  troubles elsewhere.

* no performance loss takes place if the where clauses specifies the PK
  columns.

Example: CD-Album
* Album: PK=ean
* Tracks: PK=ean,disc_nr,track_nr

The database view to show the tracks starts:

  SELECT ean||lpad("disc_nr",2,'0')||lpad("track_nr",2,'0') as id,  ...
  Note: no leading '1' and no padding necessary for ean numbers

Tracks.select(Tracks.q.ean==id) ... where id is the ean of the Album.

Changing the Naming Style
-------------------------

By default names in SQLObject are expected to be mixed case in Python
(like ``mixedCase``), and underscore-separated in SQL (like
``mixed_case``).  This applies to table and column names.  The primary
key is assumed to be simply ``id``.

Other styles exist.  A typical one is mixed case column names, and a
primary key that includes the table name, like ``ProductID``.  You can
use a different `Style` object to indicate a different naming
convention.  For instance::

    class Person(SQLObject):
        class sqlmeta:
            style = MixedCaseStyle(longID=True)
        firstName = StringCol()
        lastName = StringCol()

If you use ``Person.createTable()``, you'll get::

    CREATE TABLE Person (
        PersonID INT PRIMARY KEY,
        FirstName Text,
        LastName Text
    )

The `MixedCaseStyle` object handles the initial capitalization of
words, but otherwise leaves them be.  By using ``longID=True``, we
indicate that the primary key should look like a normal reference
(``PersonID`` for `MixedCaseStyle`, or ``person_id`` for the default
style).

If you wish to change the style globally, assign the style to the
connection, like::

    __connection__.style = MixedCaseStyle(longID=True)

Irregular Naming
----------------

This is now covered in the `Class sqlmeta`_ section.


Non-Integer Keys
----------------

While not strictly a legacy database issue, this fits into the category of
"irregularities".  If you use non-integer keys, all primary key management
is up to you.  You must create the table yourself (SQLObject can create
tables with int or str IDs), and when you create instances you must pass a
``id`` keyword argument into constructor
(like ``Person(id='555-55-5555', ...)``).

DBConnection: Database Connections
==================================

The `DBConnection` module currently has six external classes,
`MySQLConnection`, `PostgresConnection`, `SQLiteConnection`,
`SybaseConnection`, `MaxdbConnection`, `MSSQLConnection`.

You can pass the keyword argument `debug` to any connector.  If set to
true, then any SQL sent to the database will also be printed to the
console.

You can additionally pass `logger` keyword argument which should be a
name of the logger to use. If specified and `debug` is ``True``,
SQLObject will write debug print statements via that logger instead of
printing directly to console. The argument `loglevel` allows to choose
the logging level - it can be ``debug``, ``info``, ``warning``,
``error``, ``critical`` or ``exception``. In case `logger` is absent or
empty SQLObject uses ``print``'s instead of logging; `loglevel` can be
``stdout`` or ``stderr`` in this case; default is ``stdout``.

To configure logging one can do something like that::

    import logging
    logging.basicConfig(
        filename='test.log',
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        level=logging.DEBUG,
    )
    log = logging.getLogger("TEST")
    log.info("Log started")

    __connection__ = "sqlite:/:memory:?debug=1&logger=TEST&loglevel=debug"

The code redirects SQLObject debug messages to `test.log` file.

MySQL
-----

`MySQLConnection` takes the keyword arguments `host`, `port`, `db`, `user`,
and `password`, just like `MySQLdb.connect` does.

MySQLConnection supports all the features, though MySQL only supports
transactions_ when using the InnoDB backend; SQLObject can explicitly
define the backend using ``sqlmeta.createSQL``.

Supported drivers are ``mysqldb``, ``connector``, ``pymysql``,
``mariadb``, ``pyodbc``, ``pypyodbc`` or ``odbc`` (try ``pyodbc`` and
``pypyodbc``); default are ``mysqldb``, ``mysqlclient``,
``mysql-connector``, ``mysql-connector-python``, ``pymysql``.


Keyword argument ``conv`` allows to pass a list of custom converters.
Example::

    import time
    import sqlobject
    import MySQLdb.converters

    def _mysql_timestamp_converter(raw):
             """Convert a MySQL TIMESTAMP to a floating point number representing
             the seconds since the Un*x Epoch. It uses custom code the input seems
             to be the new (MySQL 4.1+) timestamp format, otherwise code from the
             MySQLdb module is used."""
             if raw[4] == '-':
                 return time.mktime(time.strptime(raw, '%Y-%m-%d %H:%M:%S'))
             else:
                 return MySQLdb.converters.mysql_timestamp_converter(raw)

    conversions = MySQLdb.converters.conversions.copy()
    conversions[MySQLdb.constants.FIELD_TYPE.TIMESTAMP] = _mysql_timestamp_converter

    MySQLConnection = sqlobject.mysql.builder()
    connection = MySQLConnection(user='foo', db='somedb', conv=conversions)

Connection-specific parameters are: ``unix_socket``, ``init_command``,
``read_default_file``, ``read_default_group``, ``conv``,
``connect_timeout``, ``compress``, ``named_pipe``, ``use_unicode``,
``client_flag``, ``local_infile``, ``ssl_key``, ``ssl_cert``,
``ssl_ca``, ``ssl_capath``, ``charset``.

Postgres
--------

`PostgresConnection` takes a single connection string, like
``"dbname=something user=some_user"``, just like `psycopg.connect`.
You can also use the same keyword arguments as for `MySQLConnection`,
and a dsn string will be constructed.

PostgresConnection supports transactions and all other features.

The user can choose a DB API driver for PostgreSQL by using a ``driver``
parameter in DB URI or PostgresConnection that can be a comma-separated
list of driver names. Possible drivers are: ``psycopg``, ``psycopg2``,
``pygresql``, ``pg8000``, ``pyodbc``, ``pypyodbc`` or ``odbc`` (try
``pyodbc`` and ``pypyodbc``). Default are ``psycopg``, ``psycopg2``,
``pygresql``.

Connection-specific parameters are: ``sslmode``, ``unicodeCols``,
``schema``, ``charset``.

SQLite
------

`SQLiteConnection` takes the a single string, which is the path to the
database file.

SQLite puts all data into one file, with a journal file that is opened
in the same directory during operation (the file is deleted when the
program quits).  SQLite does not restrict the types you can put in a
column -- strings can go in integer columns, dates in integers, etc.

SQLite may have concurrency issues, depending on your usage in a
multi-threaded environment.

Connection-specific parameters are: ``encoding``, ``mode``, ``timeout``,
``check_same_thread``, ``use_table_info``.

Firebird
--------

`FirebirdConnection` takes the arguments `host`, `db`, `user` (default
``"sysdba"``), `password` (default ``"masterkey"``).

Firebird supports all the features.  Support is still young, so there
may be some issues, especially with concurrent access, and especially
using lazy selects.  Try ``list(MyClass.select())`` to avoid
concurrent cursors if you have problems (using ``list()`` will
pre-fetch all the results of a select).

Firebird support ``fdb``, ``kinterbasdb`` or ``firebirdsql`` drivers.
Default are ``fdb`` and ``kinterbasdb``.

There could be a problem if one tries to connect to a server running on w32
from a program running on Unix; the problem is how to specify the database
so that SQLObject correctly parses it. Vertical bar is replaces by
a semicolon only on a w32. On Unix a vertical bar is a pretty normal
character and must not be processed.

The most correct way to fix the problem is to connect to the DB using
a database name, not a file name. In the Firebird a DBA can set an alias
instead of database name in the aliases.conf file

Example from `Firebird 2.0 Administrators Manual`_::

   # fbdb1 is on a Windows server:
   fbdb1 = c:\Firebird\sample\Employee.fdb

.. _`Firebird 2.0 Administrators Manual`: http://www.firebirdmanual.com/firebird/en/firebird-manual/2

Now a program can connect to firebird://host:port/fbdb1.

One can edit aliases.conf whilst the server is running. There is no need to
stop and restart the server in order for new aliases.conf entries to be
recognised.

If you are using indexes and get an error like *key size exceeds
implementation restriction for index*, see `this page`_ to understand
the restrictions on your indexing.

.. _this page: http://mujweb.cz/iprenosil/interbase/ip_ib_indexcalculator.htm

Connection-specific parameters are: ``dialect``, ``role``, ``charset``.

Sybase
------

`SybaseConnection` takes the arguments `host`, `db`, `user`, and
`password`.  It also takes the extra boolean argument `locking` (default
True), which is passed through when performing a connection.  You may
use a False value for `locking` if you are not using multiple threads,
for a slight performance boost.

It uses the Sybase_ module.

Connection-specific parameters are: ``locking``, ``autoCommit``.

MAX DB
------

MAX DB, also known as SAP DB, is available from a partnership of SAP
and MySQL.  It takes the typical arguments: `host`, `database`,
`user`, `password`.  It also takes the arguments `sqlmode` (default
``"internal"``), `isolation`, and `timeout`, which are passed through
when creating the connection to the database.

It uses the sapdb_ module.

Connection-specific parameters are: ``autoCommit``, ``sqlmode``,
``isolation``, ``timeout``.

MS SQL Server
-------------

The `MSSQLConnection` objects wants to use new style connection strings
in the format of

mssql://user:pass@host:port/db

This will then be mapped to either the correct driver format.  If running
SQL Server on a "named" port, make sure to specify the port number in the
URI.

The two drivers currently supported are adodbapi_ and pymssql_.

The user can choose a DB API driver for MSSQL by using a ``driver``
parameter in DB URI or MSSQLConnection that can be a comma-separated list
of driver names. Possible drivers are: ``adodb`` (alias ``adodbapi``) and
``pymssql``. Default is to test ``adodbapi`` and ``pymssql`` in that order.

Connection-specific parameters are: ``autoCommit``, ``timeout``.

Events (signals)
================

Signals are a mechanism to be notified when data or schema changes happen
through SQLObject. This may be useful for doing custom data validation,
logging changes, setting default attributes, etc. Some of what signals can
do is also possible by overriding methods, but signals may provide
a cleaner way, especially across classes not related by inheritance.

Example::

   from sqlobject.events import listen, RowUpdateSignal, RowCreatedSignal
   from model import Users

   def update_listener(instance, kwargs):
       """keep "last_updated" field current"""
       import datetime
       # BAD method 1, causes infinite recursion?
       # instance should be read-only
       instance.last_updated = datetime.datetime.now()
       # GOOD method 2
       kwargs['last_updated'] = datetime.datetime.now()

   def created_listener(instance, kwargs, post_funcs):
       """"email me when new users added"""
       # email() implementation left as an exercise for the reader
       msg = "%s just was just added to the database!" % kwargs['name']
       email(msg)

   listen(update_listener, Users, RowUpdateSignal)
   listen(created_listener, Users, RowCreatedSignal)

Exported Symbols
================

You can use ``from sqlobject import *``, though you don't have to.  It
exports a minimal number of symbols.  The symbols exported:

From `sqlobject.main`:

* `NoDefault`
* `SQLObject`
* `getID`
* `getObject`

From `sqlobject.col`:
* `Col`
* `StringCol`
* `IntCol`
* `FloatCol`
* `KeyCol`
* `ForeignKey`
* `EnumCol`
* `SetCol`
* `DateTimeCol`
* `DateCol`
* `TimeCol`
* `TimestampCol`
* `DecimalCol`
* `CurrencyCol`

From `sqlobject.joins`:
* `MultipleJoin`
* `RelatedJoin`

From `sqlobject.styles`:
* `Style`
* `MixedCaseUnderscoreStyle`
* `DefaultStyle`
* `MixedCaseStyle`

From `sqlobject.sqlbuilder`:

* `AND`
* `OR`
* `NOT`
* `IN`
* `LIKE`
* `DESC`
* `CONTAINSSTRING`
* `const`
* `func`

LEFT JOIN and other JOINs
-------------------------

First look in the FAQ_, question "How can I do a LEFT JOIN?"

Still here? Well. To perform a JOIN use one of the JOIN helpers from
SQLBuilder_. Pass an instance of the helper to .select()
method.  For example::

    from sqlobject.sqlbuilder import LEFTJOINOn
    MyTable.select(
        join=LEFTJOINOn(Table1, Table2,
                        Table1.q.name == Table2.q.value))

will generate the query::

    SELECT my_table.* FROM my_table, table1
    LEFT JOIN table2 ON table1.name = table2.value;

.. _FAQ: FAQ.html#how-can-i-do-a-left-join

If you want to join with the primary table - leave the first table
None::

    MyTable.select(
        join=LEFTJOINOn(None, Table1,
                        MyTable.q.name == Table1.q.value))

will generate the query::

    SELECT my_table.* FROM my_table
    LEFT JOIN table2 ON my_table.name = table1.value;

The join argument for .select() can be a JOIN() or a sequence (list/tuple)
of JOIN()s.

Available joins are JOIN, INNERJOIN, CROSSJOIN, STRAIGHTJOIN,
LEFTJOIN, LEFTOUTERJOIN, NATURALJOIN, NATURALLEFTJOIN, NATURALLEFTOUTERJOIN,
RIGHTJOIN, RIGHTOUTERJOIN, NATURALRIGHTJOIN, NATURALRIGHTOUTERJOIN,
FULLJOIN, FULLOUTERJOIN, NATURALFULLJOIN, NATURALFULLOUTERJOIN,
INNERJOINOn, LEFTJOINOn, LEFTOUTERJOINOn, RIGHTJOINOn, RIGHTOUTERJOINOn,
FULLJOINOn, FULLOUTERJOINOn, INNERJOINUsing, LEFTJOINUsing, LEFTOUTERJOINUsing,
RIGHTJOINUsing, RIGHTOUTERJOINUsing, FULLJOINUsing, FULLOUTERJOINUsing.

How can I join a table with itself?
-----------------------------------

Use Alias from SQLBuilder_. Example::

    from sqlobject.sqlbuilder import Alias
    alias = Alias(MyTable, "my_table_alias")
    MyTable.select(MyTable.q.name == alias.q.value)

will generate the query::

    SELECT my_table.* FROM my_table, my_table AS my_table_alias
    WHERE my_table.name = my_table_alias.value;

Can I use a JOIN() with aliases?
----------------------------------

Sure! That's a situation the JOINs and aliases were primary developed
for.  Code::

    from sqlobject.sqlbuilder import LEFTJOINOn, Alias
    alias = Alias(OtherTable, "other_table_alias")
    MyTable.select(MyTable.q.name == OtherTable.q.value,
        join=LEFTJOINOn(MyTable, alias, MyTable.col1 == alias.q.col2))

will result in the query::

    SELECT my_table.* FROM other_table,
        my_table LEFT JOIN other_table AS other_table_alias
    WHERE my_table.name == other_table.value AND
        my_table.col1 = other_table_alias.col2.

Subqueries (subselects)
-----------------------

You can run queries with subqueries (subselects) on those DBMS that can do
subqueries (MySQL supports subqueries from version 4.1).

Use corresponding classes and functions from SQLBuilder_::

    from sqlobject.sqlbuilder import EXISTS, Select
    select = Test1.select(EXISTS(Select(Test2.q.col2, where=(Outer(Test1).q.col1 == Test2.q.col2))))

generates the query::

   SELECT test1.id, test1.col1 FROM test1 WHERE
   EXISTS (SELECT test2.col2 FROM test2 WHERE (test1.col1 = test2.col2))

Note the usage of Outer - it is a helper to allow referring to a table in
the outer query.

Select() is used instead of .select() because you need to control what
columns the inner query returns.

Available queries are ``IN()``, ``NOTIN()``, ``EXISTS()``,
``NOTEXISTS()``, ``SOME()``, ``ANY()`` and ``ALL()``. The last 3 are
used with comparison operators, like this: ``somevalue = ANY(Select(...))``.

Utilities
---------

Some useful utility functions are included with SQLObject.  For more
information see their module docstrings.

* `sqlobject.util.csvexport <module-sqlobject.util.csvexport.html>`_

SQLBuilder
----------

For more information on SQLBuilder, read the `SQLBuilder
Documentation`_.

.. _SQLBuilder: SQLBuilder.html
.. _`SQLBuilder Documentation`: SQLBuilder.html

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
