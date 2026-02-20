.. _wxl:

WiX Localization files (.wxl)
*****************************

The Translate Toolkit is able to process WiX Localization files using the
:doc:`wxl2po </commands/wxl2po>` converter.

WiX Localization (:wp:`WiX <WiX>`) is the XML-based localization format used
by the `WiX Toolset <https://wixtoolset.org/>`_ for building Windows Installer
packages.  Files use the ``.wxl`` extension.

.. _wxl#format:

Format
======

A WXL file contains a ``WixLocalization`` root element that carries two
important attributes:

* ``Culture`` – the locale code for the target language, in lowercase, e.g.
  ``de-de``, ``pt-br`` or ``cs-cz``.  This **must** be set for new files.
* ``Codepage`` – the Windows code page or encoding identifier for the file
  (e.g. ``1252`` for Western European, ``65001`` for UTF-8).  This is used
  both as a hint for determining the file encoding and as metadata for the MSI
  installer.

Translatable strings live in child elements of the root:

* ``<String Id="key">text</String>`` – text as element content (WiX v3 style)
* ``<String Id="key" Value="text" />`` – text as ``Value`` attribute (WiX v4
  style); other attributes on the element (e.g. ``Overridable``) are preserved.
* ``<UI Id="key" Text="text" … />`` – translatable text in the ``Text``
  attribute of a ``UI`` element.

``UI`` elements *without* a ``Text`` attribute are non-translatable layout
overrides that are preserved verbatim on round-trips.

Example (WiX v4):

.. code-block:: xml

   <?xml version="1.0" encoding="windows-1252"?>
   <WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl"
                    Culture="de-de" Codepage="1252">
     <String Id="WixUIBack" Overridable="yes" Value="&amp;Zurück" />
     <String Id="WixUICancel" Overridable="yes" Value="Abbrechen" />
     <UI Dialog="FilesInUse" Control="Retry" X="280" Width="80" />
   </WixLocalization>

Example (WiX v3):

.. code-block:: xml

   <?xml version="1.0" encoding="windows-1252"?>
   <WixLocalization xmlns="http://schemas.microsoft.com/wix/2006/localization"
                    Culture="pt-br" Codepage="1252">
     <String Id="WixUIBack" Overridable="yes">&amp;Voltar</String>
     <String Id="WixUICancel">Cancelar</String>
   </WixLocalization>

.. _wxl#encoding:

Encoding
========

WXL files often lack an explicit XML encoding declaration.  When no declaration
is present the toolkit defaults to ``windows-1252`` for parsing (the most
common Codepage in WXL files) and verifies against the ``Codepage`` attribute
after the root element has been read, re-parsing with the correct encoding if
necessary.

Files that carry a ``<?xml … encoding="…"?>`` declaration are parsed using the
declared encoding directly.

.. _wxl#references:

References
==========

* `WixLocalization schema reference <https://docs.firegiant.com/wix/schema/wxl/wixlocalization/>`_
* `WiX v4 WXL XML schema <https://wixtoolset.org/schemas/v4/wxl/>`_
* `WiX Toolset <https://wixtoolset.org/>`_
