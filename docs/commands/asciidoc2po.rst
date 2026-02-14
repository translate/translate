
.. _asciidoc2po:
.. _po2asciidoc:

asciidoc2po, po2asciidoc
************************

Convert translatable items in AsciiDoc text to the PO format. Insert translated text into AsciiDoc templates.

.. _asciidoc2po#usage:

Usage
=====

::

  asciidoc2po [options] <asciidoc-src> <po>
  po2asciidoc [options] -i <po> -t <asciidoc-src> -o <asciidoc-dest>

Where:

+------------------+--------------------------------------------------------------------------------------------+
| <asciidoc-src>   | is an AsciiDoc file or a directory of AsciiDoc files, source language                      |
+------------------+--------------------------------------------------------------------------------------------+
| <asciidoc-dest>  | is an AsciiDoc file or a directory of AsciiDoc files, translated to the target language    |
+------------------+--------------------------------------------------------------------------------------------+
| <po>             | is a PO file or directory of PO files                                                      |
+------------------+--------------------------------------------------------------------------------------------+

Options (asciidoc2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in AsciiDoc format
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


Options (po2asciidoc):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in AsciiDoc format
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in AsciiDoc format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)


.. _asciidoc2po#examples:

Examples
========

::

  asciidoc2po -P source-adoc-dir pot

This will find all AsciiDoc files (.adoc, .asciidoc, .asc) in
*source-adoc-dir*, convert them to POT files (that is, extract all translatable
content) and place them in *pot*.

See the :doc:`pot2po` command for more information about how to create PO files
from the POT files, and to update existing PO files when the POT files have
changed.

Suppose you have created PO files for translation to Xhosa and placed them in
the directory *xh*. You can then generate the translated version of the AsciiDoc
documents like so:

::

  po2asciidoc -i xh -t source-adoc-dir -o xh-adoc-dir

All the PO translations in *xh* will be converted to AsciiDoc using AsciiDoc
files in *source-adoc-dir* as templates and outputting new translated AsciiDoc
files in *xh-adoc-dir*.

Should you prefer a single PO/POT file for your collection of AsciiDoc files,
this is how to do it:

::

  asciidoc2po -P --multifile=onefile source-adoc-dir file.pot

And similarly, to generate multiple translated output files from a single PO
file, invoke po2asciidoc like so:

::

  po2asciidoc -i xh.po -t source-adoc-dir -o xh-adoc-dir

In this example, *xh.po* is the translation file for Xhosa, *source-adoc-dir* is
the directory where the AsciiDoc files in the source language can be found, and
*xh-adoc-dir* is the directory where the translated AsciiDoc files will end up.

.. _asciidoc2po#notes:

Notes
=====

The :doc:`AsciiDoc format description </formats/asciidoc>` gives more details on the
format of the localisable AsciiDoc content and the capabilities of this converter.

When translating AsciiDoc documentation, it's recommended to:

* Preserve inline formatting markers like \*bold\*, \_italic\_, and \`monospace\`
* Keep admonition types (NOTE, TIP, etc.) in their original language or translate
  them consistently
* Test the translated output with asciidoctor to ensure proper rendering
* Be aware that some complex AsciiDoc features (like include directives) are
  preserved but not translated

The converter handles document headers (title, author, attributes) specially -
they are preserved but not extracted for translation. This ensures that document
metadata remains consistent across language versions.
