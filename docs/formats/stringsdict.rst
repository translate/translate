
.. _stringsdict:

Apple .stringsdict files
************************

.. versionadded:: 3.14

Apple .stringsdict files are used for plural handling in iOS/macOS applications.
The format stores plural rules using CLDR plural categories (zero, one, two, few,
many, other) in a plist (property list) format.

The Translate Toolkit supports .stringsdict files via
``translate.storage.stringsdict``.

.. seealso::

   :doc:`strings`
      Mac OSX .strings format used alongside .stringsdict files.

   :ref:`xliff#apple_xliff`
      Apple's XLIFF variant that encodes the same plural information in XLIFF
      format and is supported via ``translate.storage.applestrings_xliff``.

.. _stringsdict#references:

References
==========

* `Localizing String Resources with a Stringsdict File
  <https://developer.apple.com/documentation/xcode/localizing-string-resources-with-a-stringsdict-file>`_
* `NSStringLocalizedFormatKey
  <https://developer.apple.com/documentation/foundation/nsstringlocalizedformatkey>`_
