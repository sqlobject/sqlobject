Hello!

I'm pleased to announce version 3.10.0, the first release of branch
3.10 of SQLObject.


What's new in SQLObject
=======================

Contributors for this release are
James Hudson, Juergen Gmach, Hugo van Kemenade.
Many thanks!

Features
--------

* Allow connections in ``ConnectionHub`` to be strings.
  This allows to open a new connection in every thread.

* Add compatibility with ``Pendulum``.

Tests
-----

* Run tests with Python 3.10.

CI
--

* GitHub Actions.

* Stop testing at Travis CI.

* Stop testing at AppVeyor.

Documentation
-------------

* DevGuide: source code must be pure ASCII.

* DevGuide: ``reStructuredText`` format for docstrings is recommended.

* DevGuide: de-facto good commit message format is required:
  subject/body/trailers.

* DevGuide: ``conventional commit`` format for commit message subject lines
  is recommended.

* DevGuide: ``Markdown`` format for commit message bodies is recommended.

* DevGuide: commit messages must be pure ASCII.

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
https://pypi.org/project/SQLObject/3.10.0

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
