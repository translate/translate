.. _flatxml:

Flat XML
********

The Translate Toolkit is able to process flat XML files using the
:doc:`flatxml2po </commands/flatxml2po>` converter.

Flat XML (:wp:`eXtensible Markup Language <XML>`) is a simple monolingual
file format similar to a very basic form of the :doc:`android` format.
Flat in this context means a single level of elements wrapped in the
root-element with no other structuring.

.. _flatxml#conformance:

Conformance
===========

* Single-level XML with attributes identifying a resource:

  .. code-block:: xml

    <root>
      <str key="hello_world">Hello World!</str>
      <str key="resource_key">Translated value.</str>
    </root>

* Customizable element- and attribute-names (including namespaces):

  .. code-block:: xml

    <dictionary xmlns="urn:translate-toolkit:flat-xml-dictionary">
      <entry name="hello_world">Hello World!</entry>
      <entry name="resource_key">Translated value.</entry>
    </dictionary>

* Value whitespace is assumed to be significant
  (equivalent to setting ``xml:space="preserve"``):

  .. code-block:: xml

    <root>
      <str key="multiline">The format assumes xml:space="preserve".
    There is no need to specify it explicitly.

    This assumption only applies to the value element; not the root element.</str>
    </root>

* Non-resource elements and attributes are preserved (assuming the same file
  is also used when converting back to XML):

  .. code-block:: xml

    <root>
      <str key="translate_me">This needs to be translated</str>
      <const name="the_answer" hint="this isn't translated">42</const>
      <str key="important" priority="100">Some important string</str>
    </root>

* Indentation can be customized to match an existing and consistent style:

  .. code-block:: xml

    <root>
            <str key="indent">This file uses 8 spaces for indent</str>
            <str key="tab_works">Tabs can also be used; but this is limited to the Python API at this point</str>
            <str key="linerized">No indent (all in one line) is also supported</str>
            <str key="note_on_eof">End-of-file *always* has a LF to satisfy VCS</str>
    </root>

  .. note:: To avoid potential issues and extraneous changes in diffs,
     this format always forces an ending linefeed by default for
     compatibility with various
     :wp:`Version control systems <Version_control_system>`
     (such as :wp:`Git`).

.. _flatxml#non-conformance:

Non-Conformance
===============

While the format is flexible, not all features are supported:

* Mixed element/attribute names (as well as different namespaces for
  root- and value-element) and nested structures additional child elements.
  This format intentionally focuses on a simple structure that can be
  used by other languages (such as :wp:`XSLT`).
* Comments are preserved on roundtrips, but are not carried over into
  the resulting :doc:`po`.
* XML Fragments and non-wellformed XML.

.. _flatxml#references:

References
==========

* `XML specification <http://www.w3.org/TR/REC-xml/>`_
