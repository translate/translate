
.. _installation:

Installation
************

This is a guide to installing the Translate Toolkit on your system.  If the
Translate Toolkit is already packaged for your system, this is probably the
easiest way to install it. For several Linux distributions, the package might
be available through your package manager.

If your system already has the toolkit prepackaged, then please let us know
what steps are required to install it.


.. _installation#download:

Download
========

The recommended installation is using :program:`uv` or :program:`pip` in a
virtual environment.

.. code-block:: sh

   uv pip install translate-toolkit

You can also  download a stable `released version
<https://github.com/translate/translate/releases>`_ and install it manually.

For those who need problems fixed, or who want to work on the bleeding edge,
get the latest source from :ref:`Git <installation#installing_from_git>`.

.. _installation#installing_packaged_versions:

Installing packaged versions
============================

Many Linux distributions come with translate-toolkit packaged, use your
distribution command to install it:

On Debian (if you are on etch), just type the following command:

.. code-block:: sh

   # Debian / Ubuntu
   apt install translate-toolkit

   # Fedora / RedHat
   dnf install translate-toolkit 

   # openSUSE
   zypper install translate-toolkit 

.. _installation#installing_on_windows:

Installing on Windows
=====================

On Windows we recommend that you install Translate Toolkit using a virtual
environment. This makes installation clean and isolated.

Use the latest Python 3.9.  Install `virtualenvwrapper-win
<https://pypi.python.org/pypi/virtualenvwrapper-win>`_ to simplify handling of
virtualenvs.

1. Install latest `Python 3.9 <https://www.python.org/downloads/windows/>`_
2. Open cmd.exe or similar
3. `pip install virtualenvwrapper-win`
4. `mkvirtualenv ttk` where "ttk" is the name for the new virtualenv
5. `pip install translate-toolkit[recommended]` to install latest stable or `pip install
   --pre translate-toolkit[recommended]` to try a pre-release
6. `po2prop --version` to double check you have the right version

Next times you need to use Translate Toolkit just remember to:

1. Open cmd.exe or similar
2. `workon ttk` to enable the virtualenv again
3. Run the Translate Toolkit commands you want


.. _installation#installing_from_git:

Installing from Git
===================

If you want to try the bleeding edge, or just want to have the latest fixes
from a stabilising branch then you need to use Git to get your sources:

.. code-block:: console

   $ git clone https://github.com/translate/translate.git


This will retrieve the ``master`` branch of the Toolkit.  Further Git
`instructions <http://git.or.cz/course/svn.html>`_ are also available.

Once you have the sources you have two options, a full install:

.. code-block:: console

   $ uv pip install .

or, running the tools from the source directory:

.. code-block:: console

   $ uv pip install -e .

.. _installation#verify_installed_version:

Verify installed version
========================

To verify which version of the toolkit you have installed run:

.. highlight:: console
.. parsed-literal::


   $ prop2po --version
   prop2po |release|
