---
title: Translate Toolkit 2.2.3 released
category: releases
---

It is 5 days since the last stable release and there are some improvements
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

- Refactored functions for resolving language/country names translation to be
  memory efficient.
- Improvements for ts and subtitles formats.
- Added `--preserveplaceholders` argument to `podebug`.
- Fixed Montenegrin language name.


Detailed changes
================

Formats and Converters
----------------------

- ts

  - Write quotes as entities
  - Remove not necessary encoding/decoding to UTF-8


- Subtitles

  - Avoid errors when subtitle support is missing


Tools
-----

- Added `--preserveplaceholders` argument to `podebug` to avoid rewriting
  placeholders


Languages
---------

- Added `MinimalChecker` and `ReducedChecker` checkers.


Languages
---------

- Fixed Montenegrin language name.


API changes
-----------

- Refactored functions for resolving language/country names translation to be
  memory efficient


General
-------

- Use gzip for packaging
- Python 3 fixes
- Added more tests


...and loads of general code cleanups and of course many many bugfixes.


Contributors
============

This release was made possible by the following people:

Michal Čihař, Leandro Regueiro, Ryan Northey, Robbie Cole, Kai Pastor, Dwayne
Bailey.

And to all our bug finders and testers, a Very BIG Thank You.
