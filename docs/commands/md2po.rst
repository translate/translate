
.. _md2po:
.. _po2md:

md2po, po2md
************

Convert translatable items in Markdown text to the PO format. Insert translated text into Markdown templates.

.. _md2po#usage:

Usage
=====

::

  md2po [options] <md-src> <po>
  po2md [options] -i <po> -t <md-src> -o <md-dest>

Where:

+-----------+----------------------------------------------------------------------------------------+
| <md-src>  | is a Markdown file or a directory of Markdown files, source language                   |
+-----------+----------------------------------------------------------------------------------------+
| <md-dest> | is a Markdown file or a directory of Markdown files, translated to the target language |
+-----------+----------------------------------------------------------------------------------------+
| <po>      | is a PO file or directory of PO files                                                  |
+-----------+----------------------------------------------------------------------------------------+

Options (md2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in Markdown format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')
--multifile=MULTIFILESTYLE
                      how to split po/pot files (:doc:`single, toplevel or
                      onefile <option_multifile>`)
                      (default: 'single'; if set to 'onefile', a single po/pot
                      file will be written. 'toplevel' not used.)


Options (po2md):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in Markdown format
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in Markdown format
-S, --timestamp      skip conversion if the output file has newer timestamp
-m MAXLENGTH, --maxlinelength=MAXLENGTH
                      reflow (word wrap) the output to the given maximum
                      line length. set to 0 to disable
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _md2po#examples:

Examples
========

::

  md2po -P source-md-dir pot

This will find all Markdown files (.md, .markdown, .txt, .text) in
*source-md-dir*, convert them to POT files (that is, extract all translatable
content) and place them in *pot*.

See the :doc:`pot2po` command for more information about how to create PO files
from the POT files, and to update existing PO files when the POT files have
changed.

Suppose you have created PO files for translation to Xhosa and placed them in
the directory *xh*. You can then generate the translated version of the Markdown
documents like so:

::

  po2md -i xh -t source-md-dir -o xh-md-dir

All the PO translations in *xh* will be converted to Markdown using Markdown
files in *source-md-dir* as templates and outputting new translated Markdown
files in *xh-md-dir*.

Should you prefer a single PO/POT file for your collection of Markdown files,
this is how to do it:

::

  md2po -P --multifile=onefile source-md-dir file.pot

And similarly, to generate multiple translated output files from a single PO
file, invoke po2md like so:

::

  po2md -i xh.po -t source-md-dir -o xh-md-dir

In this example, *xh.po* is the translation file for Xhosa, *source-md-dir* is
the directory where the Markdown files in the source language can be found, and
*xh-md-dir* is the directory where the translated Markdown files will end up.

.. _md2po#notes:

Notes
=====

The :doc:`Markdown format description </formats/md>` gives more details on the
format of the localisable Markdown content and the capabilities of this converter.
