#!/usr/bin/env python

try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
    is_setuptools = True
except ImportError:
    from distutils.core import setup
    is_setuptools = False

subpackages = ['firebird', 'include', 'include.pydispatch', 'inheritance',
               'manager', 'maxdb', 'mysql', 'mssql', 'postgres', 'rdbhost',
               'sqlite', 'sybase', 'util', 'versioning']

kw = {}
if is_setuptools:
    kw['entry_points'] = """
    [paste.filter_app_factory]
    main = sqlobject.wsgi_middleware:make_middleware
    """

setup(name="SQLObject",
      version="1.1",
      description="Object-Relational Manager, aka database wrapper",
      long_description="""\
SQLObject is a popular *Object Relational Manager* for providing an
object interface to your database, with tables as classes, rows as
instances, and columns as attributes.

SQLObject includes a Python-object-based query language that makes SQL
more abstract, and provides substantial database independence for
applications.

Supports MySQL, PostgreSQL, SQLite, Firebird, Sybase, MSSQL and MaxDB (SAPDB).

For development see the `subversion repository
<http://svn.colorstudy.com/SQLObject/trunk#egg=SQLObject-1.1dev>`_
""",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://sqlobject.org/devel/",
      download_url="http://cheeseshop.python.org/pypi/SQLObject/1.1",
      license="LGPL",
      packages=["sqlobject"] + ['sqlobject.%s' % package for package in subpackages],
      scripts=["scripts/sqlobject-admin", "scripts/sqlobject-convertOldURI"],
      install_requires=["FormEncode>=1.1.1"],
      extras_require={
        'mysql': ['MySQLdb'],
        'postgresql': ['psycopg'], # or pgdb from PyGreSQL
        'sqlite': ['pysqlite'],
        'firebird': ['kinterbasdb'],
        'sybase': ['Sybase'],
        'mssql': ['adodbapi'], # or pymssql
        'sapdb': ['sapdb'],
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

What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described
as classes, and rows are instances of those classes.  SQLObject is meant to be
easy to use and quick to get started with.

It currently supports MySQL through the `MySQLdb` package, PostgreSQL
through the `psycopg` package, SQLite, Firebird, MaxDB (SAP DB), MS SQL
Sybase and Rdbhost.  It should support Python versions back to 2.4.

Where is SQLObject
==================

Site:
http://sqlobject.org

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Archives:
http://news.gmane.org/gmane.comp.python.sqlobject

Download:
http://cheeseshop.python.org/pypi/SQLObject/@@

News and changes:
http://sqlobject.org/docs/News.html


What's New
==========

@@ CHANGES

For a more complete list, please see the news:
http://sqlobject.org/docs/News.html

-- 
Ian Bicking  /  ianb@colorstudy.com  / http://blog.ianbicking.org
"""
