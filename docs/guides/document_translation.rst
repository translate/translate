
.. _document_translation:

Document translation
********************
Translating documents can be quite different from translating software
interfaces. Many issues specific to software localisation might not be relevant
in documents, such as accelerators, translation length, constructed phrases,
etc.  However, document translation has several other issues that are good to be
aware of.

.. _document_translation#preparing_for_translation:

Preparing for translation
=========================
Ideally a document should be prepared for translation. A good source document
will make translation easier. Possibilities:

* Proofread the document (spelling, grammar, clarity)
* Use consistent terminology
* Read `"writing for translation"
  <https://www.multilingualwebmaster.com/library/writing-TR.html>`_
* For structured documents, use proper structure like headings and subheadings
  instead of using style only.

.. _document_translation#translation:

Translation
===========
A lot can be said about translation in general, but this is only meant to give
you some tips.

Be aware of potential complications arising from translation memory. For example, you can have
exact matches (in which the source string is identical to one translated before),
or In Context Exact (ICE) matches, in which some translation tools specifically indicate
that surrounding text in the paragraph is identical as well. Matches could also indicate agreement
with regards to domain, file, date, etc.

.. _document_translation#post-processing:

Post-processing
===============
After generating the translated document, you will very likely need to do some post
processing. Things to consider:

* Ensuring correct translation in cases where context might not have been
  obvious during translation
* Document layout, page layout
* Fonts or other styling changes
* Style of generated content, such as numbers
* Generated sections, such as Table of contents, list of figures, index,
  variables
