Hello!

I'm pleased to announce version 3.12.1a1, the first alpha of the upcoming
release of branch 3.12 of SQLObject.

I'm pleased to announce version 3.12.1a2, the second alpha of the upcoming
release of branch 3.12 of SQLObject.

I'm pleased to announce version 3.12.1b1, the first beta of the upcoming
release of branch 3.12 of SQLObject.

I'm pleased to announce version 3.12.1rc1, the first release candidate
of the upcoming release of branch 3.12 of SQLObject.

I'm pleased to announce version 3.12.1, the first bugfix release of branch
3.12 of SQLObject.


What's new in SQLObject
=======================

The contributors for this release are ... Thanks!


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
https://pypi.org/project/SQLObject/3.12.1a0.dev20250201/

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
