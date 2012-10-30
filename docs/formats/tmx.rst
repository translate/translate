
.. _tmx:

TMX
***
TMX is the LISA standard for translation memories. See http://www.lisa.org/standards/tmx.

.. _tmx#standard_conformance:

Standard conformance
====================

Summary: TMX version 1.4 conformance to Level 1, except that no markup is stripped.

* All required header fields are supplied.
* The adminlang field in the header is always English.
* None of the optional header fields are supplied.
* We assume that only two languages are used (source and single target language).
* No special consideration for segmentation.
* Currently text is treated as plain text, in other words no markup like HTML inside messages are stripped or interpreted as it should be for complete Level 1 conformance.
