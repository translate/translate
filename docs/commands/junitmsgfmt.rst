
.. _junitmsgfmt:

junitmsgfmt
***********

.. versionadded:: 3.9

Added --untranslated flag, to enable reporting of untranslated messages.

.. versionadded:: 1.7

Run msgfmt and provide JUnit type output for use in continuous integration
systems like Hudson and Jenkins.

.. _junitmsgfmt#usage:

Usage
=====

::

  junitmsgfmt po/*.po > msgfmt_junit.xml

