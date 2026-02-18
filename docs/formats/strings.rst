
.. _strings:

Mac OSX strings
***************

.. versionadded:: 1.8

Mac OSX .strings files are used for some Cocoa / Carbon application
localization, such as for the iPhone, iPod, and OSX. They are somewhat similar
to Java properties, and therefore :doc:`prop2po </commands/prop2po>` and
po2prop are used for conversion.

This format is standardized as PWG 5100.13 and used on NeXTSTEP/OpenSTEP as well.

.. _strings#stringsdict:

.stringsdict format
===================

.. versionadded:: 3.14

The .stringsdict format is used by Apple for plural handling in iOS/macOS applications.
It stores plural rules using CLDR plural categories (zero, one, two, few, many, other)
in a plist (property list) format.

The Translate Toolkit supports .stringsdict files via ``translate.storage.stringsdict``.

Apple XLIFF variant
-------------------

Apple has also developed a custom XLIFF variant that encodes .stringsdict plural
information in XLIFF format. This is supported via ``translate.storage.applestrings_xliff``.
See :ref:`xliff#apple_xliff` for details.

.. _strings#references:

References
==========

* `Localising string resources
  <https://developer.apple.com/library/mac/#documentation/MacOSX/Conceptual/BPInternational/Articles/StringsFiles.html#//apple_ref/doc/uid/20000005-SW1>`_
* `Manual creation of .strings files
  <https://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/LoadingResources/Strings/Strings.html#//apple_ref/doc/uid/10000051i-CH6-SW10>`_
* `String format specifiers
  <https://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/Strings/Articles/formatSpecifiers.html>`_
