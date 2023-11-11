Hello!

I'm pleased to announce version 3.11.0, the first stable release
of branch 3.11 of SQLObject.


What's new in SQLObject
=======================

Features
--------

* Continue working on ``SQLRelatedJoin`` aliasing introduced in 3.10.2.
  When a table joins with itself calling
  ``relJoinCol.filter(thisClass.q.column)`` raises ``ValueError``
  hinting that an alias is required for filtering.

* Test that ``idType`` is either ``int`` or ``str``.

* Added ``sqlmeta.idSize``. This sets the size of integer column ``id``
  for MySQL and PostgreSQL. Allowed values are ``'TINY'``, ``'SMALL'``,
  ``'MEDIUM'``, ``'BIG'``, ``None``; default is ``None``. For Postgres
  mapped to ``smallserial``/``serial``/``bigserial``. For other backends
  it's currently ignored. Feature request by Meet Gujrathi at
  https://stackoverflow.com/q/77360075/7976758

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
``pysqlite``); connections to other backends
- Firebird, Sybase, MSSQL and MaxDB (also known as SAPDB) - are less
debugged).

Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Download:
https://pypi.org/project/SQLObject/3.11.0

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
