Hello!

I'm pleased to announce version 3.10.3, the 3rd bugfix release of branch
3.10 of SQLObject.


What's new in SQLObject
=======================

The contributors for this release are
Igor Yudytskiy and shuffle (github.com/shuffleyxf).
Thanks!

Bug fixes
---------

* Relaxed aliasing in ``SQLRelatedJoin`` introduced in 3.10.2 - aliasing
  is required only when the table joins with itself. When there're two
  tables to join aliasing prevents filtering -- wrong SQL is generated
  in ``relJoinCol.filter(thisClass.q.column)``.

Drivers
-------

* Fix(SQLiteConnection): Release connections from threads that are
  no longer active. This fixes memory leak in multithreaded programs
  in Windows.

  ``SQLite`` requires different connections per thread so
  ``SQLiteConnection`` creates and stores a connection per thread.
  When a thread finishes its connections should be closed.
  But if a program doesn't cooperate and doesn't close connections at
  the end of a thread SQLObject leaks memory as connection objects are
  stuck in ``SQLiteConnection``. On Linux the leak is negligible as
  Linux reuses thread IDs so new connections replace old ones and old
  connections are garbage collected. But Windows doesn't reuse thread
  IDs so old connections pile and never released. To fix the problem
  ``SQLiteConnection`` now enumerates threads and releases connections
  from non-existing threads.

* Dropped ``supersqlite``. It seems abandoned.
  The last version 0.0.78 was released in 2018.

Tests
-----

* Run tests with Python 3.12.

CI
--

* GHActions: Ensure ``pip`` only if needed

  This is to work around a problem in conda with Python 3.7 -
  it brings in wrong version of ``setuptools`` incompatible with Python 3.7.

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
https://pypi.org/project/SQLObject/3.10.3

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
