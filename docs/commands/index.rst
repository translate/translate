.. _commands:

.. _commands#converters:

Converters
**********

.. toctree::
   :maxdepth: 1
   :hidden:

   general_usage
   csv2po
   csv2tbx
   flatxml2po
   html2po
   ical2po
   ini2po
   json2po
   moz2po
   odf2xliff
   oo2po
   php2po
   po2tmx
   po2wordfast
   pot2po
   prop2po
   rc2po
   resx2po
   sub2po
   symb2po
   tbx2po
   tiki2po
   ts2po
   txt2po
   web2py2po
   xliff2po
   yaml2po

.. toctree::
   :maxdepth: 1
   :hidden:

   option_accelerator
   option_duplicates
   option_errorlevel
   option_filteraction
   option_multifile
   option_personality
   option_progress

Converters change many different formats to PO and back again. Sometimes only
one direction is supported, or conversion is done using non-PO formats.  The
converters follow a :doc:`general pattern of usage <general_usage>`,
understanding that will make the converters much easier to use and understand.

* :doc:`csv2po <csv2po>` -- Comma Separated Value (CSV) converter. Useful for
  doing translations using a spreadsheet.
* :doc:`csv2tbx <csv2tbx>` -- Create TBX (TermBase eXchange) files from Comma
  Separated Value (CSV) files
* :doc:`flatxml2po <flatxml2po>` -- Flat XML converter
* :doc:`html2po <html2po>` -- HTML converter
* :doc:`ical2po <ical2po>` -- iCalendar file converter
* :doc:`ini2po <ini2po>` -- Windows INI file converter
* :doc:`json2po <json2po>` -- JSON file converter
* :doc:`moz2po <moz2po>` -- Mozilla .properties and .dtd converter.  Works with
  Firefox and Thunderbird
* :doc:`odf2xliff <odf2xliff>` -- Convert OpenDocument (ODF) documents to XLIFF
  and vice-versa.
* :doc:`oo2po <oo2po>` -- OpenOffice.org SDF converter (Also works as
  ``oo2xliff``).
* :doc:`php2po <php2po>` -- PHP localisable string arrays converter.
* :doc:`po2tmx <po2tmx>` -- TMX (Translation Memory Exchange) converter
* :doc:`po2wordfast <po2wordfast>` -- Wordfast Translation Memory converter
* :doc:`pot2po <pot2po>` -- initialise PO Template files for translation
* :doc:`prop2po <prop2po>` -- Java property file (.properties) converter
* :doc:`rc2po <rc2po>` -- Windows Resource .rc (C++ Resource Compiler)
  converter
* :doc:`resx2po <resx2po>` -- .Net Resource (.resx) file converter
* :doc:`sub2po <sub2po>` -- Converter for various subtitle files
* :doc:`symb2po <symb2po>` -- Symbian-style translation to PO converter
* :doc:`tiki2po <tiki2po>` -- `TikiWiki <http://tikiwiki.org/>`_ language.php
  converter
* :doc:`ts2po <ts2po>` -- Qt Linguist .ts converter
* :doc:`txt2po <txt2po>` -- Plain text to PO converter
* :doc:`web2py2po` -- web2py translation to PO converter
* :doc:`xliff2po <xliff2po>` -- XLIFF (XML Localisation Interchange File
  Format) converter
* :doc:`yaml2po <yaml2po>` -- YAML (Yet Another Markup Language) converter


.. _commands#tools:

Tools
*****

The PO tools allow you to manipulate and work with PO files

.. _commands#quality_assurance:

Quality Assurance
=================

.. toctree::
   :maxdepth: 1
   :hidden:

   junitmsgfmt
   poconflicts
   pofilter
   pofilter_tests
   pogrep
   pomerge
   porestructure

These tools are especially useful for measuring and improving translation
quality.

* :doc:`junitmsgfmt` -- run msgfmt and provide JUnit type output for use in
  continuous integration systems like Hudson and Jenkins
* :doc:`poconflicts` -- extract messages that have conflicting translation
* :doc:`pofilter` -- filter PO files to find common errors using a :doc:`number
  of tests <pofilter_tests>`
* :doc:`pogrep` -- find strings in your PO files
* :doc:`pomerge` -- merge file extracted using pofilter back into the original
  files
* :doc:`porestructure` -- restructures PO files according to poconflict
  directives

.. _commands#other_tools:

Other tools
===========

.. toctree::
   :maxdepth: 1
   :hidden:

   levenshtein_distance
   option_rewrite
   poclean
   pocompile
   pocount
   podebug
   posegment
   poswap
   poterminology
   poterminology_stopword_file
   pretranslate
   tmserver

* :doc:`levenshtein_distance` -- edit distance algorithms for translation
  memory matching
* :doc:`poclean` -- produces a clean file from an unclean file
  (Trados/Wordfast) by stripping out the tw4win indicators
* :doc:`pocompile` -- create an MO (Machine Object) file from a PO or XLIFF
  file
* :doc:`pocount` -- Count words and strings in PO, XLIFF and other types of
  translatable files
* :doc:`podebug` -- Add debug strings to messages
* :doc:`posegment` -- Break a PO or XLIFF files into sentence segments, useful
  for creating a segmented translation memory
* :doc:`poswap` -- uses a translation of another language that you would rather
  use than English as source language
* :doc:`poterminology` -- extracts potential terminology from your translation
  files
* :doc:`pretranslate` -- fill any missing translations from translation memory
  via fuzzy matching.
* :doc:`tmserver` -- a Translation Memory server, can be queried over HTTP
  using JSON

.. _commands#scripts:

Scripts
*******

.. toctree::
   :maxdepth: 1
   :hidden:

   moz-l10n-builder
   mozilla_l10n_scripts
   phase
   pocommentclean
   pocompendium
   pomigrate2
   popuretext
   poreencode
   posplit

The scripts are for working with and manipulating PO files.  Unlike the
``tools`` which are written in Python, the scripts are written in ``bash``.
Some of them are packaged since version 1.0 of the Toolkit, but you might need
to download them from version control and do a manual installation .

* :doc:`moz-l10n-builder` -- Create Mozilla XPIs and rebuild Windows installers
  from existing translations
* :doc:`mozilla_l10n_scripts` -- Build Mozilla products Firefox and Thunderbird
* :doc:`phase` -- Helps manage a project divided into phases of work, including
  sending, checking, etc
* :doc:`pocompendium` -- Creates various types of PO compendium (i.e. combines
  many PO files into a single PO file)
* :doc:`pocommentclean` -- Remove all translator comments from a PO file
* :doc:`pomigrate2` -- Migrate older PO files to new POT files
* :doc:`popuretext` -- Extracts all the source text from a directory of POT
  files
* :doc:`poreencode` -- Converts PO files to a new character encoding
* :doc:`posplit` -- Split a PO file into translate, untranslated and fuzzy
  files
