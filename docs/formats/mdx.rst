
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

* Block-level JSX components (tags starting with an uppercase letter, e.g.
  ``<Alert>``, ``<Tabs>``) are preserved verbatim. Their inner content is
  *not* separately extracted for translation.

* Inline JSX expressions such as ``{variable}`` at the block level are
  preserved verbatim.

* Regular Markdown content between JSX blocks is extracted for translation
  in the same way as the plain Markdown converter.

* Inherits all Markdown conformance properties: placeholder-based inline
  element handling, optional code block extraction, optional front matter
  extraction, and maximum line length reflowing in ``po2mdx``.

* Does not translate embedded HTML.

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
