SQLObject 3.13.1
================

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
https://pypi.org/project/SQLObject/

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
