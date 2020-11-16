
.. _installation:

Installation
************

This is a guide to installing the Translate Toolkit on your system.  If the
Translate Toolkit is already packaged for your system, this is probably the
easiest way to install it. For several Linux distributions, the package might
be available through your package manager.  On Windows, we recommend using a
virtual environment.

If your system already has the toolkit prepackaged, then please let us know
what steps are required to install it.


.. _installation#building:

Building
========

For build instructions, see the :doc:`developers/building` page.


.. _installation#download:

Download
========

Download a stable `released version
<https://github.com/translate/translate/releases>`_.  Or
if you have a python environment, run `pip install translate-toolkit`.  For
those who need problems fixed, or who want to work on the bleeding edge, get
the latest source from :ref:`Git <installation#installing_from_git>`.

If you install through your distribution's package manager, you should
automatically have all the dependencies you need. If you are installing a
version from Version Control, or from a source release, you should check the
README file for information on the dependencies that are needed. Some of the
dependencies are optional. The README file documents this.


.. _installation#installing_packaged_versions:

Installing packaged versions
============================

Get the package for your system:

+------------+------------------------------------------------------------+
| RPM        | If you want to install easily on an RPM based system       |
+------------+------------------------------------------------------------+
| .tar.gz    | for source based installing on Linux                       |
+------------+------------------------------------------------------------+
| .deb       | for Debian GNU/Linux (etch version)                        |
+------------+------------------------------------------------------------+

The RPM package can be installed by using the following command:

.. code-block:: console

   $ rpm -Uvh translate-toolkit-1.0.1.rpm


To install a tar.bz2:

.. code-block:: console

   $ tar xvjf translate-toolkit-1.1.0.tar.bz2
   $ cd translate-toolkit-1.1.0
   $ su
   $ ./setup.py install


On Debian (if you are on etch), just type the following command:

.. code-block:: console

   $ aptitude install translate-toolkit


If you are using an old Debian stable system, you might want to install the
.tar.bz2 version. Be sure to install python and python development first with:

.. code-block:: console

   $ apt-get install python python-dev


Alternatively newer packages might be in testing.


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

   $ su
   $ ./setup.py install


or, running the tools from the source directory:

.. code-block:: console

   $ su
   $ pip install -e .

.. _installation#verify_installed_version:

Verify installed version
========================

To verify which version of the toolkit you have installed run:

.. highlight:: console
.. parsed-literal::


   $ prop2po --version
   prop2po |release|


.. _installation#cleanup:

Cleaning up existing installation
=================================

To remove old versions of the toolkit which you might have installed without a
virtual environment or without your package manager.

The following advice only applies to manual installation from a tarball.

#. Find location of your python packages:

   .. code-block:: console

      $ python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"


#. Delete toolkit package from your Python site-packages directory e.g.:

   .. code-block:: console

      $ rm -R /usr/local/lib/python3.9/dist-packages/translate
