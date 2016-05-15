#!/usr/bin/env python

from imp import load_source
from os.path import abspath, dirname, join

try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
    is_setuptools = True
except ImportError:
    from distutils.core import setup
    is_setuptools = False

versionpath = join(abspath(dirname(__file__)), "sqlobject", "__version__.py")
load_source("sqlobject_version", versionpath)
from sqlobject_version import version  # noqa: ignore flake8 E402

subpackages = ['firebird', 'include',
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
    kw['install_requires'] = ["FormEncode>=1.1.1", "PyDispatcher>=2.0.4"]
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
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: "
          "GNU Library or Lesser General Public License (LGPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
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
                        "../docs/LICENSE", "../docs/*.txt", "../docs/*.css",
                        "../docs/html/*.html", "../docs/html/*.css",
                        "../docs/html/sqlobject/*.html",
                        "../docs/html/sqlobject/firebird/*.html",
                        "../docs/html/sqlobject/include/*.html",
                        "../docs/html/sqlobject/inheritance/*.html",
                        "../docs/html/sqlobject/manager/*.html",
                        "../docs/html/sqlobject/maxdb/*.html",
                        "../docs/html/sqlobject/mssql/*.html",
                        "../docs/html/sqlobject/mysql/*.html",
                        "../docs/html/sqlobject/postgres/*.html",
                        "../docs/html/sqlobject/rdbhost/*.html",
                        "../docs/html/sqlobject/sqlite/*.html",
                        "../docs/html/sqlobject/sybase/*.html",
                        "../docs/html/sqlobject/util/*.html",
                        "../docs/html/sqlobject/versioning/*.html",
                    ],
                    "sqlobject.maxdb": ["readme.txt"],
                    },
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
