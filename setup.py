#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup
import sys

versionpath = join(abspath(dirname(__file__)), 'sqlobject', '__version__.py')
sqlobject_version = {}

if sys.version_info[:2] == (2, 7):
    execfile(versionpath, sqlobject_version)  # noqa: F821 'execfile' Py3

elif sys.version_info >= (3, 4):
    exec(open(versionpath, 'r').read(), sqlobject_version)

else:
    raise ImportError("SQLObject requires Python 2.7 or 3.4+")

subpackages = ['firebird', 'include', 'include.tests',
               'inheritance', 'inheritance.tests',
               'manager', 'maxdb', 'mysql', 'mssql', 'postgres',
               'sqlite', 'sybase', 'tests', 'util',
               'versioning', 'versioning.test']

setup(
    name="SQLObject",
    version=sqlobject_version['version'],
    description="Object-Relational Manager, aka database wrapper",
    long_description="""\
SQLObject is a popular *Object Relational Manager* for providing an
object interface to your database, with tables as classes, rows as
instances, and columns as attributes.

SQLObject includes a Python-object-based query language that makes SQL
more abstract, and provides substantial database independence for
applications.

Supports MySQL, PostgreSQL, SQLite, Firebird, Sybase, MSSQL and MaxDB (SAPDB).
Python 2.7 or 3.4+ is required.

For development see the projects at
`SourceForge <https://sourceforge.net/projects/sqlobject/>`_
and `GitHub <https://github.com/sqlobject>`_.

.. image:: https://github.com/sqlobject/sqlobject/actions/workflows/run-tests.yaml/badge.svg?branch=github-actions
   :target: https://github.com/sqlobject/sqlobject/actions/workflows/run-tests.yaml
""",  # noqa: E501 line too long
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        "GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    maintainer="Oleg Broytman",
    maintainer_email="phd@phdru.name",
    url="http://sqlobject.org/",
    download_url="https://pypi.org/project/SQLObject/%s/" %
    sqlobject_version['version'],
    project_urls={
        'Homepage': 'http://sqlobject.org/',
        'Development docs': 'http://sqlobject.org/devel/',
        'Download': 'https://pypi.org/project/SQLObject/%s/' %
        sqlobject_version['version'],
        'Github repo': 'https://github.com/sqlobject',
        'Issue tracker': 'https://github.com/sqlobject/sqlobject/issues',
        'SourceForge project': 'https://sourceforge.net/projects/sqlobject/',
        'Twitter': 'https://twitter.com/SQLObject',
        'Wikipedia': 'https://en.wikipedia.org/wiki/SQLObject',
    },
    keywords=["sql", "orm", "object-relational mapper"],
    license="LGPL",
    platforms="Any",
    packages=["sqlobject"]
    + ['sqlobject.%s' % package for package in subpackages],
    scripts=["scripts/sqlobject-admin", "scripts/sqlobject-convertOldURI"],
    package_data={
        "sqlobject.maxdb": ["readme.txt"],
    },
    entry_points="""
    [paste.filter_app_factory]
    main = sqlobject.wsgi_middleware:make_middleware
    """,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    requires=['FormEncode', 'PyDispatcher'],
    install_requires=[
        "FormEncode>=1.1.1,!=1.3.0; python_version=='2.7'",
        "FormEncode>=1.3.1; python_version>='3.4'",
        "PyDispatcher>=2.0.4",
    ],
    extras_require={
        # Firebird/Interbase
        'fdb': ['fdb'],
        'firebirdsql': ['firebirdsql'],
        'kinterbasdb': ['kinterbasdb'],
        # MS SQL
        'adodbapi': ['adodbapi'],
        'pymssql': ['pymssql'],
        # MySQL
        'mysql:python_version=="2.7"': ['MySQL-python'],
        'mysql:python_version>="3.4"': ['mysqlclient'],
        'mysql-connector': ['mysql-connector'],
        'mysql-connector-python': ['mysql-connector-python'],
        'oursql:python_version=="2.7"': [
            'oursql @ git+https://github.com/sqlobject/oursql.git@master'],
        'oursql:python_version>="3.4"': [
            'oursql3 @ git+https://github.com/sqlobject/oursql.git@py3k'],
        'pymysql': ['pymysql'],
        'mariadb': ['mariadb'],
        # ODBC
        'odbc': ['pyodbc'],
        'pyodbc': ['pyodbc'],
        'pypyodbc': ['pypyodbc'],
        # PostgreSQL
        'psycopg2': ['psycopg2'],
        'psycopg': ['psycopg2'],
        'postgres': ['psycopg2'],
        'postgresql': ['psycopg2'],
        'pygresql': ['pygresql'],
        'pypostgresql': ['py-postgresql'],
        'py-postgresql': ['py-postgresql'],
        'pg8000:python_version=="2.7"': ['pg8000<1.13'],
        'pg8000:python_version=="3.4"': ['pg8000<1.12.4'],
        'pg8000:python_version>="3.5"': ['pg8000'],
        #
        'sapdb': ['sapdb'],
        'sqlite': ['pysqlite'],
        'supersqlite': ['supersqlite'],
        'sybase': ['Sybase'],
    },
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
and Sybase.  Python 2.7 or 3.4+ is required.


Where is SQLObject
==================

Site:
http://sqlobject.org

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Download:
https://pypi.org/project/SQLObject/@@/

News and changes:
http://sqlobject.org/docs/News.html

-- 
Ian Bicking  /  ianb@colorstudy.com  / http://blog.ianbicking.org
"""  # noqa: preserve space after two dashes
