+++++++++++++++++++++++++
SQLObject Developer Guide
+++++++++++++++++++++++++

.. contents::
   :backlinks: none

.. _start:

These are some notes on developing SQLObject.

Development Installation
========================

First install `FormEncode <http://www.formencode.org/en/latest/download.html>`_::

    $ git clone git://github.com/formencode/formencode.git
    $ cd formencode
    $ sudo python setup.py develop

Then do the same for SQLObject::

    $ git clone git clone git://github.com/sqlobject/sqlobject
    $ cd sqlobject
    $ sudo python setup.py develop

Or rather fork it and clone your fork. To develop a feature or a bugfix
create a separate branch, push it to your fork and create a pull request
to the original repo. That way CI will be triggered to test your code.

Voila!  The packages are globally installed, but the files from the
checkout were not copied into ``site-packages``.  See `setuptools
<https://setuptools.readthedocs.io/en/latest/index.html>`_ for more.

Architecture
============

There are three main kinds of objects in SQLObject: tables, columns and
connections.

Tables-related objects are in `sqlobject/main.py`_ module. There are two
main classes: ``SQLObject`` and ``sqlmeta``; the latter is not a
metaclass but a parent class for ``sqlmeta`` attribute in every class -
the authors tried to move there all attributes and methods not directly
related to columns to avoid cluttering table namespace.

.. _`sqlobject/main.py`: sqlobject/main.py.html

Connections are instances of ``DBConnection`` class (from
`sqlobject/dbconnection.py`_) and its concrete descendants.
``DBConnection`` contains generic code for generating SQL, working with
transactions and so on. Concrete connection classes (like
``PostgresConnection`` and ``SQLiteConnection``) provide
backend-specific functionality.

.. _`sqlobject/dbconnection.py`: sqlobject/dbconnection.py.html

Columns, validators and converters
----------------------------------

Columns are instances of classes from `sqlobject/col.py`_. There are two
classes for every column: one is for user to include into an instance of
SQLObject, an instance of the other is automatically created by
SQLObject's metaclass. The two classes are usually named ``Col`` and
``SOCol``; for example, ``BoolCol`` and ``SOBoolCol``. User-visible
classes, descendants of ``Col``, seldom contain any code; the main code
for a column is in ``SOCol`` descendants and in validators.

.. _`sqlobject/col.py`: sqlobject/col.py.html

Every column has a list of validators. Validators validate input data
and convert input data to python data and back. Every validator must
have methods ``from_python`` and ``to_python``. The former converts data
from python to internal representation that will be converted by
converters to SQL strings. The latter converts data from SQL data to
python. Also please bear in mind that validators can receive ``None``
(for SQL ``NULL``) and ``SQLExpression`` (an object that represents
SQLObject expressions); both objects must be passed unchanged by
validators.

Converters from `sqlobject/converters.py`_ aren't visible to users. They
are used behind the scene to convert objects returned by validators to
backend-specific SQL strings. The most elaborated converter is
``StringLikeConverter``. Yes, it converts strings to strings. It
converts python strings to SQL strings using backend-specific quoting
rules.

.. _`sqlobject/converters.py`: sqlobject/converters.py.html

Let look into ``BoolCol`` as an example. The very ``BoolCol`` doesn't
have any code. ``SOBoolCol`` has a method to create ``BoolValidator``
and methods to create backend-specific column type. ``BoolValidator``
has identical methods ``from_python`` and ``to_python``; the method
passes ``None``, ``SQLExpression`` and bool values unchanged; int and
objects that have method ``__nonzero__`` are converted to bool; other
objects trigger validation error. Bool values that are returned by call
to ``from_python`` will be converted to SQL strings by
``BoolConverter``; bool values from ``to_python`` (is is supposed they
are originated from the backend via DB API driver) are passed to the
application.

Objects that are returned from ``from_python`` must be registered with
converters. Another approach for ``from_python`` is to return an object
that has ``__sqlrepr__`` method. Such objects convert to SQL strings
themselves, converters are not used.

Branch workflow
===============

Initially ``SQLObject`` was being developed using ``Subversion``. Even
after switching to git development process somewhat preserves the old
workflow.

The ``trunk``, called ``master`` in git, is the most advanced and the
most unstable branch. It is where new features are applied. Bug fixes
are applied to ``oldstable`` and ``stable`` branches and are merged
upward -- from ``oldstable`` to ``stable`` and from ``stable`` to
``master``.

Style Guide
===========

Generally you should follow the recommendations in `PEP 8`_, the
Python Style Guide.  Some things to take particular note of:

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/

* With a few exceptions sources must be `flake8`_-clean (and hence
  pep8-clean). Please consider using pre-commit hook installed by
  running ``flake8 --install-hook``.

.. _flake8: https://gitlab.com/pycqa/flake8

* **No tabs**.  Not anywhere.  Always indent with 4 spaces.

* We don't stress too much on line length.  But try to break lines up
  by grouping with parenthesis instead of with backslashes (if you
  can).  Do asserts like::

    assert some_condition(a, b), (
        "Some condition failed, %r isn't right!" % a)

* But if you are having problems with line length, maybe you should
  just break the expression up into multiple statements.

* Blank lines between methods, unless they are very small and closely
  bound to each other.

* *Never* use the form ``condition and trueValue or falseValue``.
  Break it out and use a variable.

* Careful of namespace pollution.  SQLObject does allow for ``from
  sqlobject import *`` so names should be fairly distinct, or they
  shouldn't be exported in ``sqlobject.__init__``.

* We're very picky about whitespace.  There's one and only one right way
  to do it.  Good examples::

    short = 3
    longerVar = 4

    if x == 4:
        do stuff

    func(arg1='a', arg2='b')
    func((a + b)*10)

  **Bad** examples::

    short    =3
    longerVar=4

    if x==4: do stuff

    func(arg1 = 'a', arg2 = 'b')
    func(a,b)
    func( a, b )
    [ 1, 2, 3 ]

  To us, the poor use of whitespace seems lazy.  We'll think less of
  your code (justified or not) for this very trivial reason.  We will
  fix all your code for you if you don't do it yourself, because we
  can't bear to look at sloppy whitespace.

* Use ``@@`` to mark something that is suboptimal, or where you have a
  concern that it's not right.  Try to also date it and put your
  username there.

* Docstrings are good.  They should look like::

    class AClass(object):
        """
        doc string...
        """

  Don't use single quotes (''').  Don't bother trying make the string
  less vertically compact.

* Comments go right before the thing they are commenting on.

* Methods never, ever, ever start with capital letters.  Generally
  only classes are capitalized.  But definitely never methods.

* mixedCase is preferred.

* Use ``cls`` to refer to a class.  Use ``meta`` to refer to a
  metaclass (which also happens to be a class, but calling a metaclass
  ``cls`` will be confusing).

* Use ``isinstance`` instead of comparing types.  E.g.::

    if isinstance(var, str): ...
    # Bad:
    if type(var) is StringType: ...

* Never, ever use two leading underscores.  This is annoyingly
  private.  If name clashes are a concern, use name mangling instead
  (e.g., ``_SO_blahblah``).  This is essentially the same thing as
  double-underscore, only it's transparent where double underscore
  obscures.

* Module names should be unique in the package.  Subpackages shouldn't
  share module names with sibling or parent packages.  Sadly this
  isn't possible for ``__init__``, but it's otherwise easy enough.

* Module names should be all lower case, and probably have no
  underscores (smushedwords).


Testing
=======

Tests are important.  Tests keep everything from falling apart.  All
new additions should have tests.

Testing uses pytest, an alternative to ``unittest``.  It is available
at http://pytest.org/ and https://pypi.python.org/pypi/pytest.  Read its
`getting started`_ document for more.

.. _getting started: http://docs.pytest.org/en/latest/getting-started.html

To actually run the test, you have to give it a database to connect to.
You do so with the option ``-D``. You can either give a complete URI or
one of several shortcuts like ``mysql`` (these shortcuts are defined in
the top of ``tests/dbtest.py``).

All the tests are modules in ``sqlobject/tests``.  Each module tests
one kind of feature, more or less.  If you are testing a module, call
the test module ``tests/test_modulename.py`` -- only modules that
start with ``test_`` will be picked up by pytest.

The "framework" for testing is in ``tests/dbtest``.  There's a couple of
important functions:

``setupClass(soClass)`` creates the tables for the class.  It tries to
avoid recreating tables if not necessary.

``supports(featureName)`` checks if the database backend supports the
named feature.  What backends support what is defined at the top of
``dbtest``.

If you ``import *`` you'll also get pytest's version of raises_, an
``inserts`` function that can create instances for you, and a couple
miscellaneous functions.

.. _raises: http://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions

If you submit a patch or implement a feature without a test, we'll be
forced to write the test.  That's no fun for us, to just be writing
tests.  So please, write tests; everything at least needs to be
exercised, even if the tests are absolutely complete.

We now use Travis CI and AppVeyor to run tests. See the statuses:

.. image:: https://travis-ci.org/sqlobject/sqlobject.svg?branch=master
   :target: https://travis-ci.org/sqlobject/sqlobject

.. image:: https://ci.appveyor.com/api/projects/status/github/sqlobject/sqlobject?branch=master
   :target: https://ci.appveyor.com/project/phdru/sqlobject

To avoid triggering unnecessary test run at CI services add text `[skip ci]
<https://docs.travis-ci.com/user/customizing-the-build/#skipping-a-build>`_ or
``[ci skip]`` anywhere in your commit messages for commits that don't change
code (documentation updates and such).

We use `coverage.py <https://pypi.python.org/pypi/coverage>`_
to measures code coverage by tests and upload the result for analyzis to
`Coveralls <https://coveralls.io/github/sqlobject/sqlobject>`_ and
`Codecov <https://codecov.io/gh/sqlobject/sqlobject>`_:

.. image:: https://coveralls.io/repos/github/sqlobject/sqlobject/badge.svg?branch=master
   :target: https://coveralls.io/github/sqlobject/sqlobject?branch=master

.. image:: https://codecov.io/gh/sqlobject/sqlobject/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/sqlobject/sqlobject

Documentation
=============

Please write documentation.  Documentation should live in the docs/
directory in reStructuredText format.  We use Sphinx to convert docs to
HTML.

.. image:: https://sourceforge.net/sflogo.php?group_id=74338&type=10
   :target: https://sourceforge.net/projects/sqlobject
   :class: noborder
   :align: center
   :height: 15
   :width: 80
   :alt: Get SQLObject at SourceForge.net. Fast, secure and Free Open Source software downloads
