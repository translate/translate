.. _resx:

.NET Resource files (.resx)
***************************

.Net Resource (.resx) files are a monolingual file format used in Microsoft .Net Applications. The .resx resource
file format consists of XML entries, which specify objects and strings inside XML tags. It contains a
standard set of header information, which describes the format of the resource entries and specifies the
versioning information for the XML used to parse the data. Following the header information, each entry is
described as a name/value pair.

Comments can be added per string using the optional ``<comment>`` field. As only one comment field is available,
both translator and developer comments are stored in the same place. Translator comments are
automatically wrapped with brackets and pre-fixed with 'Translator Comment:' during the po2resx process to
make it easy to distinguish comment origin inside the .resx files.

Example:

::

    <data name="key">
        <value>hello world</value>
        <comment>Optional developer comment about the string [Translator Comment: Optional translator comment]</comment>
    </data>

resx2po and  po2resx are used for conversion.

.. _resx#references:

References
==========

* `Resources in .Resx File Format
  <http://msdn.microsoft.com/en-us/library/ekyft91f%28v=VS.90%29.aspx>`_
* `ASP.NET Web Page Resources Overview
  <http://msdn.microsoft.com/en-us/library/ms227427.aspx>`_
