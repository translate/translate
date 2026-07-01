
.. _mdx:

MDX
***

The Translate Toolkit is able to process MDX files using the :doc:`mdx2po
</commands/mdx2po>` converter.

MDX is Markdown with JSX — it extends standard Markdown with the ability to
embed JSX components, import/export statements, and JavaScript expressions.
See `What is MDX? <https://mdxjs.com/docs/what-is-mdx/>`__ for background.


.. _mdx#conformance:

Conformance
===========

* Extends the :doc:`Markdown <md>` parser with MDX-specific pre-processing.

* Uses the CommonMark-compliant mistletoe parser for the Markdown portions.

* Import and export statements at the top level are preserved verbatim and
  are not extracted for translation.

* The MDX-specific extractor intentionally recognizes only JSX components that
  begin at column zero and occupy complete physical lines. Component names must
  start with an uppercase letter, and component blocks must be separated from
  surrounding Markdown by blank lines.

* Simple boolean and quoted string attributes on one-line component tags are
  supported. Quoted values are extracted for translation, for example
  ``<Step title="Open" />`` or ``<Callout title="Warning">``.

* Markdown children are extracted only when a supported one-line opening tag
  and its matching closing tag are separate, column-zero lines and the child
  block contains no JSX, raw HTML, JavaScript expressions, or top-level ESM
  outside fenced code blocks. The child is parsed as an isolated Markdown
  document and its common indentation is restored after translation.

* Syntax requiring JSX or JavaScript parsing is deliberately opaque. This
  includes multiline tags, expression or spread attributes, same-line children,
  nested components, fragments, and component-like literals in child content.
  Such syntax is preserved without partial extraction when it forms a
  blank-delimited block. Same-name nesting is recognized only on complete
  physical lines.

* Brace-containing paragraphs and standalone JavaScript expressions are
  preserved without attempting to balance JavaScript tokens. Top-level import
  and export statements are preserved through the next blank line.

* Inline JSX and JSX after Markdown container markers are not interpreted by
  the MDX-specific extractor. They remain subject to the inherited Markdown
  handling and their attributes are not separately extracted.

* Regular Markdown content between JSX blocks is extracted for translation
  in the same way as the plain Markdown converter.

* Inherits all Markdown conformance properties: placeholder-based inline
  element handling, optional code block extraction, optional front matter
  extraction, and maximum line length reflowing in ``po2mdx``.

* Does not provide dedicated embedded HTML extraction; HTML handling is
  inherited from the Markdown parser.

* Does not perform any checks that the translated text has the same formatting
  as the source.


.. _mdx#excluding_content:

Excluding Content from Translation
===================================

Supports the same ``<!-- translate:off -->`` / ``<!-- translate:on -->``
exclusion mechanism as the Markdown converter.


.. _mdx#references:

References
==========

* `MDX documentation <https://mdxjs.com/>`__
* `The CommonMark specification <https://spec.commonmark.org/>`__
* `The mistletoe parser <https://github.com/miyuchina/mistletoe>`__
