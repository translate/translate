
.. _fluent2po:

fluent2po
*********

Converts Fluent (.ftl) files to Gettext PO format.

`Fluent <https://projectfluent.org/>`_ is a monolingual localization format
used by Mozilla Firefox, Anki, and other projects.

.. _fluent2po#usage:

Usage
=====

::

  fluent2po [options] <ftl> <po>

Where:

+--------+---------------------------------------------------+
| <ftl>  | is a valid .ftl file or directory of those files  |
+--------+---------------------------------------------------+
| <po>   | is a directory of PO or POT files                 |
+--------+---------------------------------------------------+

Options (fluent2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in Fluent format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in Fluent format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

.. _fluent2po#examples:

Examples
========

This example shows how to convert Fluent files used in a project like Anki.

First, create POT files from the English templates::

  fluent2po -P templates/ pot/

All .ftl files found in the ``templates/`` directory are converted to Gettext
POT files and placed in the ``pot/`` directory. Fluent resource comments,
group comments and standalone comments are skipped; only translatable messages
and terms are extracted.

To recover existing translations, run::

  fluent2po -t templates/ ca/ po-ca/

Using the English Fluent files found in ``templates/`` and existing translated
Fluent files in ``ca/``, this creates a set of PO files in ``po-ca/``.
Messages are matched between template and translation using Fluent message IDs.

To update translations, regenerate POT files and use :doc:`pot2po` to bring
translations up to date.
