
.. _stringsdict:

Apple .stringsdict files
************************

.. versionadded:: 3.14

Apple .stringsdict files are used for plural handling in iOS/macOS applications.
The format stores plural rules using CLDR plural categories (zero, one, two, few,
many, other) in a plist (property list) format.

The Translate Toolkit supports .stringsdict files via
``translate.storage.stringsdict``.

Entries whose localized format is a direct reference to a single plural
variable are exposed as one plural unit. The variable name is included in the
unit identifier, for example ``items:count``. Entries containing literal text
in the localized format or multiple plural variables are exposed as separate
format and plural units.

Apple requires an ``other`` category in plural dictionaries. For languages
whose represented plural categories lack ``other`` (Russian, Polish, Ukrainian
and Belarusian), serialization copies the last category, ``many``, to ``other``.
This compatibility fallback keeps the existing plural counts and indexes.
An imported distinct ``other`` translation is not represented separately and
is regenerated from ``many`` on save. This also applies to fractional numeric
formats; the generated fallback may not provide correct fractional wording.
Folded entries with an empty fallback are omitted.

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
