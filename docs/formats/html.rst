
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


.. _html#adding_context:

Adding Translator Context
==========================

Translators often need additional context to provide accurate translations. The
Translate Toolkit supports adding translator comments using the
``data-translate-comment`` HTML5 data attribute.

**data-translate-comment attribute**

Any HTML element can have a ``data-translate-comment`` attribute to provide
context for translators. These comments are extracted as automatic comments
(marked with ``#.``) when using the ``--keepcomments`` option with ``html2po``.

.. code-block:: html

   <h1 data-translate-comment="This is the first text that is displayed">Hello world!</h1>
   <p data-translate-comment="Welcome message for visitors">Welcome to our site!</p>
   <button data-translate-comment="Primary call-to-action button">Sign Up Now</button>

When extracted with ``html2po --keepcomments``, these generate PO files like:

.. code-block:: po

   #. This is the first text that is displayed
   #: example.html+h1:1-1
   msgid "Hello world!"
   msgstr ""

   #. Welcome message for visitors
   #: example.html+p:2-1
   msgid "Welcome to our site!"
   msgstr ""

   #. Primary call-to-action button
   #: example.html+button:3-1
   msgid "Sign Up Now"
   msgstr ""

This is useful for:

* Explaining character limits or formatting requirements
* Providing UI context (e.g., "Button text", "Error message")
* Clarifying ambiguous terms or technical jargon
* Indicating target audience or tone
* Documenting brand names that should not be translated

The ``data-translate-comment`` attribute works alongside regular HTML comments
(``<!-- comment -->``). Both are extracted and combined when using
``--keepcomments``, giving translators comprehensive context.

.. note::

   The ``data-translate-comment`` attribute uses the HTML5 `data-* attribute
   specification <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/data-*>`_,
   which is designed for custom data that doesn't affect rendering. This means
   your HTML remains valid and the attributes are safely ignored by browsers.


.. _html#meta_tags:

Translatable Meta Tags
======================

The HTML converter automatically extracts content from meta tags that are
suitable for translation, including social media meta tags used by platforms
like Facebook, Twitter, and LinkedIn.

**Standard Meta Tags**

* ``<meta name="description" content="...">`` - Page description
* ``<meta name="keywords" content="...">`` - Keywords

**Open Graph Meta Tags** (for Facebook, LinkedIn, etc.)

* ``<meta property="og:title" content="...">`` - Page title for social sharing
* ``<meta property="og:description" content="...">`` - Page description for social sharing
* ``<meta property="og:site_name" content="...">`` - Site name

**Twitter Card Meta Tags**

* ``<meta name="twitter:title" content="...">`` - Page title for Twitter cards
* ``<meta name="twitter:description" content="...">`` - Page description for Twitter cards

**Non-Translatable Meta Tags**

The following meta tags are intentionally **not** extracted for translation as
they contain URLs, images, or technical values:

* ``og:url``, ``og:image``, ``og:type`` - URLs and content types
* ``twitter:card``, ``twitter:image``, ``twitter:site`` - Technical settings and URLs
* ``viewport``, ``charset``, ``http-equiv`` - Technical HTML settings

Example
-------

.. code-block:: html

   <head>
       <meta name="description" content="Learn about our products">
       <meta property="og:title" content="Our Amazing Products">
       <meta property="og:description" content="Discover quality products">
       <meta property="og:image" content="https://example.com/image.jpg">
       <meta name="twitter:title" content="Our Amazing Products">
   </head>

When extracted with ``html2po``, the translatable strings will be:

* "Learn about our products"
* "Our Amazing Products"
* "Discover quality products"

The ``og:image`` URL is preserved as-is and not extracted for translation.

After translation with ``po2html``, social media platforms will display the
translated title and description when users share links to your website.


.. _html#references:

References
==========

* `Reserved characters
  <https://developer.mozilla.org/en-US/docs/Glossary/Entity>`__
* `Using character entities
  <http://www.w3.org/International/questions/qa-escapes>`__
