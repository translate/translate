
.. _tmx:

TMX
***
TMX is the `LISA OSCAR standard
<https://www.gala-global.org/lisa-oscar-standards>`_ for translation memories.

.. _tmx#standard_conformance:

Standard conformance
====================

Summary: `TMX version 1.4
<https://www.gala-global.org/oscarStandards/tmx/tmx14b.html>`_ conformance to
Level 1, except that no markup is stripped.

* All required header fields are supplied.
* The ``adminlang`` field in the header is always English.
* None of the optional header fields are supplied.
* Multiple language variants are supported. Source variants are selected using
  the configured source language, a translation unit's ``srclang``, or the
  header's ``srclang``, in that order. Target variants can be selected by
  configuring a target language.
* No special consideration for segmentation.
* Currently text is treated as plain text, in other words no markup like HTML
  inside messages are stripped or interpreted as it should be for complete
  Level 1 conformance.

Language matching
=================

Language lookup first matches the requested code exactly, ignoring case and
``_`` versus ``-`` separators. If a bare language code has no exact match, its
Weblate language-data default-country variant is used when present. For example,
``en`` can select ``en-US`` and ``ko`` can select ``ko-KR``. An explicit ``en``
entry always takes precedence over ``en-US``.

Regional and script-qualified requests remain exact-only: ``en-GB`` does not
select ``en-US``, and ``en-US`` does not select ``en``. Unmatched languages remain
empty; target fallback does not reuse the source node for a distinct requested
language. Editing a matched language preserves its existing XML language tag.
