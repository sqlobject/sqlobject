Download SQLObject
++++++++++++++++++

The latest releases are always available on the `Python Package Index
<https://pypi.org/project/SQLObject/>`_, and is installable
with `pip <https://pip.pypa.io/en/latest/>`_ or `easy_install
<https://setuptools.readthedocs.io/en/latest/easy_install.html>`_.

You can install the latest release with::

  pip install -U SQLObject

or::

  easy_install -U SQLObject

You can install the latest version of SQLObject with::

  easy_install SQLObject==dev

You can install the latest bug fixing branch with::

  easy_install SQLObject==bugfix

If you want to require a specific revision (because, for instance, you
need a bugfix that hasn't appeared in a release), you can put this in
your `setuptools
<https://setuptools.readthedocs.io/en/latest/index.html>`_ using
``setup.py`` file::

  setup(...
    install_requires=["SQLObject==bugfix,>=0.7.1dev-r1485"],
  )

This says that you *need* revision 1485 or higher.  But it also says
that you can aquire the "bugfix" version to try to get that.  In fact,
when you install ``SQLObject==bugfix`` you will be installing a
specific version, and "bugfix" is just a kind of label for a way of
acquiring the version (it points to a branch in the repository).

Drivers
-------

SQLObject can be used with a number of drivers_. They can be installed
separately but it's also possible to install them with ``pip install``,
for example ``pip install SQLObject[mysql]`` or
``pip install SQLObject[postgres]``. The following drivers are
available:

.. _drivers: SQLObject.html#requirements

Firebird/Interbase
^^^^^^^^^^^^^^^^^^

fdb firebirdsql kinterbasdb

MS SQL
^^^^^^

adodbapi pymssql

MySQL
^^^^^

mysql (installs MySQL-python for Python 2.7 and mysqlclient for Python 3.4+)
mysql-connector pymysql mariadb

ODBC
^^^^

pyodbc pypyodbc odbc (synonym for pyodbc)

PostgreSQL
^^^^^^^^^^

psycopg psycopg2 postgres postgresql (synonyms for psycopg2)
pygresql pg8000

The rest
^^^^^^^^

sapdb sybase

Repositories
------------

The SQLObject `git <https://git-scm.com/>`_ repositories are located at
https://github.com/sqlobject and
https://sourceforge.net/p/sqlobject/_list/git

Before switching to git development was performed at the Subversion
repository that is no longer available.

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
