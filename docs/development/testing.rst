.. _testing:

Testing
=======

Our aim is that all new functionality is adequately tested. Adding tests for
existing functionality is highly recommended before any major reimplementation
(refactoring, etcetera).

We use `py.test`_ for (unit) testing. You need at least pytest >= 1.0.0, but
pytest >= 2.1 is strongly recommended.

To run tests in the current directory and its subdirectories:

.. code-block:: bash

    $ py.test  # runs all tests
    $ py.test storage/test_dtd.py  # runs just a single test module

We use several py.test features to simplify testing, and to suppress errors in
circumstances where the tests cannot possibly succeed (limitations of
tests and missing dependencies).


Skipping tests
--------------

Pytest allows tests, test classes, and modules to be skipped or marked as
"expected to fail" (xfail).
Generally you should *skip* only if the test cannot run at all (throws uncaught
exception); otherwise *xfail* is preferred as it provides more test coverage.

importorskip
^^^^^^^^^^^^

.. the ~ in this :func: reference suppresses all but the last component

Use the builtin :func:`~pytest:_pytest.runner.importorskip` function
to skip a test module if a dependency cannot be imported:

.. code-block:: python

    from pytest import importorskip
    importorskip("vobject")

If *vobject* can be imported, it will be; otherwise it raises an exception
that causes pytest to skip the entire module rather than failing.

skipif
^^^^^^

Use the ``skipif`` decorator to :ref:`mark tests to be skipped <pytest:skipif>`
unless certain criteria are met.  The following skips a test if the version of
*mymodule* is too old:

.. code-block:: python

    import mymodule

    @pytest.mark.skipif("mymodule.__version__ < '1.2'")
    def test_function():
        ...

In Python 2.6 and later, you can apply this decorator to classes as well as
functions and methods.

It is also possible to skip an entire test module by creating a ``pytestmark``
static variable in the module:

.. code-block:: python

    # mark entire module as skipped for py.test if no indexer available
    pytestmark = pytest.mark.skipif("noindexer")

xfail
^^^^^

Use the ``xfail`` decorator to :ref:`mark tests as expected to fail
<pytest:xfail>`. This allows you to do the following:

* Build tests for functionality that we haven't implemented yet
* Mark tests that will fail on certain platforms or Python versions
* Mark tests that we should fix but haven't got round to fixing yet

The simplest form is the following:

.. code-block:: python

    from pytest import pytest.mark
    
    @mark.xfail
    def test_function():
        ...

You can also pass parameters to the decorator to mark expected failure only
under some condition (like *skipif*), to document the reason failure is
expected, or to actually skip the test:

.. code-block:: python

    @mark.xfail("sys.version_info >= (3,0)")  # only expect failure for Python 3
    @mark.xfail(..., reason="Not implemented")  # provide a reason for the xfail
    @mark.xfail(..., run=False)  # skip the test but still regard it as xfailed


Testing for Warnings
--------------------

deprecated_call
^^^^^^^^^^^^^^^

The builtin :func:`~pytest:pytest.deprecated_call` function checks that a
function that we run raises a DeprecationWarning:

.. code-block:: python

    from pytest import deprecated_call
 
    def test_something():
        deprecated_call(function_to_run, arguments_for_function)

recwarn
^^^^^^^

The |recwarn plugin|_ allows us to test for other warnings. Note that
``recwarn`` is a funcargs plugin, which means that you need it in your test
function parameters:

.. code-block:: python

    def test_example(recwarn):
        # do something
        w = recwarn.pop()
        # w.{message,category,filename,lineno}
        assert 'something' in str(w.message)


.. _py.test: http://pytest.org/

.. _recwarn plugin: http://pytest.org/latest/recwarn.html
.. |recwarn plugin| replace:: *recwarn plugin*
.. we use |recwarn plugin| here and in ref above for italics like :ref:
