
.. _asciidoc:

AsciiDoc
********

The Translate Toolkit is able to process AsciiDoc files using the :doc:`asciidoc2po
</commands/asciidoc2po>` converter.


.. _asciidoc#conformance:

Conformance
===========

* Parses common AsciiDoc syntax elements for translation.

* Capable of handling nested containers, such as lists in lists, and other
  AsciiDoc features.

* Aims to extract all content relevant for translation, at the cost of also
  including some formatting. For example, \*bold text\* and \`monospace\`
  is included in the text to be translated.

* Aims to preserve formatting as far as possible during round-trip conversion.

* One translation unit per logical element (paragraph, heading, list item, etc.).

* Preserves document structure including block delimiters, attributes, and directives.


.. _asciidoc#supported_features:

Supported Features
==================

The AsciiDoc converter supports the following elements:

**Document Structure:**

* Document headers (preserved but not translated)
* Section headings at all levels (==, ===, etc.)
* Paragraphs with normalized whitespace

**Lists:**

* Unordered lists (*)
* Ordered lists (.)
* Description lists (term:: definition)
* Checklists ([*], [x], [ ])
* Nested lists
* List continuation markers (+)

**Block Elements:**

* Code blocks (----)
* Literal blocks (....)
* Example blocks (====)
* Sidebar blocks (****)
* Comment blocks (////)
* Quote blocks (____)
* Passthrough blocks (++++)

**Inline and Special Elements:**

* Admonitions (NOTE, TIP, WARNING, IMPORTANT, CAUTION)
* Simple tables (pipe-separated cells)
* Attribute lines (e.g., [NOTE], [source,java])
* Conditional blocks (ifdef, ifndef, ifeval, endif)
* Anchors ([[anchor-id]])
* Block titles (.Title)
* Comments (// and ////)

**Preserved Elements:**

* Include directives (not translated)
* All block delimiter markers
* Attribute definitions
* Conditional directives
* Anchors and cross-references
* Comment blocks


.. _asciidoc#limitations:

Limitations
===========

* Table parsing is limited to simple pipe-separated format. Does not support:
  
  * Cell spanning
  * CSV-formatted tables
  * PSV-formatted tables (colon-separated)
  * Complex table layouts with merged cells

* Inline HTML and other complex inline elements are preserved but treated as
  part of the translatable text.

* Does not validate that translated text maintains the same AsciiDoc formatting
  as the source.

* Block delimiters must use consistent delimiter characters (e.g., ====, not
  ===== of different lengths).


.. _asciidoc#best_practices:

Best Practices
==============

* Use standard AsciiDoc syntax for best compatibility.

* Keep list items concise for easier translation.

* Use admonitions consistently (NOTE, TIP, etc.).

* Avoid mixing different list types within the same list structure.

* Test translated documents with asciidoctor to ensure proper rendering.


.. _asciidoc#references:

References
==========

* `The AsciiDoc Language Documentation
  <https://docs.asciidoctor.org/asciidoc/latest/>`__
* `Asciidoctor User Manual
  <https://docs.asciidoctor.org/asciidoctor/latest/>`__
* `AsciiDoc Quick Reference
  <https://docs.asciidoctor.org/asciidoc/latest/syntax-quick-reference/>`__
