Hello!

I'm pleased to announce version 3.8.0, the first stable release of branch
3.8 of SQLObject.


What's new in SQLObject
=======================

Features
--------

* Add driver ``supersqlite``. Not all tests are passing
  so the driver isn't added to the list of default drivers.

Minor features
--------------

* Improve sqlrepr'ing ``ALL/ANY/SOME()``: always put the expression
  at the right side of the comparison operation.

Bug fixes
---------

* Fixed a bug in cascade deletion/nullification.

* Fixed a bug in ``PostgresConnection.columnsFromSchema``:
  PostgreSQL 12 removed outdated catalog attribute
  ``pg_catalog.pg_attrdef.adsrc``.

* Fixed a bug working with microseconds in Time columns.

CI
--

* Run tests with Python 3.8 at Travis CI.

Contributors for this release are Andrew Trusty, Marco Sirabella and darix.

For a more complete list, please see the news:
http://sqlobject.org/News.html


What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described
as classes, and rows are instances of those classes.  SQLObject is meant to be
easy to use and quick to get started with.

SQLObject supports a number of backends: MySQL, PostgreSQL, SQLite,
Firebird, Sybase, MSSQL and MaxDB (also known as SAPDB).

Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Development:
http://sqlobject.org/devel/

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Download:
https://pypi.org/project/SQLObject/3.8.0

News and changes:
http://sqlobject.org/News.html

StackOverflow:
https://stackoverflow.com/questions/tagged/sqlobject


Example
=======

Create a simple class that wraps a table::

  >>> from sqlobject import *
  >>>
  >>> sqlhub.processConnection = connectionForURI('sqlite:/:memory:')
  >>>
  >>> class Person(SQLObject):
  ...     fname = StringCol()
  ...     mi = StringCol(length=1, default=None)
  ...     lname = StringCol()
  ...
  >>> Person.createTable()

Use the object::

  >>> p = Person(fname="John", lname="Doe")
  >>> p
  <Person 1 fname='John' mi=None lname='Doe'>
  >>> p.fname
  'John'
  >>> p.mi = 'Q'
  >>> p2 = Person.get(1)
  >>> p2
  <Person 1 fname='John' mi='Q' lname='Doe'>
  >>> p is p2
  True

Queries::

  >>> p3 = Person.selectBy(lname="Doe")[0]
  >>> p3
  <Person 1 fname='John' mi='Q' lname='Doe'>
  >>> pc = Person.select(Person.q.lname=="Doe").count()
  >>> pc
  1
