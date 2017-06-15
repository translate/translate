---
title: Translate Toolkit 2.2.0 released
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

- Avoid resolving external entities while parsing XML.
- Improvements for Android, ts and resx formats.
- Added support for PHP nested arrays.
- Added Kabyle language


Detailed changes
================

Requirements
------------

- Updated requirements.
- Added `pycountry` recommended requirement for localized language names.


Formats and Converters
----------------------

- XML formats

  - Avoid resolving external entities while parsing.

- Properties

  - Improved behavior for strings with no value.

- Android resources

  - Improved newlines handling.
  - Strip leading and trailing whitespace.

- PHP

  - Added support for nested named arrays and nested unnamed arrays.

- ts

  - Handle gracefully empty location tag.
  - Encode `po2ts` output as UTF-8.

- resx

  - Improved skeleton.
  - Fixed indent of the </data> elements.


Languages
---------

- Added Kabyle language.


API changes
-----------

- Added functions to retrieve language and country ISO names.
- If available, `pycountry` is used first to get language names translations.


General
-------

- Python 3 fixes
- Added more tests


...and loads of general code cleanups and of course many many bugfixes.


Contributors
============

This release was made possible by the following people:

Dwayne Bailey, Michal Čihař, Taras Semenenko, Leandro Regueiro, Rimas Kudelis,
BhaaL, Muḥend Belqasem, Jens Petersen.

And to all our bug finders and testers, a Very BIG Thank You.
