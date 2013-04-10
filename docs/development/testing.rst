.. _testing:

Testing
=======

Our aim is that all new functionality is adequately tested. Adding tests for
existing functionality is highly recommended before any major reimplementation
(refactoring etcetera).

We use py.test for unit testing. You need at least py.test >= 1.0.0

To run all the tests in the current directory and its subdirectories::

    $ py.test

To run tests in a specific test file::

    $ py.test storage/test_dtd.py

Plugins for py.test
===================

We use several py.test plugins to simplify testing, and to suppress errors in
circumstances where the tests cannot possibly succeed (limitations of
tests and missing dependencies).

Skipping tests
--------------

The `skipping plugin <http://pytest.org/latest/skipping.html>`_ allows tests,
test classes, and modules to be skipped or marked as "expected to fail"
(xfail). We use several of the functions and decorators that this provides.
Generally you should *skip* only if the test cannot run at all (throws uncaught
exception); otherwise *xfail* is preferred as it provides more test coverage.

The ``importorskip`` function can be used to skip a test module if a dependency
cannot be imported::

    import pytest
    pytest.importorskip("vobject")

If **vobject** can be imported, it will be; otherwise it raises an exception
that causes pytest to skip the entire module rather than failing.

The ``skipif`` decorator can be used to skip a function/method or all methods
of a class if certain criteria are not met.  The following will skip a test if
the version of **mymodule** is too old::

    import mymodule

    @pytest.mark.skipif("mymodule.__version__ < '1.2'")
    def test_function():
        ...

It is also possible to skip an entire test module by creating a ``pytestmark``
global variable in the module::

    # mark entire module as skipped for py.test if no indexer available
    pytestmark = pytest.mark.skipif("noindexer")

The ``xfail`` decorator allows us to run tests that we expect to fail.
This allows you to do the following:

* Build tests for functionality that we haven't implemented yet
* Mark tests that will fail on certain platforms or Python versions
* Mark out tests that we want to fix but haven't got round to fixing yet

The simplest form is the following::

    from pytest import pytest.mark

    @mark.xfail("Not implemented")
    def test_function():
        ...

You can also pass the following parameters::

    xfail(“sys.version_info >= (3,0)”) - only expect failure in some cases
    xfail(..., run=False) - don't run the test but still regard it as xfailed
    xfail(..., reason=“my reason”) - provide a reason for the xfail

Testing for Warnings
--------------------

The `recwarn plugin <http://pytest.org/latest/recwarn.html>`_ allows us to test
for Warnings (in particular DeprecationWarning).

Note that ``recwarn`` is a funcargs plugins which means that you need it in
your test function parameters::

    def test_example(recwarn):
        # do something
        w = recwarn.pop()
        # w.{message,category,filename,lineno}
        assert 'something' in str(w.message)

To test for DeprecationWarning is even simpler::

    from pytest import deprecated_call
 
    def test_something():
        deprecated_call(function_to_run, arguments_for_function)

will check that a function that we run raises a DeprecationWarning

