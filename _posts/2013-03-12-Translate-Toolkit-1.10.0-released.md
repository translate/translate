---
title: Translate Toolkit 1.10.0 released
category: releases
---
This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes for the
upcoming [Pootle](http://pootle.translatehouse.org/) 2.5.0.

It is just over a year since the last release so there are many improvements
across the board.  A number of people contributed to this release and we've
tried to credit them wherever possible (sorry if somehow we missed you).


Highlighted improvements
========================
* Android format support
* Version control improvements
* Source now on Github - all our code is now on github
* Documentation - migrated all from our wiki into the code and Read The Docs
* Continuous Integration using Travis


Most important for Pootle
-------------------------
* Version control improvements
* Categorize pofilter checks into critical, functional, cosmetic, etc


Formats and Converters
----------------------
* Android format support \[Michal Čihař\]
* Mozilla .lang, many improvements
* PHP support for defintions, // comments and improved whitespace preservation
* PO: X-Merge-On header to explicitly demand a conversion strategy instead of
  guessing
* .properties: BOMs in messages and C style comments \[Roman Imankulov\]
* Mac OS String formatting imporved \[Roman Imankulov\]


Version Control improvements
----------------------------
* Interface for adding files to a repository & Implement .add() for all VCSs.
* Caching of VC version info
* Don't look for VCS if it snot available
* Stop looking for VCS at a given parent
* Subversion VC tests
* Alway pass -m to 'commit' in Subversion to prevent blocking


Checks
------
* New OpenOffice variables style used in extensions
* Check for self-closing tags in the xmltags test \[Seb M\].
* GConf test fixes
* Terminology checker type for future terminology features
* Categorize pofilter checks into critical, functional, cosmetic, etc
* Added support for Objective-C %@ printf specifiers


Language specific fixes
-----------------------
* Correct plurals: Scottish Gaelic (gd), Irish
* Plural rules: Fulah, Brazilian Portuguese
* Punctuation rules and tests to ignore for: Burmese, Urdu, Afrikaans, Wolof


Documentation
-------------
* Moved to Git and we are now using reStructured Text and Sphinx
* Published in Read The Docs (RTD).
* Old wiki migrated to RTD.
* New clean theme for documentation and website
* API and code epydoc moved to reStructured Text.
* Translate code Style Guide written


Mozilla tooling fixes
---------------------
* Mozilla specific test for dialog size settings
* Gaia properties dialect and plural handling
* Fixes and imporovement to the Firefox build scripts
* Improved accesskey detection
* Improved DTD escaping for &quote, %, etc
* Improvement of DTD to align with Base classes
* Support new {{xx}} variable style introduced in PDF viewer


...and refactoring, PEP8, test coverage and of course many many bugfixes.


Contributors
------------
This release was made possible by the following people:

Dwayne Bailey, Friedel Wolff, Leandro Regueiro, Julen Ruiz Aizpuru,
Michal Čihař, Roman Imankulov, Alexander Dupuy, Frank Tetzel,
Luiz Fernando Ranghetti, Laurette Pretorius, Jiro Matsuzawa, Henrik Saari,
Luca De Petrillo, Khaled Hosny, Dave Dash & Chris Oelmueller.

And to all our bug finder, testers and
[localisers](http://pootle.locamotion.org/projects/pootle/), a Very BIG Thank
You.
