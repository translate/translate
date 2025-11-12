
.. _md:

Markdown
********

The Translate Toolkit is able to process Markdown files using the :doc:`md2po
</commands/md2po>` converter.


.. _md#conformance:

Conformance
===========

* Uses the CommonMark-compliant mistletoe parser.

* Capable of handling nested containers, such as lists in lists, and other
  esoteric Markdown features.

* Aims to extract all content relevant for translation, at the cost of also
  including some formatting. For example, \*phrase emphasis\* and \`inline code\`
  is included in the text to be translated. More bulky inline content, such
  as inline HTML and autolinks, are replaced with placeholders {1}, {2}, etc.

* Aims to preserve formatting as far as possible. But since the formatting is
  lost with the PO format, it is likely that you will want to reflow (word wrap)
  the translated Markdown. The po2md converter has an option to do that.

* Hard line breaks in the Markdown appear as hard line breaks in the translation
  units (PO files), and vice versa.

* Does not translate embedded HTML.

* Does not perform any checks that the translated text has the same formatting
  as the source.


.. _md#excluding_content:

Excluding Content from Translation
===================================

You can exclude sections of Markdown content from translation by using HTML
comment markers. Content between ``<!-- translate:off -->`` and
``<!-- translate:on -->`` will be preserved in the output but will not be
extracted for translation.

Example::

   # Welcome

   This text will be translated.

   <!-- translate:off -->

   ```python
   def example():
       return "This code won't be extracted"
   ```

   [link-ref]: https://example.com

   <!-- translate:on -->

   This text will also be translated.

In this example, only "Welcome", "This text will be translated.", and "This
text will also be translated." will be extracted as translation units. The
code block and link reference definition will remain unchanged.

This feature is useful for:

* Code examples and syntax highlighting blocks
* Link reference definitions
* Static content like images and media references
* Configuration examples
* API endpoints and technical identifiers


.. _md#references:

References
==========

* `The CommonMark specification
  <https://spec.commonmark.org/>`__
* `The mistletoe parser
  <https://github.com/miyuchina/mistletoe>`__
