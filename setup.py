#!/usr/bin/env python

import sys
from imp import load_source
from os.path import abspath, dirname, join

try:
    from setuptools import setup
    is_setuptools = True
except ImportError:
    from distutils.core import setup
    is_setuptools = False

versionpath = join(abspath(dirname(__file__)), "sqlobject", "__version__.py")
load_source("sqlobject_version", versionpath)
from sqlobject_version import version  # noqa: ignore flake8 E402

subpackages = ['firebird', 'include', 'include.tests',
               'inheritance', 'inheritance.tests',
               'manager', 'maxdb', 'mysql', 'mssql', 'postgres', 'rdbhost',
               'sqlite', 'sybase', 'tests', 'util',
               'versioning', 'versioning.test']

kw = {}
if is_setuptools:
    kw['entry_points'] = """
    [paste.filter_app_factory]
    main = sqlobject.wsgi_middleware:make_middleware
    """
    install_requires = []
    if (sys.version_info[0] == 2) and (sys.version_info[:2] >= (2, 6)):
        install_requires.append("FormEncode>=1.1.1,!=1.3.0")
    elif (sys.version_info[0] == 3) and (sys.version_info[:2] >= (3, 4)):
        install_requires.append("FormEncode>=1.3.1")
    else:
        raise ImportError("SQLObject requires Python 2.6, 2.7 or 3.4+")
    install_requires.append("PyDispatcher>=2.0.4")
    kw['install_requires'] = install_requires
    kw['extras_require'] = {
        'mysql': ['MySQLdb'],
        'postgresql': ['psycopg'],  # or pgdb from PyGreSQL
        'sqlite': ['pysqlite'],
        'firebird': ['fdb'],  # or kinterbasdb
        'sybase': ['Sybase'],
        'mssql': ['adodbapi'],  # or pymssql
        'sapdb': ['sapdb'],
    }

setup(name="SQLObject",
      version=version,
      description="Object-Relational Manager, aka database wrapper",
      long_description="""\
SQLObject is a popular *Object Relational Manager* for providing an
object interface to your database, with tables as classes, rows as
instances, and columns as attributes.

SQLObject includes a Python-object-based query language that makes SQL
more abstract, and provides substantial database independence for
applications.

Supports MySQL, PostgreSQL, SQLite, Firebird, Sybase, MSSQL and MaxDB (SAPDB).
Python 2.6, 2.7 or 3.4+ is required.

For development see the projects at
`SourceForge <https://sourceforge.net/projects/sqlobject/>`_
and `GitHub <https://github.com/sqlobject>`_.

.. image:: https://travis-ci.org/sqlobject/sqlobject.svg?branch=master
  :target: https://travis-ci.org/sqlobject/sqlobject
""",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: "
          "GNU Library or Lesser General Public License (LGPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Database",
          "Topic :: Database :: Front-Ends",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      maintainer="Oleg Broytman",
      maintainer_email="phd@phdru.name",
      url="http://sqlobject.org/devel/",
      download_url="https://pypi.python.org/pypi/SQLObject/%s" % version,
      license="LGPL",
      packages=["sqlobject"] +
          ['sqlobject.%s' % package for package in subpackages],
      scripts=["scripts/sqlobject-admin", "scripts/sqlobject-convertOldURI"],
      package_data={"sqlobject":
                    [
                        "../LICENSE",
                        "../docs/*.rst",
                        "../docs/html/*",
                        "../docs/html/_sources/*",
                        "../docs/html/_sources/api/*",
                        "../docs/html/_modules/*",
                        "../docs/html/_modules/sqlobject/*",
                        "../docs/html/_modules/sqlobject/mysql/*",
                        "../docs/html/_modules/sqlobject/postgres/*",
                        "../docs/html/_modules/sqlobject/manager/*",
                        "../docs/html/_modules/sqlobject/inheritance/*",
                        "../docs/html/_modules/sqlobject/inheritance/tests/*",
                        "../docs/html/_modules/sqlobject/mssql/*",
                        "../docs/html/_modules/sqlobject/tests/*",
                        "../docs/html/_modules/sqlobject/rdbhost/*",
                        "../docs/html/_modules/sqlobject/versioning/*",
                        "../docs/html/_modules/sqlobject/versioning/test/*",
                        "../docs/html/_modules/sqlobject/util/*",
                        "../docs/html/_modules/sqlobject/maxdb/*",
                        "../docs/html/_modules/sqlobject/firebird/*",
                        "../docs/html/_modules/sqlobject/sybase/*",
                        "../docs/html/_modules/sqlobject/sqlite/*",
                        "../docs/html/_modules/sqlobject/include/*",
                        "../docs/html/_modules/sqlobject/include/tests/*",
                        "../docs/html/_modules/pydispatch/*",
                        "../docs/html/_modules/_pytest/*",
                        "../docs/html/api/*",
                        "../docs/html/_static/*",
                    ],
                    "sqlobject.maxdb": ["readme.txt"],
                    },
      requires=['FormEncode', 'PyDispatcher'],
      **kw
      )

# Send announce to:
#   sqlobject-discuss@lists.sourceforge.net
#   python-announce@python.org
#   python-list@python.org
#   db-sig@python.org

# Email tempate:
"""
@@ INTRO


What's new in SQLObject
=======================

@@ CHANGES

For a more complete list, please see the news:
http://sqlobject.org/docs/News.html


What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described
as classes, and rows are instances of those classes.  SQLObject is meant to be
easy to use and quick to get started with.

It currently supports MySQL through the `MySQLdb` package, PostgreSQL
through the `psycopg` package, SQLite, Firebird, MaxDB (SAP DB), MS SQL
Sybase and Rdbhost.  Python 2.6, 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Archives:
http://news.gmane.org/gmane.comp.python.sqlobject

Download:
https://pypi.python.org/pypi/SQLObject/@@

News and changes:
http://sqlobject.org/docs/News.html

-- 
Ian Bicking  /  ianb@colorstudy.com  / http://blog.ianbicking.org
"""  # noqa: preserve space after two dashes
