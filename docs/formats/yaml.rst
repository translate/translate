.. _yaml:


YAML
====

.. versionadded:: 2.0.0

:wp:`YAML` is a common format for web data interchange. The two variants of
YAML files are supported:

* Plain YAML files.
* Ruby YAML localization files with root node as language. This variant
  supports plurals as well.


Ruby plural mappings expose explicit string values through ``plural_forms``.
YAML null values remain untranslated placeholders. An empty string is an
explicit translation.

.. _yaml#non-conformance:

Non-Conformance
===============

The following are not yet supported (in most cases these are properly parsed,
but not saved in round trip):

* Booleans:

  .. code-block:: yaml

      foo: True

When importing Ruby YAML translations from PO, the catalog's ``Plural-Forms``
header determines the order of translated values. The converter compares
integer examples against the locale's gettext rule. If that rule is unavailable
or its categories do not match the declared indexes, the converter tries Babel's
CLDR cardinal rule. It raises an error if it cannot identify a distinct category
for every declared index. Without a header it uses the locale default.
Untranslated entries use the PO singular and plural source strings.
