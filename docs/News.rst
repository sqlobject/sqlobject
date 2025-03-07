++++
News
++++

.. contents:: Contents:
   :backlinks: none

SQLObject 3.13.0
================

Released 2025 Mar 07.

Drivers
-------

* Extended default list of MySQL drivers to ``mysqldb``, ``mysqlclient``,
  ``mysql-connector``, ``mysql-connector-python``, ``pymysql``.

* Extended default list of PostgreSQL drivers to ``psycopg``, ``psycopg2``,
  ``pygresql``, ``pg8000``.

* Fixed outstanding problems with ``psycopg``. It's now the first class driver.

* Fixed all problems with ``pg8000``. It's now the first class driver.

* Dropped support for ``CyMySQL``;
  its author refused to fix unicode-related problems.

* Dropped support for ``py-postgresql``; it's completely broken
  with debianized ``Postgres`` and the authors reject fixes.

Tests
-----

* Added tests for ``mysqldb`` (aka ``mysql-python``)
  and ``mysqlclient`` on w32.

* Improved tests of ``mysql-connector`` and ``mysql-connector-python``.

CI
--

* Tests(GHActions): Fixed old bugs in the workflow on w32.

* Run tests with ``psycopg[c]``.

SQLObject 3.12.0.post2
======================

Released 2025 Feb 01.

Installation/dependencies
-------------------------

* Use ``FormEncode`` 2.1.1 for Python 3.13.

SQLObject 3.12.0
================

Released 2024 Dec 20.

Drivers
-------

* Add support for CyMySQL; there're some problems with unicode yet.

* Separate ``psycopg`` and ``psycopg2``;
  ``psycopg`` is actually ``psycopg3`` now; not all tests pass.

* Minor fix in getting error code from PyGreSQL.

* Dropped ``oursql``. It wasn't updated in years.

* Dropped ``PySQLite2``. Only builtin ``sqlite3`` is supported.

Tests
-----

* Run tests with Python 3.13.

* Run tests with ``psycopg-c``; not all tests pass.

* Fix ``test_exceptions.py`` under MariaDB, PostgreSQL and SQLite.

* ``py-postgres``: Set ``sslmode`` to ``allow``;
  upstream changed default to ``prefer``.

CI
--

* Run tests with ``PyGreSQL`` on w32, do not ignore errors.

* Skip tests with ``pg8000`` on w32.

* GHActions: Switch to ``setup-miniconda``.

* GHActions: Python 3.13.

SQLObject 3.11.0
================

Released 2023 Nov 11.

Features
--------

* Continue working on ``SQLRelatedJoin`` aliasing introduced in 3.10.2.
  When a table joins with itself calling
  ``relJoinCol.filter(thisClass.q.column)`` raises ``ValueError``
  hinting that an alias is required for filtering.

* Test that ``idType`` is either ``int`` or ``str``.

* Added ``sqlmeta.idSize``. This sets the size of integer column ``id``
  for MySQL and PostgreSQL. Allowed values are ``'TINY'``, ``'SMALL'``,
  ``'MEDIUM'``, ``'BIG'``, ``None``; default is ``None``. For Postgres
  mapped to ``smallserial``/``serial``/``bigserial``. For other backends
  it's currently ignored. Feature request by Meet Gujrathi at
  https://stackoverflow.com/q/77360075/7976758

SQLObject 3.10.3
================

Released 2023 Oct 25.

Bug fixes
---------

* Relaxed aliasing in ``SQLRelatedJoin`` introduced in 3.10.2 - aliasing
  is required only when the table joins with itself. When there're two
  tables to join aliasing prevents filtering -- wrong SQL is generated
  in ``relJoinCol.filter(thisClass.q.column)``.

Drivers
-------

* Fix(SQLiteConnection): Release connections from threads that are
  no longer active. This fixes memory leak in multithreaded programs
  in Windows.

  ``SQLite`` requires different connections per thread so
  ``SQLiteConnection`` creates and stores a connection per thread.
  When a thread finishes its connections should be closed.
  But if a program doesn't cooperate and doesn't close connections at
  the end of a thread SQLObject leaks memory as connection objects are
  stuck in ``SQLiteConnection``. On Linux the leak is negligible as
  Linux reuses thread IDs so new connections replace old ones and old
  connections are garbage collected. But Windows doesn't reuse thread
  IDs so old connections pile and never released. To fix the problem
  ``SQLiteConnection`` now enumerates threads and releases connections
  from non-existing threads.

* Dropped ``supersqlite``. It seems abandoned.
  The last version 0.0.78 was released in 2018.

Tests
-----

* Run tests with Python 3.12.

CI
--

* GHActions: Ensure ``pip`` only if needed

  This is to work around a problem in conda with Python 3.7 -
  it brings in wrong version of ``setuptools`` incompatible with Python 3.7.

SQLObject 3.10.2
================

Released 2023 Aug 09.

Minor features
--------------

* Class ``Alias`` grows a method ``.select()`` to match ``SQLObject.select()``.

Bug fixes
---------

* Fixed a bug in ``SQLRelatedJoin`` in the case where the table joins with
  itself; in the resulting SQL two instances of the table must use different
  aliases.

CI
--

* Install all Python and PyPy versions from ``conda-forge``.

SQLObject 3.10.1
================

Released 2022 Dec 22.

Minor features
--------------

* Use ``module_loader.exec_module(module_loader.create_module())``
  instead of ``module_loader.load_module()`` when available.

Drivers
-------

* Added ``mysql-connector-python``.

Tests
-----

* Run tests with Python 3.11.

CI
--

* Ubuntu >= 22 and ``setup-python`` dropped Pythons < 3.7.
  Use ``conda`` via ``s-weigand/setup-conda`` instead of ``setup-python``
  to install older Pythons on Linux.

SQLObject 3.10.0
================

Released 2022 Sep 20.

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


`Older news`__

.. __: News6.html

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
