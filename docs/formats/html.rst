
.. _html:

HTML
****

The Translate Toolkit is able to process HTML files using the :doc:`html2po
</commands/html2po>` converter.


.. _html#conformance:

Conformance
===========

* Can identify almost all HTML elements and attributes that are localisable.

* The localisable and localised text in the PO/POT files is fragments of HTML.
  Therefore, reserved characters must be represented by HTML entities:

  - Content from HTML elements uses the HTML entities ``&amp;`` (&), ``&lt;``
    (<), and ``&gt;`` (>).

  - Content from HTML attributes uses the HTML entities ``&quot;`` (") or
    ``&apos;`` (').

* Leading and trailing tags are removed from the localisable text,
  but only in matching pairs.

* Can cope with embedded PHP, as long as the documents remain valid HTML. If
  you place PHP code inside HTML attributes, you need to make sure that the PHP
  doesn't contain special characters that interfere with the HTML.


.. _html#ignoring_content:

Ignoring Content from Translation
==================================

Two methods are available to exclude specific content from translation:

1. **data-translate-ignore attribute**

   Any HTML element with the ``data-translate-ignore`` attribute will have its
   content and all nested elements excluded from extraction.

   .. code-block:: html

      <p>This will be translated</p>
      <div data-translate-ignore>
          <p>This won't be translated</p>
          <p>Neither will this</p>
      </div>
      <p>This will be translated again</p>

   This is useful for:

   * Legal disclaimers that must remain in original language
   * Code examples or technical content
   * Brand names and trademarks
   * Copyright notices

2. **translate:off/on comment directives**

   Content between ``<!-- translate:off -->`` and ``<!-- translate:on -->``
   HTML comments will be excluded from extraction.

   .. code-block:: html

      <p>This will be translated</p>
      <!-- translate:off -->
      <div class="technical-content">
          <p>Technical documentation in English</p>
          <code>function example() { return "code"; }</code>
      </div>
      <!-- translate:on -->
      <p>This will be translated</p>

   This is useful for:

   * Temporarily disabling translation for sections during development
   * Excluding large blocks without modifying HTML attributes
   * Working with generated HTML where attributes can't be easily added

Both methods work with ``html2po`` extraction and ``po2html`` conversion,
preserving ignored content in the original language.


.. _html#references:

References
==========

* `Reserved characters
  <https://developer.mozilla.org/en-US/docs/Glossary/Entity>`__
* `Using character entities
  <http://www.w3.org/International/questions/qa-escapes>`__
