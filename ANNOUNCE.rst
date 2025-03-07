Hello!

I'm pleased to announce version 3.13.0, the first release of branch
3.13 of SQLObject.


What's new in SQLObject
=======================

Drivers
-------

* Extended default list of MySQL drivers to ``mysqldb``, ``mysqlclient``,
  ``mysql-connector``, ``mysql-connector-python``, ``pymysql``.

* Extended default list of PostgreSQL drivers to ``psycopg``, ``psycopg2``,
  ``pygresql``, ``pg8000``.

* Fixed outstanding problems with ``psycopg``. It's now the first class driver.

* Fixed all problems with ``pg8000``. It's now the first class driver.

* Dropped support for ``CyMySQL``;
  its author refused to fix unicode-related problems.

* Dropped support for ``py-postgresql``; it's completely broken
  with debianized ``Postgres`` and the authors reject fixes.

Tests
-----

* Added tests for ``mysqldb`` (aka ``mysql-python``)
  and ``mysqlclient`` on w32.

* Improved tests of ``mysql-connector`` and ``mysql-connector-python``.

CI
--

* Tests(GHActions): Fixed old bugs in the workflow on w32.

* Run tests with ``psycopg[c]``.


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
https://pypi.org/project/SQLObject/3.13.0

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
