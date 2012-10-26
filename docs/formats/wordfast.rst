
.. _pages/toolkit/wordfast#wordfast_translation_memory:

Wordfast Translation Memory
***************************

The Wordfast format, as used by the `Wordfast <https://en.wikipedia.org/wiki/Wordfast>`_ translation tool, is a simple tab delimited file.

The storage format can read and write Wordfast TM files.

.. _pages/toolkit/wordfast#conformance:

Conformance
===========

* Escaping - The format correctly handles Wordfast ``&'XX;`` escaping and will unescape and escape seamlessly.
* Soft-breaks - these are not managed and are left as escaped
* Replaceables - these are not managed
* Header - Only basic updating and reading of the header is implemented
* Tab-separated value (TSV) - the format correctly handles the TSV format used by Wordfast.  There is no quoting, Windows newlines are used and the ``\t`` is used as a delimiter (see `bug 472 <http://bugs.locamotion.org/show_bug.cgi?id=472>`_)
