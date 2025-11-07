
.. _xliff:

XLIFF
*****

XLIFF [#f1]_ is the `OASIS <https://www.oasis-open.org/>`_ standard for translation.

.. [#f1] XML Localization Interchange File Format

.. _xliff#versions:

Versions
========

The Translate Toolkit supports both XLIFF 1.x and XLIFF 2.0:

* **XLIFF 1.x** (1.1 and 1.2) - Available via ``translate.storage.xliff``
* **XLIFF 2.0** - Available via ``translate.storage.xliff2`` (added in version 3.17.0)

XLIFF 2.0 introduces significant structural changes compared to 1.x:

* Uses ``<unit>`` instead of ``<trans-unit>``
* Uses ``<segment>`` elements to contain source and target
* Different namespace: ``urn:oasis:names:tc:xliff:document:2.0``
* Simplified core with modular extensions
* Not backward compatible with XLIFF 1.x

References
----------
- `XLIFF 1.2 Standard
  <http://docs.oasis-open.org/xliff/xliff-core/xliff-core.html>`_
- `XLIFF 2.0 Standard
  <http://docs.oasis-open.org/xliff/xliff-core/v2.0/xliff-core-v2.0.html>`_
- `OASIS XLIFF Technical Committee
  <https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=xliff>`_ website

.. _xliff#flavours:

Flavours
========

XLIFF also has documents that specify the conversion from various standard
source documents and localisation formats.

* PO -- For conformance to the po2xliff spec, see :doc:`xliff2po
  </commands/xliff2po>`.

  * Draft `XLIFF 1.2 Representation Guide for Gettext PO
    <http://docs.oasis-open.org/xliff/v1.2/xliff-profile-po/xliff-profile-po-1.2.html>`_
* HTML -- not implemented

  * Draft `XLIFF 1.2 Representation Guide for HTML
    <http://docs.oasis-open.org/xliff/v1.2/xliff-profile-html/xliff-profile-html-1.2.html>`_
* Java (includes .properties and Java resource bundles) -- not implemented

  * Draft `XLIFF 1.2 Representation Guide for Java Resource Bundles
    <http://docs.oasis-open.org/xliff/v1.2/xliff-profile-java/xliff-profile-java-v1.2.html>`_
* ICU Resource Bundles -- not officially being developed by XLIFF -- Proposed
  `representation guide
  <http://www.icu-project.org/repos/icu/icuhtml/trunk/design/locale/xliff-profile-icuresourcebundle-1.2.htm>`_

.. _xliff#standard_conformance:

Standard conformance
====================

.. _xliff#done:

Done
----

* File creation and parsing
* API can create multiple files in one XLIFF (some tools only read the first
  file)
* source-language attribute
* trans-unit with
   * note: addnote() and getnotes()
   * state
      * fuzzy: isfuzzy() and markfuzzy()
      * translated: marktranslated()
      * approved
      * needs-review-translation: isreview(), markreviewneeded()
   * id: setid()
   * context-group: createcontextgroup()
* context groups
* alt-trans

.. _xliff#xliff_and_other_tools:

XLIFF and other tools
=====================

Here is a small report on :doc:`XLIFF support by Windows programs
<guide:guide/tools/xliff_support_by_ms_windows_programs>`.
