
.. _mdx2po:
.. _po2mdx:

mdx2po, po2mdx
**************

Convert translatable items in MDX files to the PO format. Insert translated
text into MDX templates.

MDX is Markdown with JSX support. JSX components, imports, exports, and
JavaScript expressions are preserved verbatim; regular Markdown content between
them is extracted for translation.

.. _mdx2po#usage:

Usage
=====

::

  mdx2po [options] <mdx-src> <po>
  po2mdx [options] -i <po> -t <mdx-src> -o <mdx-dest>

Where:

+------------+-----------------------------------------------------------------------------------------+
| <mdx-src>  | is an MDX file or a directory of MDX files, source language                             |
+------------+-----------------------------------------------------------------------------------------+
| <mdx-dest> | is an MDX file or a directory of MDX files, translated to the target language           |
+------------+-----------------------------------------------------------------------------------------+
| <po>       | is a PO file or directory of PO files                                                   |
+------------+-----------------------------------------------------------------------------------------+

Options (mdx2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in MDX format
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
--no-code-blocks     do not extract code blocks for translation
--no-frontmatter     do not extract front matter for translation
--no-placeholders    render inline elements verbatim instead of {n} placeholder markers


Options (po2mdx):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT  write to OUTPUT in MDX format
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in MDX format
-S, --timestamp      skip conversion if the output file has newer timestamp
-m MAXLENGTH, --maxlinelength=MAXLENGTH
                      reflow (word wrap) the output to the given maximum
                      line length. set to 0 to disable
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)
--no-code-blocks     do not extract code blocks for translation
--no-frontmatter     do not extract front matter for translation
--no-placeholders    render inline elements verbatim instead of {n} placeholder markers


.. _mdx2po#examples:

Examples
========

::

  mdx2po -P source-mdx-dir pot

This will find all MDX files (``.mdx``) in *source-mdx-dir*, convert them to
POT files (extract all translatable content) and place them in *pot*.

See the :doc:`pot2po` command for more information about how to create PO files
from the POT files, and to update existing PO files when the POT files have
changed.

Suppose you have created PO files for translation to Xhosa and placed them in
the directory *xh*. You can then generate the translated version of the MDX
documents like so:

::

  po2mdx -i xh -t source-mdx-dir -o xh-mdx-dir

All the PO translations in *xh* will be converted to MDX using MDX files in
*source-mdx-dir* as templates and outputting new translated MDX files in
*xh-mdx-dir*.

Should you prefer a single PO/POT file for your collection of MDX files, this
is how to do it:

::

  mdx2po -P --multifile=onefile source-mdx-dir file.pot

And similarly, to generate multiple translated output files from a single PO
file, invoke po2mdx like so:

::

  po2mdx -i xh.po -t source-mdx-dir -o xh-mdx-dir

In this example, *xh.po* is the translation file for Xhosa, *source-mdx-dir*
is the directory where the MDX files in the source language can be found, and
*xh-mdx-dir* is the directory where the translated MDX files will end up.

.. _mdx2po#notes:

Notes
=====

The :doc:`MDX format description </formats/mdx>` gives more details on the
format of the localisable MDX content and the capabilities of this converter.
