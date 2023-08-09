++++
News
++++

.. contents:: Contents:
   :backlinks: none

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
