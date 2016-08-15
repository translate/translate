
.. _l20n2po:
.. _po2l20n:

l20n2po
*******

Convert between L20n files (.ftl) and Gettext PO format.


.. _l20n2po#usage:

Usage
=====

::

  l20n2po [options] <ftl> <po>
  po2l20n [options] -t <template> <po> <ftl>

Where:

+------------+-----------------------------------------------------------+
| <ftl>      | is a directory containing ftl files or an individual      |
|            | ftl file                                                  |
+------------+-----------------------------------------------------------+
| <po>       | is a directory containing PO files and an individual      |
|            | ftl file                                                  |
+------------+-----------------------------------------------------------+
| <template> | is a directory of template ftl files or a single          |
|            | template ftl file                                         |
+------------+-----------------------------------------------------------+

Options (l20n2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in l20n format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in l20n format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2l20n):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in l20n format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in l20n format
-S, --timestamp       skip conversion if the output file has newer timestamp
--removeuntranslated  remove key value from output if it is untranslated
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _l20n2po#examples:

Examples
========

These examples demonstrate most of the useful invocations of l20n2po:


.. _l20n2po#creating_pot_files:

Creating POT files
------------------

::

  l20n2po -P l20n pot

Extract messages from *l20n* directory and place them in a directory
called *pot*.  The :opt:`-P` option ensures that we create POT files instead of
PO files.::

  l20n2po -P file.ftl file.pot

Extract messages from *file.ftl* and place them in *file.pot*.


.. _l20n2po#creating_po_files_from_existing_work:

Creating PO files from existing work
------------------------------------

::

  l20n2po --duplicates=msgctxt -t reference zu zu-po

Extract all existing Zulu messages from *zu* directory and place the resultant
PO files in a directory called *zu-po*.  If you find duplicate messages in a
file then use Gettext's mgsctxt to disambiguate them.  During the merge we use
the .ftl files in *reference* as templates and as the source of the
English text for the msgid.  Once you have your PO files you might want to use
:doc:`pomigrate2` to ensure that your PO files match the latest POT files.


.. _l20n2po#creating_.ftl_files_from_your_translations:

Creating .ftl files from your translations
------------------------------------------

::

  po2l20n -t reference zu-po zu

Using our translations found in *zu-po* and the templates found in *reference*
we create a new set of ftl files in *zu*.  These new ftl files will
look exactly like those found in the templates, but with the text changed to
the translation.  Any fuzzy entry in our PO files will be ignored and any
untranslated item will be placed in *zu* in English.
