.. _yaml2po:
.. _po2yaml:

yaml2po
*******

.. versionadded:: 2.2.6

Converts YAML localization files to Gettext PO format.

.. _yaml2po#usage:

Usage
=====

.. code-block:: console

  yaml2po [options] <yml> <po>
  po2yaml [options] <po> <yml>


Where:

+--------+--------------------------------------------------------------+
| <yml>  | is a valid YAML localisable file or directory of those files |
+--------+--------------------------------------------------------------+
| <po>   | is a directory of PO or POT files                            |
+--------+--------------------------------------------------------------+

Options (yaml2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in yaml, yml formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in yaml, yml formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2yaml):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in yaml, yml formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in yaml, yml formats
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is
                     above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _yaml2po#formats_supported:

Formats Supported
=================

Check :doc:`YAML format </formats/yaml>` document to see to which extent the
YAML format is supported.


.. _yaml2po#examples:

Examples
========

This example looks at roundtrip of YAML translations as well as recovery of
existing translations.

First we need to create a set of POT files:

.. code-block:: console

  yaml2po -P lang/en pot/


All .yml files found in the ``lang/en`` directory are converted to Gettext POT
files and placed in the ``pot`` directory.

If you are translating for the first time then you can skip the next step. If
you need to recover your existing translations then we do the following:

.. code-block:: console

  yaml2po -t lang/en lang/zu po-zu/


Using the English YAML files found in ``lang/en`` and your existing Zulu
translation in ``lang/zu`` we create a set of PO files in ``po-zu``.  These
will now have your translations. Please be aware that in order for that to work
100% you need to have both English and Zulu at the same revision, if they are
not you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows:

.. code-block:: console

  po2yaml -t lang/en po-zu/ lang/zu


Your translations found in the Zulu PO directory, ``po-zu``, will be converted
to YAML using the files in ``lang/en`` as templates and placing your new
translations in ``lang/zu``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.
