from distutils.core import setup
import warnings
warnings.filterwarnings("ignore", "Unknown distribution option")

import sys
# patch distutils if it can't cope with the "classifiers" keyword
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="SQLObject",
      version="0.5.1",
      description="Object-Relational Manager, aka database wrapper",
      long_description="""\
Classes created using SQLObject wrap database rows, presenting a
friendly-looking Python object instead of a database/SQL interface.
Emphasizes convenience.  Works with MySQL, Postgres, SQLite, Firebird.
Requires Python 2.2+.
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
      packages=["SQLObject", "SQLObject.include"],
      download_url="http://prdownloads.sourceforge.net/sqlobject/SQLObject-0.5.1.tar.gz?download")

# Send announce to:
#   sqlobject-discuss@lists.sourceforge.net
#   db-sig@python.org
#   python-announce@python.org
#   python-list@python.org
