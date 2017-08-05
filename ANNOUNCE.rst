Hello!

I'm pleased to announce version 3.4.0, the first stable release of branch
3.4 of SQLObject.


What's new in SQLObject
=======================

Contributor for this release is Dr. Neil Muller.

Features
--------

* Python 2.6 is no longer supported. The minimal supported version is
  Python 2.7.

Drivers (work in progress)
--------------------------

* Encode binary values for py-postgresql driver. This fixes the
  last remaining problems with the driver.

* Encode binary values for PyGreSQL driver using the same encoding as for
  py-postgresql driver. This fixes the last remaining problems with the driver.

  Our own encoding is needed because unescape_bytea(escape_bytea()) is not
  idempotent. See the comment for PQunescapeBytea at
  https://www.postgresql.org/docs/9.6/static/libpq-exec.html:

    This conversion is not exactly the inverse of PQescapeBytea, because the
    string is not expected to be "escaped" when received from PQgetvalue. In
    particular this means there is no need for string quoting considerations.

* List all drivers in extras_require in setup.py.

Minor features
--------------

* Use base64.b64encode/b64decode instead of deprecated
  encodestring/decodestring.

Tests
-----

* Fix a bug with sqlite-memory: rollback transaction and close connection.
  The solution was found by Dr. Neil Muller.

* Use remove-old-files.py from ppu to cleanup pip cache
  at Travis and AppVeyor.

* Add test_csvimport.py more as an example how to use load_csv
  from sqlobject.util.csvimport.

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
https://pypi.python.org/pypi/SQLObject/3.4.0

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
