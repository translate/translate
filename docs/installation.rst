
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

On Windows we recommend using `uv <https://docs.astral.sh/uv/>`_ to install
Translate Toolkit. This automatically manages virtual environments for you.

1. Install latest `Python 3.9+ <https://www.python.org/downloads/windows/>`_
2. Install uv by running in PowerShell:

   .. code-block:: powershell

      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

3. Create a project directory and install:

   .. code-block:: console

      $ mkdir translate-work
      $ cd translate-work
      $ uv venv
      $ uv pip install translate-toolkit

4. Activate the environment and verify:

   .. code-block:: console

      $ .venv\Scripts\activate
      $ po2prop --version

Next times you need to use Translate Toolkit:

1. Navigate to your project directory
2. Activate the virtual environment: ``.venv\Scripts\activate``
3. Run the Translate Toolkit commands you want


.. _installation#installing_from_git:

Installing from Git
===================

If you want to try the bleeding edge, or just want to have the latest fixes
from a stabilising branch then you need to use Git to get your sources:

.. code-block:: console

   $ git clone https://github.com/translate/translate.git
   $ cd translate


This will retrieve the ``master`` branch of the Toolkit.  Further Git
`instructions <http://git.or.cz/course/svn.html>`_ are also available.

**For users** wanting to install from source:

.. code-block:: console

   $ uv pip install .

**For developers** wanting to contribute:

.. code-block:: console

   $ uv sync --all-extras --dev

This sets up a complete development environment with all dependencies.
See the :doc:`contributing guide </developers/contributing>` for more details.

.. _installation#verify_installed_version:

Verify installed version
========================

To verify which version of the toolkit you have installed run:

.. highlight:: console
.. parsed-literal::


   $ prop2po --version
   prop2po |release|
