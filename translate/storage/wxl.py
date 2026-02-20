#
# Copyright 2025 Translate Authors
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Module for handling WiX Localization (.wxl) files.

Specification: https://docs.firegiant.com/wix/schema/wxl/wixlocalization/
XML schema: https://wixtoolset.org/schemas/v4/wxl/
"""

from __future__ import annotations

import re

from lxml import etree

from translate.misc.xml_helpers import reindent
from translate.storage import base

# WiX XML namespace identifiers
WXL_NAMESPACE_V4 = "http://wixtoolset.org/schemas/v4/wxl"
WXL_NAMESPACE_V3 = "http://schemas.microsoft.com/wix/2006/localization"

# Mapping from WiX Codepage values to Python codec names
_CODEPAGE_MAP: dict[str, str] = {
    "037": "cp037",
    "437": "cp437",
    "500": "cp500",
    "720": "cp720",
    "737": "cp737",
    "775": "cp775",
    "850": "cp850",
    "852": "cp852",
    "855": "cp855",
    "857": "cp857",
    "858": "cp858",
    "860": "cp860",
    "861": "cp861",
    "862": "cp862",
    "863": "cp863",
    "864": "cp864",
    "865": "cp865",
    "866": "cp866",
    "869": "cp869",
    "874": "cp874",
    "875": "cp875",
    "932": "cp932",
    "936": "cp936",
    "949": "cp949",
    "950": "cp950",
    "1026": "cp1026",
    "1250": "windows-1250",
    "1251": "windows-1251",
    "1252": "windows-1252",
    "1253": "windows-1253",
    "1254": "windows-1254",
    "1255": "windows-1255",
    "1256": "windows-1256",
    "1257": "windows-1257",
    "1258": "windows-1258",
    "65001": "utf-8",
    "utf-8": "utf-8",
    "utf8": "utf-8",
}

_DEFAULT_ENCODING = "windows-1252"


def _codepage_to_encoding(codepage: str | None) -> str:
    """Convert a WiX Codepage value to a Python encoding name."""
    if not codepage:
        return _DEFAULT_ENCODING
    key = str(codepage).lower().strip()
    if key in _CODEPAGE_MAP:
        return _CODEPAGE_MAP[key]
    if key.isdigit():
        return f"cp{key}"
    return _DEFAULT_ENCODING


def _detect_encoding(content: bytes) -> str:
    """
    Detect the encoding of a WXL file from its bytes.

    Checks for a BOM first; then the XML encoding declaration; if absent,
    looks for the Codepage attribute on the root element and maps it to a
    codec.  Falls back to windows-1252 (most common in WXL files).
    """
    # Byte-Order Marks take highest precedence.
    if content.startswith(b"\xef\xbb\xbf"):
        return "utf-8"
    if content.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"

    if content.startswith(b"<?xml"):
        m = re.search(rb'encoding=["\']([\w-]+)["\']', content[:200])
        if m:
            return m.group(1).decode("ascii").lower()

    # No XML declaration – look for Codepage in the first part of the file
    m = re.search(rb'Codepage=["\']([\w-]+)["\']', content[:1000])
    if m:
        return _codepage_to_encoding(m.group(1).decode("ascii"))

    return _DEFAULT_ENCODING


class WxlUnit(base.TranslationUnit):
    """
    A single localizable entry in a WXL file.

    Handles both ``<String Id="…">value</String>`` (text content),
    ``<String Id="…" Value="…" />`` (Value attribute, WiX v4), and
    ``<UI Id="…" Text="…" />`` (UI element with Text attribute).
    All other attributes are preserved on round-trip.
    """

    def __init__(self, source: str = "", **kwargs) -> None:
        self.xmlelement = etree.Element("String")
        super().__init__(source, **kwargs)

    # ------------------------------------------------------------------
    # TranslationUnit interface

    @property
    def source(self) -> str:
        return self.getid() or ""

    @source.setter
    def source(self, value: str) -> None:
        self.setid(value)

    @property
    def target(self) -> str:
        """Return the translatable text for this entry."""
        tag = etree.QName(str(self.xmlelement.tag)).localname
        if tag == "UI":
            return self.xmlelement.get("Text", "")
        # String element: prefer Value attribute (WiX v4), fall back to text
        value_attr = self.xmlelement.get("Value")
        if value_attr is not None:
            return value_attr
        return self.xmlelement.text or ""

    @target.setter
    def target(self, value: str) -> None:
        if self.target == value:
            return
        tag = etree.QName(str(self.xmlelement.tag)).localname
        if tag == "UI":
            self.xmlelement.set("Text", value or "")
        elif self.xmlelement.get("Value") is not None:
            # Preserve Value-attribute style
            self.xmlelement.set("Value", value or "")
        else:
            self.xmlelement.text = value or ""

    def setid(self, value: str) -> None:
        if value:
            self.xmlelement.set("Id", value)

    def getid(self) -> str:
        return self.xmlelement.get("Id") or ""

    def getlocations(self) -> list[str]:
        id_ = self.getid()
        return [id_] if id_ else []

    def __str__(self) -> str:
        return etree.tostring(self.xmlelement, encoding="unicode")

    @classmethod
    def createfromxmlElement(cls, element: etree._Element) -> WxlUnit:
        unit = cls.__new__(cls)
        super(WxlUnit, unit).__init__()
        unit.xmlelement = element
        return unit


class WxlFile(base.TranslationStore):
    """
    Class representing a WiX Localization (.wxl) file store.

    Supports reading and writing both WiX v3
    (``http://schemas.microsoft.com/wix/2006/localization``) and WiX v4
    (``http://wixtoolset.org/schemas/v4/wxl``) format files.

    Translatable entries are:

    * ``<String Id="key">text</String>`` – text as element content
    * ``<String Id="key" Value="text" />`` – text as Value attribute (WiX v4)
    * ``<UI Id="key" Text="text" … />`` – text as Text attribute

    All other XML content (comments, ``<UI>`` elements without ``Text``,
    extra attributes on ``<String>`` elements, etc.) is preserved on
    round-trip.
    """

    UnitClass = WxlUnit
    Name = "WiX Localization File"
    Mimetypes = ["text/xml"]
    Extensions = ["wxl"]

    def __init__(self, inputfile=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._codepage: str = "1252"

        if inputfile is not None:
            self.parse(inputfile)
        else:
            self._make_empty()

    # ------------------------------------------------------------------
    # Language / Codepage

    def gettargetlanguage(self) -> str:
        """Return the target language (WXL ``Culture`` attribute)."""
        return self.targetlanguage or ""

    def settargetlanguage(self, targetlanguage: str) -> None:
        """Set the target language and update the ``Culture`` attribute."""
        self.targetlanguage = targetlanguage
        if hasattr(self, "root") and self.root is not None:
            if targetlanguage:
                self.root.set("Culture", targetlanguage)
            elif "Culture" in self.root.attrib:
                del self.root.attrib["Culture"]

    @property
    def codepage(self) -> str:
        """The WiX Codepage value (e.g. ``1252``, ``utf-8``)."""
        return self._codepage

    @codepage.setter
    def codepage(self, value: str) -> None:
        self._codepage = value
        if hasattr(self, "root") and self.root is not None:
            self.root.set("Codepage", value)

    # ------------------------------------------------------------------
    # Internal helpers

    def _make_empty(self) -> None:
        """Create an empty WXL document backed by an lxml element tree."""
        self.root = etree.Element(
            f"{{{WXL_NAMESPACE_V4}}}WixLocalization",
            nsmap={None: WXL_NAMESPACE_V4},
        )
        self.document = self.root.getroottree()

    def _parse_units(self) -> None:
        """
        Walk root children and register translatable units.

        * ``<String>`` elements are always translatable.
        * ``<UI>`` elements are only translatable when they carry a
          ``Text`` attribute.  Other ``<UI>`` elements are kept in the XML
          tree for round-trip fidelity but are not exposed as units.
        """
        for element in self.root:
            if not isinstance(element.tag, str):
                # Skip comments, processing instructions, etc.
                continue
            localname = etree.QName(element.tag).localname
            if localname == "String" or (
                localname == "UI" and element.get("Text") is not None
            ):
                unit = self.UnitClass.createfromxmlElement(element)
                self.addunit(unit, new=False)

    # ------------------------------------------------------------------
    # TranslationStore interface

    def addunit(self, unit: WxlUnit, new: bool = True) -> None:
        super().addunit(unit)
        if new:
            self.root.append(unit.xmlelement)

    def removeunit(self, unit: WxlUnit) -> None:
        super().removeunit(unit)
        self.root.remove(unit.xmlelement)

    def parse(self, input) -> None:  # ty:ignore[invalid-method-override]
        """Parse a WXL file from a file object or bytes."""
        if not hasattr(self, "filename"):
            self.filename = getattr(input, "name", "")

        if hasattr(input, "read"):
            input.seek(0)
            content = input.read()
        else:
            content = input

        if isinstance(content, str):
            content = content.encode("utf-8")

        # Detect the file encoding, defaulting to windows-1252 per WXL convention.
        encoding = _detect_encoding(content)

        parser = etree.XMLParser(encoding=encoding, resolve_entities=False)
        self.root = etree.fromstring(content, parser)
        self.document = self.root.getroottree()

        # Read Codepage and verify the encoding we used was correct.
        codepage = self.root.get("Codepage", "1252")
        self._codepage = codepage
        self.settargetlanguage(self.root.get("Culture", ""))

        # Only re-parse based on Codepage when the encoding wasn't already
        # declared authoritatively via a BOM or an XML encoding declaration;
        # those always take precedence over the WiX Codepage attribute.
        bom_prefixes = (b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")
        encoding_is_authoritative = content.startswith(
            bom_prefixes
        ) or content.startswith(b"<?xml")
        correct_encoding = _codepage_to_encoding(codepage)
        if not encoding_is_authoritative and correct_encoding.lower().replace(
            "-", ""
        ) != encoding.lower().replace("-", ""):
            # Re-parse with the correct encoding indicated by Codepage.
            parser = etree.XMLParser(encoding=correct_encoding, resolve_entities=False)
            self.root = etree.fromstring(content, parser)
            self.document = self.root.getroottree()

        self._parse_units()

    def serialize(self, out) -> None:
        """Serialize the store back to a WXL file."""
        # Ensure Culture is written to the root element.
        culture = self.gettargetlanguage()
        if culture:
            self.root.set("Culture", culture)

        # Determine output encoding from Codepage.
        encoding = _codepage_to_encoding(self._codepage)
        # Normalise to the form lxml understands for XML declarations.
        xml_encoding = "utf-8" if encoding.lower() in {"utf-8", "utf8"} else encoding

        reindent(self.root, indent="  ")
        self.root.tail = "\n"

        out.write(
            etree.tostring(
                self.document,
                xml_declaration=True,
                encoding=xml_encoding,
                pretty_print=False,
            )
        )
