# ez_setup doesn't work with Python 2.2, so we use distutils
# in that case:
try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
except ImportError:
    from distutils.core import setup

subpackages = ['firebird', 'inheritance', 'mysql', 'postgres',
               'sqlite', 'sybase', 'maxdb', 'util', 'manager']

import sys
# patch distutils if it can't cope with the "classifiers" keyword
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="SQLObject",
      version="0.7b1",
      description="Object-Relational Manager, aka database wrapper",
      long_description="""\
Classes created using SQLObject wrap database rows, presenting a
friendly-looking Python object instead of a database/SQL interface.
Emphasizes convenience.  Works with MySQL, Postgres, SQLite, Firebird.
Requires Python 2.2+.

For development see the `subversion repository
<http://svn.colorstudy.com/trunk/SQLObject#egg=SQLObject>`_
""",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Programming Language :: Python",
                   "Topic :: Database",
                   "Topic :: Database :: Front-Ends",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://sqlobject.org",
      license="LGPL",
      packages=["sqlobject"] + ['sqlobject.%s' % package for package in subpackages],
      scripts=["scripts/sqlobject-admin"],
      install_requires=["FormEncode>=0.2.2"],
      extras_require={
        'postgresql': ['psycopg'],
        'mysql': ['MySQLdb'],
        'sqlite': ['pysqlite'],
        # Others?
        },
      )

# Send announce to:
#   sqlobject-discuss@lists.sourceforge.net
#   db-sig@python.org
#   python-announce@python.org
#   python-list@python.org

# Email tempate:
"""
@@ INTRO

What is SQLObject
=================

SQLObject is an object-relational mapper.  Your database tables are described as classes, and rows are instances of those classes.  SQLObject is meant to be easy to use and quick to get started with.

SQLObject supports a number of backends: MySQL, PostgreSQL, SQLite, and Firebird.  It also has newly added support for Sybase and MaxDB (also known as SAPDB).


Where is SQLObject
==================

Site:
http://sqlobject.org

Mailing list:
https://lists.sourceforge.net/mailman/listinfo/sqlobject-discuss

Archives:
http://news.gmane.org/gmane.comp.python.sqlobject

Download:
http://prdownloads.sourceforge.net/sqlobject/SQLObject-@@.tar.gz?download

News and changes:
http://sqlobject.org/docs/News.html


What's New
==========

@@ CHANGES

For a more complete list, please see the news: http://sqlobject.org/docs/News.html

-- 
Ian Bicking  /  ianb@colorstudy.com  / http://blog.ianbicking.org
"""
