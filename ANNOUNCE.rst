Hello!

I'm pleased to announce version 3.13.1, the first bugfix release of the
branch 3.13 of SQLObject.


What's new in SQLObject
=======================

The contributors for this release are:

* Igor Yudytskiy. Thanks for PR #194:
  fix: connect to old mssql versions via set tds_version uri parameter.

* Dave Mulligan fixed #195: Minor ``NameError`` in ``pgconnection.py``
  when using ``psycopg`` version 1 with a non-default port. Thanks!

* Chris Kauffman found a minor bug in ``UuidValidator``.

* GH user ghaushe-ampere. Thanks for finding an obscure bug!

Bug fixes
---------

* ``UuidValidator.from_python()`` now accepts strings as a valid input.
  This fixes #199.

* Fixed #197: a bug in ``dbconnection.ConnectionURIOpener.registerConnection``
  triggered by non-empty instance's ``name``. The bug was inserted in 2004 so
  it seems nobody ever used named instances. Fixed anyway.

* Fixed #195: Minor ``NameError`` in ``pgconnection.py``
  when using ``psycopg`` version 1 with a non-default port.

Tests
-----

* Tested with Python 3.14.

* Run tests with source-only (non-binary) ``psycopg`` and ``psycopg2``.

For a more complete list, please see the news:
http://sqlobject.org/News.html


What is SQLObject
=================

SQLObject is a free and open-source (LGPL) Python object-relational
mapper.  Your database tables are described as classes, and rows are
instances of those classes.  SQLObject is meant to be easy to use and
quick to get started with.

SQLObject supports a number of backends: MySQL/MariaDB (with a number of
DB API drivers: ``MySQLdb``, ``mysqlclient``, ``mysql-connector``,
``PyMySQL``, ``mariadb``), PostgreSQL (``psycopg``, ``psycopg2``, ``PyGreSQL``,
partially ``pg8000``), SQLite (builtin ``sqlite3``);
connections to other backends - Firebird, Sybase, MSSQL and MaxDB (also
known as SAPDB) - are less debugged).

Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Download:
https://pypi.org/project/SQLObject/3.13.1

News and changes:
http://sqlobject.org/News.html

StackOverflow:
https://stackoverflow.com/questions/tagged/sqlobject

Mailing lists:
https://sourceforge.net/p/sqlobject/mailman/

Development:
http://sqlobject.org/devel/

Developer Guide:
http://sqlobject.org/DeveloperGuide.html


Example
=======

Install::

  $ pip install sqlobject

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
