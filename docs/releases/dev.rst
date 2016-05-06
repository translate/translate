Translate Toolkit dev
*********************

*Not yet released*

This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes and
optimizations for the upcoming `Pootle <http://pootle.translatehouse.org/>`_
2.8.0 and `Virtaal <http://virtaal.translatehouse.org>`_ releases.

It is just over X months since the last release and there are many improvements
across the board.  A number of people contributed to this release and we've
tried to credit them wherever possible (sorry if somehow we missed you).


dev vs 2.0.0b1
==============

- ``odf2xliff`` now extracts all the text (:issue:`3275`).


Major changes
=============

- Python 3 compatibility thanks to Claude Paroz
- Dropped support for Python 2.6
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
- Python 3.3-3.5 is now supported.


Formats and Converters
----------------------

- PO

  - Duplicate entries are now removed by default if no way to handle
    duplicates is specified. Note that converters still default to `msgctxt`.
  - msgid comments (KDE style) are only parsed from msgid now.

- DTD

  - Newlines are now skipped when parsing (:issue:`3390`).

- Properties

  - Keys can contain delimiters if they are properly wrapped (:issue:`3275`).
  - Fix control characters escaping for utf-8 encoding.

- Android

  - Unknown locales no longer produce failures.

- ODF

  - ``odf2xliff`` now extracts all the text (:issue:`3275`).

- JSON

  - Output now includes a trailing newline.
  - Unit ordering is maintained (:issue:`3394`).

- TermBase eXchange (TBX)

  - :doc:`tbx2po </commands/tbx2po>` converter added
  - Added basic support for Parts of Speech and term definitions.

- Fixed error when writing back to the same file (:issue:`3419`).


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

- Dropped ``translate.misc.dictutils.ordereddict`` in favor of
  ``collections.OrderedDict``.
- Added encoding handling in base ``TranslationStore`` class exposing a single
  API.
- Encoding detection in ``TranslationStore`` has been improved.
- Standardized UnitClass definition across ``TranslationStore`` subclasses.
- ``translate.misc.multistring.multistring``:

  - Fixed list coercion to text
  - Fixed comparison regression with multistrings (:issue:`3404`).
  - Re-added ``str`` method (:issue:`3428`).
  - Fixed ``__hash__`` (:issue:`3434`).


API deprecation
---------------

- Passing non-ASCII bytes to the ``multistring`` class has been deprecated, as
  well as the ``encoding`` argument to it.
  Applications should always construct ``multistring`` objects by passing
  characters (``unicode`` in Python 2, ``str`` in Python 3), not bytes. Support
  for passing non-ASCII bytes will be removed in the next version.
- ``TxtFile.getoutput()`` and ``dtdfile.getoutput()`` have been deprecated.
  Either call ``bytes(<file_instance>)`` or use the
  ``file_instance.serialize()`` API if you need to get the serialized store
  content of a ``TxtFile`` or ``dtdfile`` instance.


General
-------

- Dropped support for Python 2.6 since it is no longer supported by the Python
  Foundation. Sticking to it was making us difficult to maintain code while we
  move to Python 3.
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
