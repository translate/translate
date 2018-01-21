
.. _catkeys:

Haiku catkeys
*************

.. versionadded:: 1.8

Localisation for the `Haiku <http://www.haiku-os.org/>`_ operating system is
done with a file format called catkeys.  It is a bilingual file format.

The is a tab separated value (TSV) file, where each line represents a
translatable unit. A line consists of four elements:

+------------+---------------------------------------------------------------+
| Column     | Description                                                   |
+============+===============================================================+
| source     | The source text (in English)                                  |
+------------+---------------------------------------------------------------+
| context    | The context of where the source text is used.                 |
+------------+---------------------------------------------------------------+
| remarks    | An additional remark by the developer, that gives a hint to   |
|            | the translator. Within the context of this toolkit, this is   |
|            | stored as the note of the unit.                               |
+------------+---------------------------------------------------------------+
| target     | The target text                                               |
+------------+---------------------------------------------------------------+

The first line of the file is the header file, with four tab separated values:

* The version (currently: 1)
* The name of the language in lower case (for example: catalan)
* The signature (for example: x-vnd.Haiku-StyledEdit)
* A checksum (32 bit unsigned integer)

The checksum is calculated by an algorithm that hashes the source, context and
remark values of all units. The target text is not relevant for the checksum
algorithm.

.. _catkeys#links:

Links
=====

* `Some notes about the format
  <http://www.haiku-os.org/blog/pulkomandy/2009-09-24_haiku_locale_kit_translator_handbook>`_
* `Some example files
  <http://cgit.haiku-os.org/haiku/tree/data/catalogs/>`_
