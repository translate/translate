
.. _pages/toolkit/pocommentclean#pocommentclean:

pocommentclean
**************

pocommentclean will remove all translator comments from a directory of PO files.

.. _pages/toolkit/pocommentclean#prerequisites:

Prerequisites
=============

* `sed <http://linux.die.net/man/1/bash>`_

.. _pages/toolkit/pocommentclean#usage:

Usage
=====

::

  pocommentclean [--backup] <po>

Where:
| po           | is a directory of existing PO files that you want to clean  |

Options:
| -- backup  | Create a backup file for each PO file converted, .po.bak  |

.. _pages/toolkit/pocommentclean#operation:

Operation
=========

Using sed pocommentclean will delete all lines starting with # but which are not standard Gettext PO format lines.  So it won't delete developer comments (#.), obsolete messages (#~), flags (#,) or locations (#:).

.. _pages/toolkit/pocommentclean#bugs:

Bugs
====

pocommentclean cannot clean individual PO files, it only cleans directories
