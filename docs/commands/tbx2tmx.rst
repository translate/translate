
.. _tbx2tmx:

tbx2tmx
*******

Convert :doc:`TBX </formats/tbx>` files to a :doc:`/formats/tmx`
translation memory file. TMX is the Translation Memory eXchange format;
see the `TMX 1.4b specification
<https://www.ttt.org/oscarStandards/tmx/tmx14b.html>`_.

.. _tbx2tmx#usage:

Usage
=====

::

  tbx2tmx [options] --language <target> <tbx> <tmx>

Where:

+-------+-----------------+
| <tbx> | is a TBX file   |
+-------+-----------------+
| <tmx> | is a TMX file   |
+-------+-----------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in tbx format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in tmx format
-lLANG, --language=LANG  set target language code (e.g. af-ZA) [required]
--source-language=LANG   set source language code (default: en)

.. _tbx2tmx#examples:

Examples
========

::

  tbx2tmx -l xh browser.tbx browser.tmx

Use the Xhosa (*xh*) translations in the TBX file *browser.tbx* to create a TMX
file called *browser.tmx*

Conversion details
==================

The source language defaults to English (``en``). Use ``--source-language`` to
select another language. The target language must be supplied with ``--language``.
Entries missing either selected language are skipped.

All nonempty, nondeprecated source and target terms in each concept are paired
with one another, producing one TMX translation unit per pair. Concept, language
and term notes are copied to the corresponding translation units. Terms are
exported as plain text, including the text inside inline XML elements.

A directory of TBX files can be combined into a single TMX file::

  tbx2tmx --source-language en -l cs tbx-directory glossary.tmx
