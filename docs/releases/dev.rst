Translate Toolkit 1.14.0
************************

*Not yet released*

This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes and
optimizations for the upcoming `Pootle <http://pootle.translatehouse.org/>`_
2.8.0 and `Virtaal <http://virtaal.translatehouse.org>`_ releases.

It is just over X months since the last release and there are many improvements
across the board.  A number of people contributed to this release and we've
tried to credit them wherever possible (sorry if somehow we missed you).

..
  This is used for the email and other release notifications
  Getting it and sharing it
  =========================
  * pip install translate-toolkit
  * Please share this URL http://toolkit.translatehouse.org/download.html if
    you'd like to tweet or post about the release.


1.14.0 vs 1.14.0-rc1
====================

- Support for new XXX format


Major changes
=============

- Python 3 compatibility
- Translate Toolkit can now easily be installed on Windows
- Changes in storage API to expose a more standardized API


Detailed changes
================

Python 3 support
----------------

- Translate Toolkit went through a massive code cleanup looking forward Python
  3 compatibility. There might be quirks that need to be fixed, so please test
  and `report any issue <https://github.com/translate/translate/issues/new>`_
  you might find.


Formats and Converters
----------------------

- PO

  - Duplicate entries are now removed by default if no way to handle
    duplicates is specified. Note that converters still default to `msgctxt`.

- Properties

  - Keys can contain delimiters if they are properly wrapped (:issue:`3275`).
  - Fix control characters escaping for utf-8 encoding.

- Android

  - Unknown locales no longer produce failures.

- JSON

  - Output now includes a trailing newline.
  - Unit ordering is maintanned (:issue:`3394`).

- TermBase eXchange (TBX)

  - :doc:`tbx2po </commands/tbx2po>` converter added
  - Added basic support for Parts of Speech and term definitions.


Filters and Checks
------------------

- LibreOffice checker no longer checks for Python brace format (:issue:`3303`).
- Numbers check now handles non latin numbers. Support for non latin numbers
  has been added for Arabic, Assamese, Bengali and Persian languages.
- Fixed issue that prevented standard checks from being used in Pootle with
  default settings.
- Fixed missing attribute warning displayed when using ``GnomeChecker``,
  ``LibreOfficeChecker`` and ``MozillaChecker`` checkers.


Tools
-----

- posegment now correctly segments Japanese strings with half width punctuation
  sign (:issue:`3280`).


Languages
---------

- Fixed plural form for Slovenian and Turkish.
- Added language settings for Brazilian Portuguese.


Setup
-----

- Fixed Inno Setup builds allowing to easily install Translate Toolkit on
  Windows using the ``pip`` installer. Commands are compiled to .exe files.


API changes
-----------

- Added encoding handling in base ``TranslationStore`` class exposing a single
  API.
- Encoding detection in ``TranslationStore`` has been improved.
- Standardized UnitClass definition across ``TranslationStore`` subclasses.


API deprecation
---------------

- ``TxtFile.getoutput()`` and ``dtdfile.getoutput()`` have been deprecated.
  Either call ``bytes(<file_instance>)`` or use the
  ``file_instance.serialize()`` API if you need to get the serialized store
  content of a ``TxtFile`` or ``dtdfile`` instance.


General
-------

- Misc docs cleanups.
- Added more tests.
- Legacy, deprecated and unused code cleansing:

  - Dropped code for no longer supported Python versions.
  - Removed unused code from various places across codebase.
  - The legacy ``translate.search.indexing.PyLuceneIndexer1`` was removed.
  - The deprecated ``translate.storage.properties.find_delimiter()`` was
    removed and replace by the
    ``translate.storage.properties.Dialect.find_delimiter()`` class method.
  - Python scripts are now available via `console_scripts` entry point, thus
    allowing to drop dummy files for exposing the scripts.


...and loads of general code cleanups and of course many many bugfixes.


Contributors
============

This release was made possible by the following people:

%CONTRIBUTORS%

And to all our bug finders and testers, a Very BIG Thank You.
