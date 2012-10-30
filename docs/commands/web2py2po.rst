
.. _py2web2po#web2py2po:

web2py2po
*********

Converts web2py translation files to PO files and vice versa.

`Web2py <http://mdp.cti.depaul.edu>`_, formerly known as Gluon) is an open-source, Python-based web application framework by Massimo Di Pierro (inspired by Django and Rails).

Web2py uses an internal localization engine based on Python dictionaries, which is applied with the T() lookup function. Web2py provides a built-in translation interface for the T()-engine, which is excellent for rapid application development.

On the other hand, for collaboration and workflow control in a wider community you might probably rather want to use Pootle, Launchpad or similar facilities for translation, thus need to transform the web2py dictionaries into PO files and vice versa. And exactly that is what the web2py2po converters are good for.

.. _py2web2po#usage:

Usage
=====

::

  web2py2po [options] <web2py> <po>
  po2web2py [options] <po> <web2py>

Where:

| <web2py> | is a valid web2py translation file |
| <po>   | is a PO or POT file or a directory of PO or POT files  |

Options (web2py2po):

| --version           | show program's version number and exit  |
| -h, --help          | show this help message and exit  |
| --manpage           | output a manpage based on the help  |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose  |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`  | show errorlevel as: none, message, exception, traceback   |
| -i INPUT, --input=INPUT      | read from INPUT in php format  |
| -x EXCLUDE, --exclude=EXCLUDE  | exclude names matching EXCLUDE from input paths   |
| -o OUTPUT, --output=OUTPUT     | write to OUTPUT in po, pot formats  |
| :doc:`--psyco=mode <option_psyco>`  | use psyco to speed up the operation, modes: none,                        full, profile  |

Options (po2web2py):

| --version            | show program's version number and exit  |
| -h, --help           | show this help message and exit  |
| --manpage            | output a manpage based on the help  |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose  |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`    | show errorlevel as: none, message, exception, traceback  |
| -i INPUT, --input=INPUT  | read from INPUT in po, pot formats  |
| -x EXCLUDE, --exclude=EXCLUDE   | exclude names matching EXCLUDE from input paths  |
| -o OUTPUT, --output=OUTPUT      | write to OUTPUT in php format  |
| :doc:`--psyco=mode <option_psyco>`         | use psyco to speed up the operation, modes: none, full, profile  |
| --fuzzy %%|%% --nofuzzy     | include%%|%%exclude fuzzy translations  |

.. _py2web2po#notes:

Notes
=====

**Handling of blanks/untranslated messages:**

Untranslated messages in the web2py translation files are usually marked with a leading ``%%"*** "%%``, so:

* All target strings from the web2py sources with a leading ``%%"*** "%%`` are inserted as blank msgstr's into the PO result (web2py2po)
* Blank msgstr's from the PO file will get the msgid string with a leading ``%%"*** "%%`` as target string in the web2py result (po2web2py)
