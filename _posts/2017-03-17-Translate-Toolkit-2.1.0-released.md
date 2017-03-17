---
title: Translate Toolkit 2.1.0 released
category: releases
---

It is 3 months since the last stable release and there are some improvements
across the board. This release contains such improvements and bug fixes. While
it contains many general improvements, it also specifically contains needed
changes and optimizations for the upcoming
[Pootle](http://pootle.translatehouse.org/) 2.8.0 and
[Virtaal](http://virtaal.translatehouse.org) releases.


Getting it and sharing it
=========================

- `pip install translate-toolkit`
- Please share this URL
  [http://toolkit.translatehouse.org/download.html](http://toolkit.translatehouse.org/download.html)
  if you'd like to tweet or post about the release.


Major changes
=============

- Fixed `RomanianChecker` checks.
- Added an iOS checker style.
- Changed plural equations for Slovenian, Persian, Kazakh and Kyrgyz.
- Several fixes in formats and tools.


Detailed changes
================

Python 3 support
----------------

- Python 3.6 is now supported.


Requirements
------------

- Updated and pinned requirements.
- Now recommended requirements pulls required requirements.


Formats and Converters
----------------------

- All formats

  - `locationindex` now uses first duplicate unit in case of several units
    having the same location in order to keep duplicate entries in some formats
    when converting from PO format.

- PO

  - Only add duplicate unit if `msgcxt` is unique, in order to be able to
    convert monolingual formats with duplicate entries to PO.

- Properties

  - Added support for Joomla dialect.

- ts

  - Set the right context on the units.

- YAML

  - Fixed parsing of unicode values in lists.

- HTML

  - Use character offset in line for unit location in order to keep parsing
    repeated strings in different units.

- txt

  - Use line number on unit location to keep parsing repeated strings in
    different units.


Filters and Checks
------------------

- Fixed `RomanianChecker` checks.
- Added an iOS checker style to detect iOS variables styles such as ``%@`` and
  ``$(VAR)``.


Tools
-----

- `posegment` no longer outputs duplicate headers


Languages
---------

- Changed plural equations for Slovenian, Persian, Kazakh and Kyrgyz.


Setup
-----

- Fixed Inno Setup builds allowing to easily install Translate Toolkit on
  Windows using the `pip` installer. Commands are compiled to .exe files.


API changes
-----------

- Changed management of Xapian locks to prevent database corruption.


General
-------

- Python 3 fixes
- Removed unused code


...and loads of general code cleanups and of course many many bugfixes.


Contributors
============

This release was made possible by the following people:

Dwayne Bailey, Leandro Regueiro, Michal Čihař, Ryan Northey, Friedel Wolff,
Olly Betts, Claude Paroz.

And to all our bug finders and testers, a Very BIG Thank You.
