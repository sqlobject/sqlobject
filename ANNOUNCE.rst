Hello!

I'm pleased to announce version 3.2.0, the first stable release of branch
3.2 of SQLObject.


What's new in SQLObject
=======================

Contributor for this release is Neil Muller.

Minor features
--------------

* Drop table name from ``VACUUM`` command in SQLiteConnection: SQLite
  doesn't vacuum a single table and SQLite 3.15 uses the supplied name as
  the name of the attached database to vacuum.

* Remove ``driver`` keyword from RdbhostConnection as it allows one driver
  ``rdbhdb``.

* Add ``driver`` keyword for FirebirdConnection. Allowed values are 'fdb',
  'kinterbasdb' and 'pyfirebirdsql'. Default is to test 'fdb' and
  'kinterbasdb' in that order. pyfirebirdsql is supported but has problems.

* Add ``driver`` keyword for MySQLConnection. Allowed values are 'mysqldb',
  'connector', 'oursql' and 'pymysql'. Default is to test for mysqldb only.

* Add support for `MySQL Connector
  <https://pypi.python.org/pypi/mysql-connector>`_ (pure python; `binary
  packages <https://dev.mysql.com/doc/connector-python/en/>`_ are not at
  PyPI and hence are hard to install and test).

* Add support for `oursql <https://github.com/python-oursql/oursql>`_ MySQL
  driver (only Python 2.6 and 2.7 until oursql author fixes Python 3
  compatibility).

* Add support for `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ - pure
  python mysql interface).

* Add parameter ``timeout`` for MSSQLConnection (usable only with pymssql
  driver); timeouts are in seconds.

* Remove deprecated ez_setup.py.

Drivers (work in progress)
--------------------------

* Extend support for PyGreSQL driver. There are still some problems.

* Add support for `py-postgresql
  <https://pypi.python.org/pypi/py-postgresql>`_ PostgreSQL driver. There
  are still problems with the driver.

* Add support for `pyfirebirdsql
  <https://pypi.python.org/pypi/firebirdsql>`_.There are still problems with
  the driver.

Bug fixes
---------

* Fix MSSQLConnection.columnsFromSchema: remove `(` and `)` from default
  value.

* Fix MSSQLConnection and SybaseConnection: insert default values into a table
  with just one IDENTITY column.

* Remove excessive NULLs from ``CREATE TABLE`` for MSSQL/Sybase.

* Fix concatenation operator for MSSQL/Sybase (it's ``+``, not ``||``).

* Fix MSSQLConnection.server_version() under Py3 (decode version to str).

Documentation
-------------

* The docs are now generated with Sphinx.

* Move ``docs/LICENSE`` to the top-level directory so that Github
  recognizes it.

Tests
-----

* Rename ``py.test`` -> ``pytest`` in tests and docs.

* Great Renaming: fix ``pytest`` warnings by renaming ``TestXXX`` classes
  to ``SOTestXXX`` to prevent ``pytest`` to recognize them as test classes.

* Fix ``pytest`` warnings by converting yield tests to plain calls: yield
  tests were deprecated in ``pytest``.

* Tests are now run at CIs with Python 3.5.

* Drop ``Circle CI``.

* Run at Travis CI tests with Firebird backend (server version 2.5;
  drivers fdb and firebirdsql). There are problems with tests.

* Run tests at AppVeyor for windows testing. Run tests with MS SQL,
  MySQL, Postgres and SQLite backends; use Python 2.7, 3.4 and 3.5,
  x86 and x64. There are problems with MS SQL and MySQL.

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

Archives:
http://news.gmane.org/gmane.comp.python.sqlobject

Download:
https://pypi.python.org/pypi/SQLObject/3.2.0

News and changes:
http://sqlobject.org/News.html
