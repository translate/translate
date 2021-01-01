
.. _html2po:
.. _po2html:

html2po, po2html
****************

Convert translatable items in HTML to the PO format. Insert translated text into HTML templates.

.. _html2po#usage:

Usage
=====

::

  html2po [options] <html-src> <po>
  po2html [options] -i <po> -t <html-src> -o <html-dest>

Where:

+-------------+---------------------------------------------------------------------------------+
| <html-src>  | is an HTML file or a directory of HTML files, source language                   |
+-------------+---------------------------------------------------------------------------------+
| <html-dest> | is an HTML file or a directory of HTML files, translated to the target language |
+-------------+---------------------------------------------------------------------------------+
| <po>        | is a PO file or directory of PO files                                           |
+-------------+---------------------------------------------------------------------------------+

Options (html2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in htm, html, xhtml formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
-u, --untagged       include untagged sections
--keepcomments       preserve html comments as translation notes in the output
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')
--multifile=MULTIFILESTYLE
                      how to split po/pot files (:doc:`single, toplevel or
                      onefile <option_multifile>`)
                      (default: 'single'; if set to 'onefile', a single po/pot
                      file will be written. 'toplevel' not used.)


Options (po2html):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in htm, html, xhtml formats
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in htm, html, xhtml formats
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _html2po#examples:

Examples
========

::

  html2po -P site pot

This will find all HTML files (.htm, .html, .xhtml) in *site*, convert them to
POT files and place them in *pot*.

You can create and update PO files for different languages using the
:doc:`pot2po` command. For example, you can create PO files for a translation to
Xhosa like this:

::

  pot2po -i pot -t site -o xh

This will merge the POT files in *pot* into the PO files in *xh* (if any).

And then, after editing the PO files in *xh*, you can generate the translated
version of the web site like so:

::

  po2html -i xh -t site -o site-xh

All the PO translations in *xh* will be converted to HTML using HTML files in
*site* as templates and outputting new translated HTML files in *site-xh*.

Should you prefer a single PO/POT file for your web site, you can create one
like so:

::

  html2po -P --multifile=onefile site file.pot

When po2html is invoked with a single PO file as input, and a directory of template
HTML files, it will produce one output file per template file. So to generate translated
output files from a single PO file, invoke po2html like so:

::

  po2html -i xh.po -t site -o site-xh

In this example, *xh.po* is the translation file for Xhosa, *site* is the directory where
the HTML files in the source language can be found, and *site-xh* is the directory where
the translated HTML files will end up.

.. _html2po#notes:

Notes
=====

The :doc:`HTML format description </formats/html>` gives more details on the 
format of the localisable HTML content and the capabilities of this converter.


.. _html2po#bugs:

Bugs
====

Some items end up in the msgid's that should not be translated
