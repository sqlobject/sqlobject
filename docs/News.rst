++++
News
++++

.. contents:: Contents:
   :backlinks: none

SQLObject 3.9.1
===============

Released 2021 Feb 27.

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

SQLObject 3.9.0
===============

Released 2020 Dec 15.

Features
--------

* Add ``JSONCol``: a universal json column that converts simple Python objects
  (None, bool, int, float, long, dict, list, str/unicode to/from JSON using
  json.dumps/loads. A subclass of StringCol. Requires ``VARCHAR``/``TEXT``
  columns at backends, doesn't work with ``JSON`` columns.

* Extend/fix support for ``DateTime`` from ``Zope``.

* Drop support for very old version of ``mxDateTime``
  without ``mx.`` namespace.

Drivers
-------

* Support `mariadb <https://pypi.org/project/mariadb/>`_.

CI
--

* Run tests with Python 3.9 at Travis and AppVeyor.

SQLObject 3.8.1
===============

Released 2020 Oct 01.

Documentation
-------------

* Use conf.py options to exclude sqlmeta options.

Tests
-----

* Fix ``PyGreSQL`` version for Python 3.4.

CI
--

* Run tests with Python 3.8 at AppVeyor.

SQLObject 3.8.0
===============

Released 7 Dec 2019.

Features
--------

* Add driver ``supersqlite``. Not all tests are passing
  so the driver isn't added to the list of default drivers.

Minor features
--------------

* Improve sqlrepr'ing ``ALL/ANY/SOME()``: always put the expression
  at the right side of the comparison operation.

Bug fixes
---------

* Fixed a bug in cascade deletion/nullification.

* Fixed a bug in ``PostgresConnection.columnsFromSchema``:
  PostgreSQL 12 removed outdated catalog attribute
  ``pg_catalog.pg_attrdef.adsrc``.

* Fixed a bug working with microseconds in Time columns.

CI
--

* Run tests with Python 3.8 at Travis CI.

SQLObject 3.7.3
===============

Released 22 Sep 2019.

Bug fixes
---------

* Avoid excessive parentheses around ``ALL/ANY/SOME()``.

Tests
-----

* Add tests for cascade deletion.

* Add tests for ``sqlbuilder.ALL/ANY/SOME()``.

* Fix calls to ``pytest.mark.skipif`` - make conditions bool instead of str.

* Fix module-level calls to ``pytest.mark.skip`` - add reasons.

* Fix escape sequences ``'\%'`` -> ``'\\%'``.

CI
--

* Reduce the number of virtual machines/containers:
  one OS, one DB, one python version, many drivers per VM.

* Fix sqlite test under Python 3.7+ at AppVeyor.

SQLObject 3.7.2
===============

Released 1 May 2019.

Minor features
--------------

* Adapt Postgres exception handling to ``psycopg2`` version ``2.8``:
  in the recent ``psycopg2`` errors are in ``psycopg2.errors`` module.

* Removed RdbhostConnection: David Keeney and rdbhost seem to be unavailable
  since 2017.

SQLObject 3.7.1
===============

Released 2 Feb 2019.

Bug fixes
---------

* Fixed a unicode problem in the latest mysqlclient.

Documentation
-------------

* Exclude sqlmeta members from some of the api docs.
  The inclusion of of these sqlmeta members in these files breaks
  reproducible builds.

Development
-----------

* Source code was made flake8-clean using the latest flake8.

CI
--

* Run tests with Python 3.7.

SQLObject 3.7.0
===============

Released 6 June 2018.

Features
--------

* Add signals on commit and rollback; pull request by Scott Stahl.

Bug fixes
---------

* Fix SSL-related parameters for MySQL-connector (connector uses
  a different param style). Bug reported by Christophe Popov.

Drivers
-------

* Remove psycopg1. Driver ``psycopg`` is now just an alias for ``psycopg2``.

Tests
-----

* Install psycopg2 from `psycopg2-binary`_ package.

.. _`psycopg2-binary`: https://pypi.org/project/psycopg2-binary/

SQLObject 3.6.0
===============

Released 24 Feb 2018.

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

SQLObject 3.5.0
===============

Released 15 Nov 2017.

Minor features
--------------

* Add Python3 special methods for division to SQLExpression.
  Pull request by Michael S. Root.

Drivers
-------

* Add support for `pg8000 <https://pypi.org/project/pg8000/>`_
  PostgreSQL driver.

* Fix autoreconnect with pymysql driver. Contributed by Shailesh Mungikar.

Documentation
-------------

* Remove generated HTML from eggs/wheels (docs are installed into wrong
  place). Generated docs are still included in the source distribution.

Tests
-----

* Add tests for PyGreSQL, py-postgresql and pg8000 at AppVeyor.

* Fixed bugs in py-postgresql at AppVeyor. SQLObject requires
  the latest version of the driver from our fork.

SQLObject 3.4.0
===============

Released 5 Aug 2017.

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

SQLObject 3.3.0
===============

Released 7 May 2017.

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

SQLObject 3.2.0
===============

Released 11 Mar 2017.

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
  <https://pypi.org/project/mysql-connector/>`_ (pure python; `binary
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
  <https://pypi.org/project/py-postgresql/>`_ PostgreSQL driver. There
  are still problems with the driver.

* Add support for `pyfirebirdsql
  <https://pypi.org/project/firebirdsql/>`_.There are still problems with
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
