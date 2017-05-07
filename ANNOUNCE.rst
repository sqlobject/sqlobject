Hello!

I'm pleased to announce version 3.3.0, the first stable release of branch
3.3 of SQLObject.


What's new in SQLObject
=======================

Features
--------

* Support for Python 2.6 is declared obsolete and will be removed
  in the next release.

Minor features
--------------

* Convert scripts repository to devscripts subdirectory.
  Some of thses scripts are version-dependent so it's better to have them
  in the main repo.

* Test for __nonzero__ under Python 2, __bool__ under Python 3 in BoolCol.

Drivers (work in progress)
--------------------------

* Add support for PyODBC and PyPyODBC (pure-python ODBC DB API driver) for
  MySQL, PostgreSQL and MS SQL. Driver names are ``pyodbc``, ``pypyodbc``
  or ``odbc`` (try ``pyodbc`` and ``pypyodbc``). There are some problems
  with pyodbc and many problems with pypyodbc.

Documentation
-------------

* Stop updating http://sqlobject.readthedocs.org/ - it's enough to have
  http://sqlobject.org/

Tests
-----

* Run tests at Travis CI and AppVeyor with Python 3.6, x86 and x64.

* Stop running tests at Travis with Python 2.6.

* Stop running tests at AppVeyor with pymssql - too many timeouts and
  problems.

For a more complete list, please see the news:
http://sqlobject.org/News.html


What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described
as classes, and rows are instances of those classes.  SQLObject is meant to be
easy to use and quick to get started with.

SQLObject supports a number of backends: MySQL, PostgreSQL, SQLite,
Firebird, Sybase, MSSQL and MaxDB (also known as SAPDB).

Python 2.6, 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Development:
http://sqlobject.org/devel/

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Download:
https://pypi.python.org/pypi/SQLObject/3.3.0

News and changes:
http://sqlobject.org/News.html
