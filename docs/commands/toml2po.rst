.. _toml2po:
.. _po2toml:

toml2po
*******

.. versionadded:: 3.16.0

Converts TOML localization files to Gettext PO format.

.. _toml2po#usage:

Usage
=====

.. code-block:: console

  toml2po [options] <toml> <po>
  po2toml [options] <po> <toml>


Where:

+--------+---------------------------------------------------------------+
| <toml> | is a valid TOML localisable file or directory of those files |
+--------+---------------------------------------------------------------+
| <po>   | is a directory of PO or POT files                             |
+--------+---------------------------------------------------------------+

Options (toml2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in toml formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in toml formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2toml):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in toml formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in toml formats (required)
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is
                     above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _toml2po#formats_supported:

Formats Supported
=================

Check :doc:`TOML format </formats/toml>` document to see which TOML features
are supported.

Both plain TOML files and Go i18n TOML files with plurals are supported.


.. _toml2po#examples:

Examples
========

This example looks at roundtrip of TOML translations as well as recovery of
existing translations.

First we need to create a set of POT files:

.. code-block:: console

  toml2po -P i18n/en.toml pot/


The TOML file found in ``i18n/en.toml`` is converted to a Gettext POT
file and placed in the ``pot`` directory.

If you are translating for the first time then you can skip the next step. If
you need to recover your existing translations then we do the following:

.. code-block:: console

  toml2po -t i18n/en.toml i18n/fr.toml po-fr/


Using the English TOML file found in ``i18n/en.toml`` and your existing French
translation in ``i18n/fr.toml`` we create a set of PO files in ``po-fr``. These
will now have your translations. Please be aware that in order for that to work
100% you need to have both English and French at the same revision, if they are
not you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows:

.. code-block:: console

  po2toml -t i18n/en.toml po-fr/ i18n/fr.toml


Your translations found in the French PO directory, ``po-fr/``, will be
converted to TOML using the file in ``i18n/en.toml`` as a template and placing
your new translations in ``i18n/fr.toml``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.


.. _toml2po#go_i18n:

Go i18n Format with Plurals
============================

For Go i18n TOML files that contain pluralized strings, the conversion works
the same way. The plural forms are automatically detected when a table contains
2 or more keys that are all CLDR plural categories.

Example Go i18n TOML file:

.. code-block:: toml

    [reading_time]
    one = "One minute to read"
    other = "{{ .Count }} minutes to read"

    [category]
    other = "category"

    [items]
    zero = "No items"
    one = "One item"
    other = "{{ .Count }} items"


When converted to PO, plural entries will have proper ``msgid_plural`` and
``msgstr[n]`` forms, while single-key tables (like ``category``) are treated as
regular strings.
