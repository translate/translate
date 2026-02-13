
.. _arb2po:

arb2po
******

Converts ARB (Application Resource Bundle) files to Gettext PO format.

ARB is a JSON-based localization format used by Flutter applications.

.. _arb2po#usage:

Usage
=====

::

  arb2po [options] <arb> <po>

Where:

+--------+---------------------------------------------------+
| <arb>  | is a valid .arb file or directory of those files  |
+--------+---------------------------------------------------+
| <po>   | is a directory of PO or POT files                 |
+--------+---------------------------------------------------+

Options (arb2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in ARB format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in ARB format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

.. _arb2po#examples:

Examples
========

This example shows how to convert ARB files used in a Flutter project.

First, create a POT file::

  arb2po -P app_en.arb app.pot

The English ARB file is converted to a Gettext POT file. ARB metadata entries
(``@@locale``, ``@@last_modified``, etc.) are automatically filtered out, and
``@key`` description fields are preserved as translator comments.

To recover existing translations, run::

  arb2po -t app_en.arb app_ca.arb ca.po

Using the English ARB file as a template and an existing translated ARB file,
this creates a PO file with existing translations.

To update translations, regenerate the POT file and use :doc:`pot2po` to bring
translations up to date.
