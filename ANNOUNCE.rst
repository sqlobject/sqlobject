Hello!

I'm pleased to announce version 3.4.1a1, the first alpha of the upcoming
release of branch 3.4 of SQLObject.

I'm pleased to announce version 3.4.1a2, the second alpha of the upcoming
release of branch 3.4 of SQLObject.

I'm pleased to announce version 3.4.1b1, the first beta of the upcoming
release of branch 3.4 of SQLObject.

I'm pleased to announce version 3.4.1rc1, the first release candidate
of the upcoming release of branch 3.4 of SQLObject.

I'm pleased to announce version 3.4.0, the first stable release of branch
3.4 of SQLObject.

I'm pleased to announce version 3.4.1, the first bugfix release of branch
3.4 of SQLObject.


What's new in SQLObject
=======================

Contributors for this release are Shailesh Mungikar, Michael S. Root.

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
https://pypi.python.org/pypi/SQLObject/3.4.1a0.dev20170805

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
