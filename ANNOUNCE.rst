Hello!

I'm pleased to announce version 3.9.1, the first minor feature release
of branch 3.9 of SQLObject.


What's new in SQLObject
=======================

Drivers
-------

* Adapt to the latest ``pg8000``.

* Protect ``getuser()`` - it can raise ``ImportError`` on w32
  due to absent of ``pwd`` module.

Build
-----

* Change URLs for ``oursql`` in ``extras_require`` in ``setup.py``.
  Provide separate URLs for Python 2.7 and 3.4+.

* Add ``mariadb`` in ``extras_require`` in ``setup.py``.

CI
--

* For tests with Python 3.4 run ``tox`` under Python 3.5.

Tests
-----

* Refactor ``tox.ini``.

For a more complete list, please see the news:
http://sqlobject.org/News.html


What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described
as classes, and rows are instances of those classes.  SQLObject is meant to be
easy to use and quick to get started with.

SQLObject supports a number of backends: MySQL, PostgreSQL, SQLite;
connections to other backends - Firebird, Sybase, MSSQL
and MaxDB (also known as SAPDB) - are lesser debugged).

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
https://pypi.org/project/SQLObject/3.9.1

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
