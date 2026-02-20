.. _wxl2po:
.. _po2wxl:

wxl2po
******

Converts WiX Localization (.wxl) files to Gettext PO format.

.. _wxl2po#usage:

Usage
=====

::

  wxl2po [options] <wxl> <po>
  po2wxl [options] <po> <wxl> [-t <base-wxl>]

Where:

+------------+------------------------------------------------------------+
| <wxl>      | is a valid .wxl file or directory of those files           |
+------------+------------------------------------------------------------+
| <po>       | is a directory of PO or POT files                          |
+------------+------------------------------------------------------------+
| <base-wxl> | is a template or the original file before translation.     |
|            | Required for roundtrips to preserve non-translatable data. |
+------------+------------------------------------------------------------+

Options (wxl2po):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS   show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT
                      read from INPUT in wxl format
-x EXCLUDE, --exclude=EXCLUDE
                      exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT
                      write to OUTPUT in po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp

Options (po2wxl):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS   show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT
                      read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE
                      exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT
                      write to OUTPUT in wxl format
-t TEMPLATE, --template=TEMPLATE
                      read from TEMPLATE in wxl format
-S, --timestamp       skip conversion if the output file has newer timestamp

.. _wxl2po#formats-supported:

Formats Supported
=================

Check the :doc:`WXL format </formats/wxl>` document for details of what is
supported.

.. _wxl2po#examples:

Examples
========

This example shows a roundtrip of WXL translations.

First create a set of POT files::

  wxl2po -P lang/en pot/

All .wxl files found in ``lang/en`` are converted to Gettext POT files and
placed in the ``pot/`` directory.

To recover existing translations::

  wxl2po -t lang/en lang/de po-de/

Using the English WXL files in ``lang/en`` and existing German translations in
``lang/de``, create PO files in ``po-de/`` with the recovered translations.

Once translated, convert back::

  po2wxl -t lang/en po-de/ lang/de

Translations from ``po-de/`` are applied to template files in ``lang/en`` and
the result is written to ``lang/de``.
