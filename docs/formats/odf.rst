
.. _odf:
.. _opendocument_format:

OpenDocument Format
*******************
This page summarises the support for the :wp:`OpenDocument` format (ODF) in the
Translate Toolkit. This includes the :doc:`odf2xliff </commands/odf2xliff>` and
xliff2odf converters, and the :doc:`odf2po </commands/odf2po>` and po2odf
converters.

The converters read the standard ODF package XML members and embedded ODF
subdocuments declared in ``META-INF/manifest.xml``. Missing optional metadata
or styles members are accepted. Package output preserves member metadata and
writes the uncompressed ``mimetype`` member first as required by ODF.

Our support is implemented to classify tags as not containing translatable
text, or as being inline tags inside translatable tags. This approach means
that new fields added in future versions will automatically be seen as
translatable and should still be extracted successfully, even if the currently
released versions of the Translate Toolkit are not aware of their existence.

* `Currently used and classified tags
  <https://github.com/translate/translate/blob/master/translate/storage/odf_shared.py#L23>`_

More complex tag uses are still needed to extract 100% correctly in some
complex cases. Following issues are known:

* in spreadsheets you need to put the translation in both the value attribute and the ``p`` tag
* in spreadsheets only extract strings from cells with ``type="string"``
* we don't seem to be extracting user defined metadata
* ``<g>`` isn't cloneable (see https://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html#clone)
