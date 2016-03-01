
.. _pocompile:

pocompile
*********

Compile PO or XLIFF files into MO (Machine Object) files.  MO files are
installed on your computer and allow a Gettext enabled computer to provide the
translations for the application.

.. _pocompile#usage:

Usage
=====

::

  pocompile <po> <mo>

Where:

+-------------+------------------------------------------------+
| <po/xliff>  | is a standard PO file, XLIFF file or directory |
+-------------+------------------------------------------------+
| <mo>        | is the output MO file or directory of MO files |
+-------------+------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in xlf, po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT   write to OUTPUT in mo format
-S, --timestamp       skip conversion if the output file has newer timestamp
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _pocompile#examples:

Examples
========

::

  pocompile --fuzzy file.po file.mo

Creates a new MO file called *file.mo* based on the translation in the PO file
*file.po*.  By using the :opt:`--fuzzy` option we use all translations
including those marked fuzzy. ::

  pocompile file.xlf file.mo

Create an MO file from an XLIFF file called *file.xlf* (available from version
1.1 of the toolkit).
