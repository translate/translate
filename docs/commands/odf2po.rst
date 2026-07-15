.. _odf2po:
.. _po2odf:

odf2po and po2odf
*****************

Convert OpenDocument (ODF) packages to Gettext PO localization files, and
create translated ODF packages from those PO files.

Usage
=====

::

  odf2po [options] <original_odf> <po>
  po2odf [options] -t <original_odf> <po> <translated_odf>

For example::

  odf2po english.odt english_french.po
  po2odf -t english.odt english_french.po french.odt

The PO references identify both the XML path and package member for each
message. Keep these references intact: ``po2odf`` uses them to put translations
back into the right paragraph, style, metadata, or embedded ODF object.
Repeated messages are disambiguated with location-based PO contexts.

Inline ODF markup is represented by XLIFF-style ``<g>`` and ``<x>``
placeables in PO messages. Translators should preserve their identifiers.
Empty and fuzzy PO translations leave the corresponding template content
unchanged.
