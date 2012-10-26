
.. _pages/toolkit/ts2po#ts2po_and_po2ts:

ts2po and po2ts
***************

Convert Qt .ts localization files to Gettext .po format files using ts2po and convert the translated :doc:`/formats/po` files back to :doc:`/formats/ts` using po2ts.

The Qt toolkit comes with a localization application, Qt Linguist, however you might wish to standardise on one localization tool.  ts2po allows you to standardise on the PO format and PO related tools. Note that `Virtaal <http://virtaal.org>`_ and `Pootle <http://pootle.tramslatehouse.org>`_ can work with .ts files directly without needing conversion.

.. _pages/toolkit/ts2po#usage:

Usage
=====

::

  ts2po [options] <ts> <po>
  po2ts [options] <po> <ts>

Where:

| <ts>  | is a Qt .ts file or directory that contains .ts files  |
| <po>  | is a PO file or a directory of PO files  |

Options (ts2po):

| --version            | show program's version number and exit  |
| -h, --help           | show this help message and exit  |
| --manpage            | output a manpage based on the help  |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose  |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`  | show errorlevel as: none, message, exception, traceback  |
| -iINPUT, --input=INPUT   | read from INPUT in ts format  |
| -xEXCLUDE, --exclude=EXCLUDE  | exclude names matching EXCLUDE from input paths  |
| -oOUTPUT, --output=OUTPUT   | write to OUTPUT in po, pot formats  |
| :doc:`--psyco=MODE <option_psyco>`         | use psyco to speed up the operation, modes: none, full, profile  |
| -P, --pot            | output PO Templates (.pot) rather than PO files (.po)  |

Options (po2ts):

| --version            | show program's version number and exit   |
| -h, --help           | show this help message and exit   |
| --manpage            | output a manpage based on the help   |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose   |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`   | show errorlevel as: none, message, exception, traceback   |
| -iINPUT, --input=INPUT    | read from INPUT in po, pot formats   |
| -xEXCLUDE, --exclude=EXCLUDE   | exclude names matching EXCLUDE from input paths   |
| -oOUTPUT, --output=OUTPUT  | write to OUTPUT in ts format   |
| -tTEMPLATE, --template=TEMPLATE   | read from TEMPLATE in ts format   |
| :doc:`--psyco=MODE <option_psyco>`         | use psyco to speed up the operation, modes: none, full, profile  |

.. _pages/toolkit/ts2po#examples:

Examples
========

::

  ts2po -P psi.ts psi.pot

This will create a POT file called *psi.pot* from the Qt .ts file called *psi.ts*. ::

  po2ts af.po psi_af.ts

Now take your translated PO files *af.po* and convert it into a translated Qt .ts file, *psi_af.ts*.

.. note:: You need to use the tools from the Qt toolkit to create the compiled
   .qm language files for the application.

.. _pages/toolkit/ts2po#bugs:

Bugs
====

There are probably still some bugs related to migrating the various attributes across for the different formats. The converters don't support all the newer features of the TS format, whereas the native support of Virtaal and Pootle is much better.
