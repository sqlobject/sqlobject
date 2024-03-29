TODO
----

* Fix unicode problems with pyodbc.

* Resolve timeout problems with MSSQL.

* PyPy.

* Use https://pypi.org/project/psycopg2cffi/ to run SQLObject
  under PyPy.

* https://pypi.org/project/turbodbc/

* PyODBC and PyPyODBC for linux and w32: SQLite (libsqliteodbc).

* https://pypi.org/project/JayDeBeApi/

* Jython.

* Quote table/column names that are reserved keywords (order => "order",
  values => `values` for MySQL).

* RelatedJoin.hasOther(otherObject[.id])

* createParamsPre/Post::

    class MyTable(SQLObject):
        class sqlmeta:
            createParamsPre = 'TEMPORARY IF NOT EXISTS'
            createParamsPre = {temporary: True, ifNotExists: True,
                               'postgres': 'LOCAL'}
            createParamsPost = 'ENGINE InnoDB'
            createParamsPost = {'mysql': 'ENGINE InnoDB',
                                'postgres': 'WITH OIDS'}

* SQLObject.fastInsert().

* IntervalCol

* TimedeltaCol

* Cached join results.

* Invert tests isinstance(obj, (tuple, list)) to not isinstance(obj,
  basestr) to allow any iterable.

* Always use .lazyIter().

* Optimize Iteration.next() - use cursor.fetchmany().

* Generators instead of loops (fetchall => fetchone).

* Cache columns in sqlmeta.getColumns(); reset the cache on add/del
  Column/Join.

* Make ConnectionHub a context manager instead of .doInTransaction().

* Make version_info a namedtuple.

* Expression columns - in SELECT but not in INSERT/UPDATE. Something like
  this::

    class MyClass(SQLObject):
        function1 = ExpressionCol(func.my_function(MyClass.q.col1))
        function2 = ExpressionCol('sum(col2)')

* A hierarchy of exceptions. SQLObject should translate exceptions from
  low-level drivers to a consistent set of high-level exceptions.

* Memcache.

* Refactor ``DBConnection`` to use parameterized queries instead of
  generating query strings.

* PREPARE/EXECUTE.

* Protect all .encode(), catch UnicodeEncode exceptions and reraise
  Invalid.

* More kinds of joins, and more powerful join results (closer to how
  `select` works).

* Better joins - automatic joins in .select() based on
  ForeignKey/MultipleJoin/RelatedJoin.

* Deprecate, then remove connectionForOldURI.

* Switch from setuptools to distribute.

* Support PyODBC driver for all backends.

* `dbms <https://pypi.org/project/dbms/>`_ is a DB API wrapper for DB
  API drivers for IBM DB2, Firebird, MSSQL Server, MySQL, Oracle,
  PostgreSQL, SQLite and ODBC.

* dict API: use getitem interface for column access instead of getattr;
  reserve getattr for internal attributes only; this helps to avoid
  collisions with internal attributes.

* Or move column values access to a separate namespace, e.g. .c:
  row.c.column.

* More documentation.

* RSS 2.0 and Atom news feeds.

* Use DBUtils_, especially SolidConnection.

.. _DBUtils: https://pypi.org/project/DBUtils/

* ``_fromDatabase`` currently doesn't support IDs that don't fit into the
  normal naming scheme.  It should do so.  You can still use ``_idName``
  with ``_fromDatabase``.

* More databases supported.  There has been interest and some work in the
  progress for Oracle. IWBN to have Informix and DB2 drivers.

* Better transaction support -- right now you can use transactions for the
  database, but objects aren't transaction-aware, so non-database
  persistence won't be able to be rolled back.

* Optimistic locking and other techniques to handle concurrency.

* Profile of SQLObject performance to identify bottlenecks.

* Increase hooks with FormEncode validation and form generation package, so
  SQLObject classes (read: schemas) can be published for editing more
  directly and easily.  (First step: get Schema-generating method into
  sqlmeta class)

* Merge SQLObject.create*, .create*SQL methods with DBPI.create* methods.

* Made SQLObject unicode-based instead of just unicode-aware. All internal
  processing should be done with unicode strings, conversion to/from ascii
  strings should happen for non-unicode DB API drivers.

* Allow to override ConsoleWriter/LogWriter classes and makeDebugWriter
  function.

* Type annotations and mypy tests.

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
