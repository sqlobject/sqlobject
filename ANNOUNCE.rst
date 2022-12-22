Hello!

I'm pleased to announce version 3.10.1, the first minor feature release of
branch 3.10 of SQLObject.


What's new in SQLObject
=======================

Minor features
--------------

* Use ``module_loader.exec_module(module_loader.create_module())``
  instead of ``module_loader.load_module()`` when available.

Drivers
-------

* Added ``mysql-connector-python``.

Tests
-----

* Run tests with Python 3.11.

CI
--

* Ubuntu >= 22 and ``setup-python`` dropped Pythons < 3.7.
  Use ``conda`` via ``s-weigand/setup-conda`` instead of ``setup-python``
  to install older Pythons on Linux.

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
``PyMySQL``, ``mariadb``), PostgreSQL (``psycopg2``, ``PyGreSQL``,
partially ``pg8000`` and ``py-postgresql``), SQLite (builtin ``sqlite``,
``pysqlite``, partially ``supersqlite``); connections to other backends
- Firebird, Sybase, MSSQL and MaxDB (also known as SAPDB) - are less
debugged).

Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Download:
https://pypi.org/project/SQLObject/3.10.1

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
