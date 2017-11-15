Hello!

I'm pleased to announce version 3.5.0, the first stable release of branch
3.5 of SQLObject.


What's new in SQLObject
=======================

Contributors for this release are Shailesh Mungikar and Michael S. Root.

Minor features
--------------

* Add Python3 special methods for division to SQLExpression.
  Pull request by Michael S. Root.

Drivers
-------

* Add support for `pg8000 <https://pypi.python.org/pypi/pg8000>`_
  PostgreSQL driver.

* Fix autoreconnect with pymysql driver. Contributed by Shailesh Mungikar.

Documentation
-------------

* Remove generated HTML from eggs/wheels (docs are installed into wrong
  place). Generated docs are still included in the source distribution.

Tests
-----

* Add tests for PyGreSQL, py-postgresql and pg8000 at AppVeyor.

* Fixed bugs in py-postgresql at AppVeyor. SQLObject requires
  the latest version of the driver from our fork.

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
https://pypi.python.org/pypi/SQLObject/3.5.0

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
