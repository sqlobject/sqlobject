++++
News
++++

.. contents:: Contents:
   :backlinks: none

.. _start:

SQLObject 3.2.0 (master)
========================

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

* Add ``driver`` keyword for MySQLConnection. Allowed value are 'mysqldb',
  'connector', 'oursql' and 'pymysql'. Default is to test for mysqldb only.

* Add support for `MySQL Connector
  <https://pypi.python.org/pypi/mysql-connector>`_ (pure python; `binary
  packages <https://dev.mysql.com/doc/connector-python/en/>`_ are not at
  PyPI and hence are hard to install and test).

* Add support for `oursql <https://github.com/python-oursql/oursql>`_ MySQL
  driver (Python 2.6 and 2.7 until oursql fixes python 3 compatibility).

* Add support for `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ - pure
  python mysql interface).

* Add parameter ``timeout`` for MSSQLConnection (usable only with pymssql
  driver); timeouts are in seconds.

Drivers (work in progress)
--------------------------

* Extend support for PyGreSQL driver. There are still some problems.

* Add support for `py-postgresql
  <https://pypi.python.org/pypi/py-postgresql>`_ PostgreSQL driver. There
  are still problems with the driver.

* Add support for `pg8000 <https://pypi.python.org/pypi/pg8000>`_
  PostgreSQL driver. There are major problems with the driver caused by both
  the driver and SQLObject.

* Add support for `pyfirebirdsql
  <https://pypi.python.org/pypi/firebirdsql>`_.There are still problems with
  the driver.

Bug fixes
---------

* Fix MSSQLConnection.columnsFromSchema: remove `(` and `)` from default
  value.

* Fix MSSQLConnection and SybaseConnection: insert default values into a table
  with just one IDENTITY column.

* Remove excessive NULLs for MSSQL/Sybase.

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

* Run at Travis CI tests with Firebird backend (server version 2.5; drivers fdb
  and firebirdsql). There are problems with tests.

* Add AppVeyor for windows testing. Run tests with MS SQL, Postgres and
  SQLite. There are problems with MS SQL.

SQLObject 3.1.0
===============

Released 16 Aug 2016.

Features
--------

* Add UuidCol.

* Add JsonbCol. Only for PostgreSQL.
  Requires psycopg2 >= 2.5.4 and PostgreSQL >= 9.2.

* Add JSONCol, a universal json column.

* For Python >= 3.4 minimal FormEncode version is now 1.3.1.

* If mxDateTime is in use, convert timedelta (returned by MySQL) to
  mxDateTime.Time.

Documentation
-------------

* Developer's Guide is extended to explain SQLObject architecture
  and how to create a new column type.

* Fix URLs that can be found; remove missing links.

* Rename reStructuredText files from \*.txt to \*.rst.

Source code
-----------

* Fix all `import *` using https://github.com/zestyping/star-destroyer.

Tests
-----

* Tests are now run at Circle CI.

* Use pytest-cov for test coverage. Report test coverage
  via coveralls.io and codecov.io.

* Install mxDateTime to run date/time tests with it.

SQLObject 3.0.0
===============

Released 1 Jun 2016.

Features
--------

* Support for Python 2 and Python 3 with one codebase!
  (Python version >= 3.4 currently required.)

Minor features
--------------

* PyDispatcher (>=2.0.4) was made an external dependency.

Development
-----------

* Source code was made flake8-clean.

Documentation
-------------

* Documentation is published at http://sqlobject.readthedocs.org/ in
  Sphinx format.

`Older news`__

.. __: News5.html

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
