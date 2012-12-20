
.. _php2po:
.. _po2php:

php2po
******

Converts PHP localisable string arrays to Gettext PO format.

.. _php2po#usage:

Usage
=====

::

  php2po [options] <php> <po>
  po2php [options] <po> <php>


Where:

+--------+--------------------------------------------------------------+
| <php>  | is a valid PHP localisable file or directory of those files  |
+--------+--------------------------------------------------------------+
| <po>   | is a directory of PO or POT files                            |
+--------+--------------------------------------------------------------+

Options (php2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in php format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
--psyco=MODE          use psyco to speed up the operation, modes: :doc:`none,
                      full, profile <option_psyco>`
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2php):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in php format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
--psyco=MODE          use psyco to speed up the operation, modes: :doc:`none,
                      full, profile <option_psyco>`
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _php2po#formats_supported:

Formats Supported
=================

PHP files need to be organized into separate languages per file and in the
following format:

.. code-block:: php

    $variable = 'string';
    $another_variable = "another string";

If $variable is an array it can be declared with the square bracket syntax:

.. code-block:: php

    $lang['item'] = 'string';
    $lang['another_item'] = "another string";

The converter also supports arrays in the form:

.. code-block:: php

    $variable = array(
       name => 'value',
       other => "other value",
    )

Nested arrays are also supported:

.. code-block:: php

    $lang = array(
       'name' => 'value',
       'name2' => array(
          'key' => 'value',
          'key2' => 'value2',
       ),
    );

Finally, the converter also supports the define syntax:

.. code-block:: php

    define('item', 'string');
    define("another_item", "another string");

The converter supports whitespaces in various places (before the end
delimiter, in the array declaration, etc) in the different dialects supported:

.. code-block:: php

    $variable = 'string'     ;
    $lang['item'] = 'string'    ;
    $variable = array    (
       name => 'value'    ,
       other => "other value",
    )
    define('item', 'string'   );

Gettext notations are also not supported, use the Gettext tools for those
files.

.. note:: Nested arrays without key for nested arrays are not supported:

.. code-block:: php

    $lang = array(array('key' => 'value')); #NOT SUPPORTED

.. note:: In the arrays all entries should have an ending comma:

.. code-block:: php

    $variable = array(
       name => 'value',
       other => "other value" #NOT SUPPORTED
    );

.. _php2po#examples:

Examples
========
This example looks at roundtrip of PHP translations as well as recovery of
existing translations.

First we need to create a set of POT files.::

  php2po -P lang/en pot/

All .php files found in the ``lang/en`` directory are converted to Gettext POT
files and placed in the ``pot`` directory.

If you are translating for the first time then you can skip the next step. If
you need to recover your existing translations then we do the following::

  php2po -t lang/en lang/zu po-zu/

Using the English PHP files found in ``lang/en`` and your existing Zulu
translation in ``lang/zu`` we create a set of PO files in ``po-zu``.  These
will now have your translations. Please be aware that in order for that to work
100% you need to have both English and Zulu at the same revision, if they are
not you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows::

  po2php -t lang/en po-zu/ lang/zu

Your translations found in the Zulu PO directory, ``po-zu``, will be converted
to PHP using the files in ``lang/en`` as templates and placing your new
translations in ``lang/zu``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.
