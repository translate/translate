---
title: Translate Toolkit 2.2.4 released
category: releases
---

It is 41 days since the last stable release and there are some improvements
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


Changes
=======

Formats and Converters
----------------------

- XLIFF

  - Added support for `.xliff` extension in all converters and tools that
    support `.xlf` extension.

- JSON

  - Added support for nested JSON.
  - Added support for WebExtension JSON dialect.

- txt

  - `po2txt` skips obsolete and non-translatable strings.


Filters and Checks
------------------

- The `puncspace` check now strips Bidi markers chars before processing.
- Added `ReducedChecker` checker to list of checkers.


API changes
-----------

- Language and country default to `common_name` if available.
- Added function to retrieve all language classes.


...and loads of general code cleanups and of course many many bugfixes.


Contributors
============

This release was made possible by the following people:

Dwayne Bailey, Leandro Regueiro, Michal Čihař, Rimas Kudelis, Ludwig Nussel,
Stuart Prescott.

And to all our bug finders and testers, a Very BIG Thank You.
