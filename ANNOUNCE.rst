Hello!

I'm pleased to announce version 3.12.0.post1, the first post-release
of release 3.12.0 of branch 3.12 of SQLObject.


What's new in SQLObject
=======================

Drivers
-------

* Add support for CyMySQL; there're some problems with unicode yet.

* Separate ``psycopg`` and ``psycopg2``;
  ``psycopg`` is actually ``psycopg3`` now; not all tests pass.

* Minor fix in getting error code from PyGreSQL.

* Dropped ``oursql``. It wasn't updated in years.

* Dropped ``PySQLite2``. Only builtin ``sqlite3`` is supported.

Tests
-----

* Run tests with Python 3.13.

* Run tests with ``psycopg-c``; not all tests pass.

* Fix ``test_exceptions.py`` under MariaDB, PostgreSQL and SQLite.

* ``py-postgres``: Set ``sslmode`` to ``allow``;
  upstream changed default to ``prefer``.

CI
--

* Run tests with ``PyGreSQL`` on w32, do not ignore errors.

* Skip tests with ``pg8000`` on w32.

* GHActions: Switch to ``setup-miniconda``.

* GHActions: Python 3.13.

Build/release
-------------

* Release only sdist: wheels do not allow direct links for dependencies.


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
partially ``pg8000`` and ``py-postgresql``), SQLite (builtin ``sqlite3``);
connections to other backends
- Firebird, Sybase, MSSQL and MaxDB (also known as SAPDB) - are less
debugged).

Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Download:
https://pypi.org/project/SQLObject/3.12.0.post1

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
