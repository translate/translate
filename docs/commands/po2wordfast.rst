
.. _po2wordfast#po2wordfast:

po2wordfast
***********

Convert Gettext PO files to a :doc:`/formats/wordfast` translation memory file.

`Wordfast <https://en.wikipedia.org/wiki/Wordfast>`_ is a popular Windows based computer-assisted translation tool.

.. _po2wordfast#usage:

Usage
=====

::

  po2wordfast [options] --language <target> <po> <wordfast>

Where:

| <po>  | a PO file or directory |
| <wordfast>  | a Wordfast translation memory file  |

Options:

| --version            | show program's version number and exit  |
| -h, --help           | show this help message and exit  |
| --manpage            | output a manpage based on the help  |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose  |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`  | show errorlevel as: none, message, exception, traceback  |
| -iINPUT, --input=INPUT   | read from INPUT in po, pot formats  |
| -xEXCLUDE, --exclude=EXCLUDE  | exclude names matching EXCLUDE from input paths  |
| -oOUTPUT, --output=OUTPUT     | write to OUTPUT in tmx format  |
| :doc:`--psyco=MODE <option_psyco>`         | use psyco to speed up the operation, modes: none, full, profile  |
| -lLANG, --language=LANG  | set target language code (e.g. af-ZA) [required]   |
| --source-language=LANG   | set source language code (default: en)  |

.. _po2wordfast#examples:

Examples
========

::

  po2wordfast -l xh-ZA browser.po browser.txt

Use the Xhosa (*xh-ZA*) translations in the PO file *browser.po* to create a Wordfast translation memory file called *browser.txt*

