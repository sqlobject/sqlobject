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

* Add ``driver`` keyword for FirebirdConnection. Allowed values are 'fdb'
  or 'kinterbasdb'. Default is to test 'fdb' and 'kinterbasdb' in that
  order. pyfirebirdsql is supported but untested.

* Add ``driver`` keyword for MySQLConnection. Allowed value are 'mysqldb',
  'connector', 'oursql' and 'pymysql'. Default is to test for mysqldb only;
  (connector, oursql and pymysql drivers still cause problems).

Drivers (work in progress)
--------------------------

* Add support for `MySQL Connector
  <https://pypi.python.org/pypi/mysql-connector>`_ (pure python; `binary
  packages <https://dev.mysql.com/doc/connector-python/en/>`_ are not at
  PyPI and hence are hard to install and test; most tests are passed, but
  there are still problems).

* Add support for `oursql <https://github.com/python-oursql/oursql>`_ MySQL
  driver (Python 2.6 and 2.7 until oursql fixes python 3 compatibility;
  most tests are passed, but there are still problems).

* Add support for `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_ - pure
  python mysql interface; most tests are passed, but there are still
  problems).

* Extend support for PyGreSQL driver. There are still some problems.

* Add support for `py-postgresql
  <https://pypi.python.org/pypi/py-postgresql>`_ PostgreSQL driver. There
  are still problems with the driver.

* Add support for `pg8000 <https://pypi.python.org/pypi/pg8000>`_
  PostgreSQL driver. There are still some problems.

* Add support for `pyfirebirdsql
  <https://pypi.python.org/pypi/firebirdsql>`_ (untested).

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

* Tests are now run at CIs with ``python3.5``.

* Tests are split at ``Circle CI`` in 4 parallel containers.

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
