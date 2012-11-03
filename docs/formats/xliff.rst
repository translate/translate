
.. _xliff:

XLIFF
*****

XLIFF is the OASIS standard for translation. See
http://www.oasis-open.org/committees/xliff/documents/xliff-specification.htm.

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
      * needs-review-transaltion: isreview(), markreviewneeded()
   * id: setid()
   * context-group: createcontextgroup()
* context groups
* alt-trans

.. _xliff#xliff_and_other_tools:

XLIFF and other tools
=====================

Here is a small report on the :doc:`guide/tools/xliff support by ms windows
programs`.
