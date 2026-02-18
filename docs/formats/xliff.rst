
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

.. warning::

   XLIFF 2.0 is not compatible with XLIFF 1.x.

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

XLIFF 1.2 also has documents that specify the conversion from various standard
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

.. _xliff#apple_xliff:

Apple XLIFF
-----------

Apple has developed a custom variant of XLIFF 1.2 that encodes iOS/macOS .stringsdict
plural information directly in XLIFF trans-units. This format is supported via
``translate.storage.applestrings_xliff``.

The Apple XLIFF variant uses a special ID naming convention to represent plural forms:

* ``key:variable:dict`` - Marks a plural variable (source: ``NSStringPluralRuleType``)
* ``key:variable:dict/:string`` - Specifies the format value type (e.g., ``d`` for integer)
* ``key:variable:dict/PLURAL_FORM:dict/:string`` - Contains the actual plural form strings 
  (e.g., ``one``, ``other``, ``zero``)

Example
^^^^^^^

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
     <file original="Localizable.strings" source-language="en" target-language="en">
       <body>
         <!-- Plural variable marker -->
         <trans-unit id="items:count:dict">
           <source>NSStringPluralRuleType</source>
           <target>NSStringPluralRuleType</target>
         </trans-unit>
         
         <!-- Format type -->
         <trans-unit id="items:count:dict/:string">
           <source>d</source>
           <target>d</target>
         </trans-unit>
         
         <!-- Plural forms -->
         <trans-unit id="items:count:dict/one:dict/:string">
           <source>One item</source>
           <target>One item</target>
         </trans-unit>
         <trans-unit id="items:count:dict/other:dict/:string">
           <source>%d items</source>
           <target>%d items</target>
         </trans-unit>
       </body>
     </file>
   </xliff>

The Translate Toolkit can parse these plural forms and access them as multistring units,
similar to the .stringsdict format. Language detection from ``.lproj`` directories is
also supported (e.g., ``en.lproj``, ``Base.lproj``).

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
