Hello!

I'm pleased to announce version 3.6.0, the first stable release of branch
3.6 of SQLObject.


What's new in SQLObject
=======================

Contributor for this release is Michael S. Root.

Minor features
--------------

* Close cursors after using to free resources immediately
  instead of waiting for gc.

Bug fixes
---------

* Fix for TypeError using selectBy on a BLOBCol. PR by Michael S. Root.

Drivers
-------

* Extend support for oursql and Python 3 (requires our fork of the driver).

* Fix cursor.arraysize - pymssql doesn't have arraysize.

* Set timeout for ODBC with MSSQL.

* Fix _setAutoCommit for MSSQL.

Documentation
-------------

* Document extras that are available for installation.

Build
-----

* Use ``python_version`` environment marker in ``setup.py`` to make
  ``install_requires`` and ``extras_require`` declarative. This makes
  the universal wheel truly universal.

* Use ``python_requires`` keyword in ``setup.py``.

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
https://pypi.python.org/pypi/SQLObject/3.6.0

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
