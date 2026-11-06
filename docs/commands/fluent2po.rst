
.. _fluent2po:
.. _po2fluent:

fluent2po
*********

Converts Fluent (.ftl) files to Gettext PO format, and back with ``po2fluent``.

`Fluent <https://projectfluent.org/>`_ is a monolingual localization format
used by Mozilla Firefox, Anki, and other projects.

.. _fluent2po#usage:

Usage
=====

::

  fluent2po [options] <ftl> <po>
  po2fluent [options] -t <ftl> <po> <ftl>

Where:

+--------+---------------------------------------------------+
| <ftl>  | is a valid .ftl file or directory of those files  |
+--------+---------------------------------------------------+
| <po>   | is a directory of PO or POT files                 |
+--------+---------------------------------------------------+

Options (fluent2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in Fluent format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in Fluent format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2fluent):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in ftl format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in ftl format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _fluent2po#examples:

Examples
========

This example shows how to convert Fluent files used in a project like Anki.

First, create POT files from the English templates::

  fluent2po -P templates/ pot/

All .ftl files found in the ``templates/`` directory are converted to Gettext
POT files and placed in the ``pot/`` directory. Fluent resource comments,
group comments and standalone comments are skipped; only translatable messages
and terms are extracted.

To recover existing translations, run::

  fluent2po -t templates/ ca/ po-ca/

Using the English Fluent files found in ``templates/`` and existing translated
Fluent files in ``ca/``, this creates a set of PO files in ``po-ca/``.
Messages are matched between template and translation using Fluent message IDs.

To update translations, regenerate POT files and use :doc:`pot2po` to bring
translations up to date.

Once translated, convert the PO files back to Fluent::

  po2fluent -t templates/ po-ca/ ca/

The English Fluent files in ``templates/`` provide the structure, comments and
message IDs; translations from ``po-ca/`` are matched using the PO locations
(``#: message-id``), falling back to ``msgctxt``. Untranslated messages, fuzzy
messages (unless ``--fuzzy`` is given), messages missing from the PO file and
translations that are not valid Fluent keep the template text.

.. _po2fluent#plurals:

Plurals
=======

fluent2po keeps select expressions as Fluent syntax in a single PO message, and
po2fluent copies such translations back unchanged.

PO files with gettext plurals (``msgid_plural`` and ``msgstr[n]``) are
converted to a Fluent select expression. The gettext forms are mapped to CLDR
plural categories by evaluating the ``Plural-Forms`` header on sample integers
and classifying the same integers with the CLDR plural rules of the PO
``Language``. When the header is missing or invalid, the plural forms known to
the toolkit for the language are used. For example, Ukrainian
(``nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 &&
(n%100<10 || n%100>=20) ? 1 : 2)``) gives:

.. code-block:: none

   emails =
       { $count ->
           [one] { $count } лист
           [few] { $count } листи
           [many] { $count } листів
          *[other] { $count } листи
       }

The selector is taken from the plural select expression of the template when
there is one, otherwise from the first variable of the PO strings, otherwise
``$count`` is used.

Fluent requires a default variant, which is always ``*[other]``. In languages
where CLDR ``other`` only applies to fractions (Belarusian, Polish, Russian,
Ukrainian), gettext has no matching form: Belarusian, Russian and Ukrainian
reuse the ``few`` form, as fractions take the genitive singular, which the
``few`` form mostly matches (``1,5 файла``); other languages reuse the last
gettext form. Other categories that only apply to fractions, such as ``many``
in Czech, are left to the default variant.

Languages with a single plural form produce a plain pattern without a select
expression.
