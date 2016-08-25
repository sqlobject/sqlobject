+++++++++
SQLObject
+++++++++

SQLObject is a popular *Object Relational Manager* for providing an
object interface to your database, with tables as classes, rows as
instances, and columns as attributes.

SQLObject includes a Python-object-based query language that makes SQL
more abstract, and provides substantial database independence for
applications.

Documentation
=============

.. toctree::
   :maxdepth: 1

   download
   community
   links

   News
   Python3
   SQLObject
   FAQ
   SQLBuilder
   SelectResults
   sqlobject-admin
   Inheritance
   Versioning
   Views
   DeveloperGuide
   Authors
   TODO

Example
=======

This is just a snippet that creates a simple class that wraps a table::

  >>> from sqlobject import *
  >>>
  >>> sqlhub.processConnection = connectionForURI('sqlite:/:memory:')
  >>>
  >>> class Person(SQLObject):
  ...     fname = StringCol()
  ...     mi = StringCol(length=1, default=None)
  ...     lname = StringCol()
  ...
  >>> Person.createTable()

SQLObject supports most database schemas that you already have, and
can also issue the ``CREATE`` statement for you (seen in
``Person.createTable()``).

Here's how you'd use the object::

  >>> p = Person(fname="John", lname="Doe")
  >>> p
  <Person 1 fname='John' mi=None lname='Doe'>
  >>> p.fname
  'John'
  >>> p.mi = 'Q'
  >>> p2 = Person.get(1)
  >>> p2
  <Person 1 fname='John' mi='Q' lname='Doe'>
  >>> p is p2
  True


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
