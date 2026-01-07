
.. _mozlang2po:
.. _po2mozlang:

mozlang2po
**********

Converts Mozilla .lang files to Gettext PO format.

.. _mozlang2po#usage:

Usage
=====

::

  mozlang2po [options] <lang> <po>
  po2mozlang [options] -t <lang> <po> <lang>

Where:

+---------+-----------------------------------------------------------+
| <lang>  | is a valid Mozilla .lang file or directory of those files |
+---------+-----------------------------------------------------------+
| <po>    | is a directory of PO or POT files                         |
+---------+-----------------------------------------------------------+

Options (mozlang2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in lang format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--encoding=ENCODING  The encoding of the input file (default: UTF-8)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2mozlang):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in lang format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in lang format
-S, --timestamp       skip conversion if the output file has newer timestamp
--mark-active        mark the file as active
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _mozlang2po#examples:

Examples
========

These examples demonstrate the basic usage of mozlang2po and po2mozlang:

.. _mozlang2po#creating_pot_files:

Creating POT files
------------------

::

  mozlang2po -P lang/ pot/

Extract messages from Mozilla .lang files in the ``lang/`` directory and create
POT files in the ``pot/`` directory. The :opt:`-P` option ensures that we
create POT files instead of PO files.::

  mozlang2po -P file.lang file.pot

Extract messages from *file.lang* and create a POT file *file.pot*.

.. _mozlang2po#creating_po_files_from_existing_translations:

Creating PO files from existing translations
--------------------------------------------

::

  mozlang2po fr/ fr-po/

Convert Mozilla .lang files from the ``fr/`` directory to PO format in
``fr-po/``. This allows you to work with PO editors while maintaining your
existing .lang translations.

.. _mozlang2po#creating_.lang_files_from_po_translations:

Creating .lang files from PO translations
-----------------------------------------

::

  po2mozlang -t en-US/ fr-po/ fr/

Using the PO translations in ``fr-po/`` and the templates in ``en-US/``, create
Mozilla .lang files in ``fr/``. These files will be in the proper .lang format
and ready for use with Mozilla websites.

To mark the output file as active, use the :opt:`--mark-active` option::

  po2mozlang --mark-active -t en-US/ fr-po/ fr/

This adds an ``## active ##`` marker to the .lang file, indicating that it
should be used in production.

.. _mozlang2po#notes:

Notes
=====

Mozilla .lang format
--------------------

The Mozilla .lang format is a simple key-value format used for localizing
Mozilla websites. See the :doc:`Mozilla .lang format documentation
</formats/mozilla_lang>` for more details.

Active marker
-------------

The ``--mark-active`` option in po2mozlang adds an ``## active ##`` marker to
the beginning of the .lang file. This marker is used by Mozilla's localization
infrastructure to indicate that a translation is complete and ready for
production use.

Encoding
--------

The default encoding for .lang files is UTF-8. If you need to work with files
in a different encoding, use the :opt:`--encoding` option when converting from
.lang to PO.
