.. These notes are used in:
   1. Our email announcements
   2. The Translate Tools download page at toolkit.translatehouse.org

Translate Toolkit 1.13.0
************************

*Not yet released*

This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes and
optimizations for the upcoming `Pootle <http://pootle.translatehouse.org/>`_
2.6.0 and `Virtaal <http://virtaal.translatehouse.org>`_ releases.

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


Highlighted improvements
========================

Major changes
-------------

- Code cleanup looking forward Python 3 compatibility


Formats and Converters
----------------------

- Removed the :option:`--engine` option from the :command:`odf2xliff` command.
  This is a consequence of stop using the `itools` third party library in favor
  of custom code.


General
-------

- Misc docs cleanups


...and loads of general code cleanups and of course many many bugfixes.


Contributors
------------

This release was made possible by the following people:

%CONTRIBUTORS%

And to all our bug finders and testers, a Very BIG Thank You.
