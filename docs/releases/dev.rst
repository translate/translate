.. These notes are used in:
   1. Our email announcements
   2. The Translate Tools download page at toolkit.translatehouse.org

Translate Toolkit 1.14.0-rc1
****************************

*Not yet released*

This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes and
optimizations for the upcoming `Pootle <http://pootle.translatehouse.org/>`_
X and `Virtaal <http://virtaal.translatehouse.org>`_ releases.

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

- Python 3 support


Formats and Converters
----------------------

- Properties

   - keys can contain delimiters if they are properly wrapped (:issue:`3275`).


Filters and Checks
------------------

- Numbers check now handles non latin numbers.


API deprecation
---------------

- The deprecated ``translate.storage.properties.find_delimiter()`` was removed
  and replace by the ``translate.storage.properties.Dialect.find_delimiter()``
  class method.

- ``TxtFile.getoutput()`` and ``dtdfile.getoutput()`` have been deprecated.
  Either call ``bytes(<file_instance>)`` or use the
  ``file_instance.serialize()`` API if you need to get the serialized store
  content of a ``TxtFile`` or ``dtdfile`` instance.


General
-------

- Misc docs cleanups


...and loads of general code cleanups and of course many many bugfixes.


Contributors
------------

This release was made possible by the following people:

%CONTRIBUTORS%

And to all our bug finders and testers, a Very BIG Thank You.
