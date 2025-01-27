#
# Copyright 2012 Michal Čihař
# Copyright 2014 Luca De Petrillo
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Module for handling Android String and Plurals resource files."""

from __future__ import annotations

import copy
import os
import re
from xml.parsers.expat import XML_PARAM_ENTITY_PARSING_NEVER, ParserCreate

from lxml import etree

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base, lisa

WHITESPACE = {" ", "\n", "\t"}  # Whitespace that we collapse.
ESCAPE_NEWLINE = {"n", "N"}
ESCAPE_TAB = {"t", "T"}
ESCAPE_PLAIN = {" ", '"', "'", "@", "?", "\\"}
MULTIWHITESPACE = re.compile(r"[ \n\t]{2}(?!\\n)")
QUOTED_STRING = re.compile(r'((?<!\\)"(?:\\"|[^"])*(?<!\\)")')
UNICODE_ESCAPE = re.compile(r"\\u([a-fA-F0-9]{4})")
CHAR_ESCAPE = re.compile(r"\\(.)")
WHITESPACE_RE = re.compile(r"\s+")

ESCAPE_TRANSLATE = str.maketrans(
    {
        "\\": "\\\\",
        "\n": "\\n",
        "\t": "\\t",
        "'": "\\'",
        '"': '\\"',
    }
)


class DecodingXMLParser:
    """
    XML parser that processes non CDATA strings.

    - all XML markup from given depth is output as is
    - CDATA elements are output as is
    - process_string() is called on all other textual content
    """

    EMIT_DEPTH = 1
    FOREGIN_DTD = True

    def __init__(self, text: str):
        self.text = text.encode("utf-8")
        self.output = []
        self.emit_start = None
        self.decoded_emit = None
        self.character_data = False
        self.raw_string = True
        self.in_string = False
        self.do_cleanup = False
        self.depth = 0
        self.parser = parser = ParserCreate()
        if self.FOREGIN_DTD:
            parser.UseForeignDTD(self.FOREGIN_DTD)
        parser.SetParamEntityParsing(XML_PARAM_ENTITY_PARSING_NEVER)
        parser.StartElementHandler = self.StartElementHandler
        parser.EndElementHandler = self.EndElementHandler
        parser.CharacterDataHandler = self.CharacterDataHandler
        parser.StartCdataSectionHandler = self.StartCdataSectionHandler
        parser.EndCdataSectionHandler = self.EndCdataSectionHandler
        parser.DefaultHandler = self.DefaultHandler

    @staticmethod
    def decode_unicode_escapes(match: re.Match) -> str:
        escaped = match.group(1)
        # Convert from hex to character
        return chr(int(escaped, 16))

    @staticmethod
    def decode_escapes(match: re.Match) -> str:
        escaped = match.group(1)
        if escaped in ESCAPE_NEWLINE:
            return "\n"  # an actual newline
        if escaped in ESCAPE_TAB:
            return "\t"  # an actual tab
        if escaped in ESCAPE_PLAIN:
            # Plain string to escape
            return escaped
        # All others, remove, like Android does as well.
        return ""

    @staticmethod
    def strip_part(text: str) -> str:
        if text.startswith('"'):
            # Missing closing quote is gracefully ignored
            return text.removeprefix('"').removesuffix('"')
        # Consolidate whitespace
        return WHITESPACE_RE.sub(" ", text)

    @classmethod
    def process_string(cls, content: str) -> tuple[str, bool, bool]:
        # Skip processing for a blank string
        if not content:
            return "", False, False

        # Extract quoted parts, remove blank ones
        parts = [part for part in QUOTED_STRING.split(content) if part]

        # Detect possible cleanups
        cleanup_start = not parts[0].startswith('"')
        cleanup_end = not parts[-1].startswith('"')

        # Collapse whitespace
        stripped_parts = [cls.strip_part(part) for part in parts]
        # Merge this back to a single string
        text = "".join(stripped_parts)

        # Handle unicode escapes
        unescaped_text = UNICODE_ESCAPE.sub(cls.decode_unicode_escapes, text)
        # Handle other escapes
        unescaped_text = CHAR_ESCAPE.sub(cls.decode_escapes, unescaped_text)

        # Detect escaping at the start and end of a string (we actually care only for
        # whitespace escapes, but detecting more does not matter)
        if text and unescaped_text and text[0] != unescaped_text[0]:
            cleanup_start = False
        if text and unescaped_text and text[-1] != unescaped_text[-1]:
            cleanup_end = False

        return unescaped_text, cleanup_start, cleanup_end

    def cleanup_text(self, text: str) -> str:
        """Remove leading whitespace from text."""
        if not self.output:
            return text.lstrip()
        return text

    def emit(self):
        if self.emit_start is not None:
            text = self.text[self.emit_start : self.parser.CurrentByteIndex].decode(
                "utf-8"
            )
            self.do_cleanup = not self.raw_string
            if not self.raw_string:
                text, cleanup_start, self.do_cleanup = self.process_string(text)
                if cleanup_start:
                    text = self.cleanup_text(text)
            self.output.append(text)
            self.emit_start = None
        self.character_data = False
        self.raw_string = True
        self.in_string = False

    def StartElementHandler(self, _name, _attributes):
        self.emit()
        if self.depth >= self.EMIT_DEPTH:
            self.emit_start = self.parser.CurrentByteIndex
        self.depth += 1

    def EndElementHandler(self, _name):
        self.emit()
        if self.depth >= self.EMIT_DEPTH:
            self.emit_start = self.parser.CurrentByteIndex
        self.depth -= 1

    def CharacterDataHandler(self, _data):
        if not self.character_data and not self.in_string:
            self.emit()
            self.emit_start = self.parser.CurrentByteIndex
            self.raw_string = False
            self.in_string = True

    def StartCdataSectionHandler(self):
        self.emit()
        self.character_data = True
        self.emit_start = self.parser.CurrentByteIndex

    def EndCdataSectionHandler(self):
        self.character_data = False

    def DefaultHandler(self, _data):
        if self.depth >= self.EMIT_DEPTH:
            self.emit()
            self.emit_start = self.parser.CurrentByteIndex

    def parse(self) -> str:
        self.parser.Parse(self.text, True)
        if self.depth >= self.EMIT_DEPTH:
            self.emit()
        # Remove trailing whitespace from text
        if self.do_cleanup and self.output:
            self.output[-1] = self.output[-1].rstrip()
        return "".join(self.output)


class EncodingXMLParser(DecodingXMLParser):
    EMIT_DEPTH = 0
    FOREGIN_DTD = False

    @staticmethod
    def process_string(text: str) -> tuple[str, bool, bool]:
        return (
            AndroidResourceUnit.escape(text, quote_wrapping_whitespaces=False),
            False,
            False,
        )

    def parse(self) -> str:
        self.emit_start = 0
        return super().parse()


class AndroidResourceUnit(base.TranslationUnit):
    """A single entry in the Android String resource file."""

    SINGULAR_TAG = "string"
    PLURAL_TAG = "plurals"

    @classmethod
    def createfromxmlElement(cls, element):
        term = None
        # Actually this class supports only plurals and string tags
        if element.tag in {cls.PLURAL_TAG, cls.SINGULAR_TAG}:
            term = cls(None, xmlelement=element)
        return term

    def __init__(self, source, empty=False, xmlelement=None, **kwargs):
        if xmlelement is not None:
            self.xmlelement = xmlelement
        elif self.hasplurals(source):
            self.xmlelement = etree.Element(self.PLURAL_TAG)
        else:
            self.xmlelement = etree.Element(self.SINGULAR_TAG)
        if source is not None:
            self.setid(source)
        super().__init__(source)

    def istranslatable(self):
        return bool(self.getid()) and self.xmlelement.get("translatable") != "false"

    def marktranslatable(self, value: bool) -> None:
        return self.xmlelement.set("translatable", "true" if value else "false")

    def isblank(self):
        return not bool(self.getid())

    def getid(self):
        return self.xmlelement.get("name")

    def setid(self, newid):
        return self.xmlelement.set("name", newid)

    def getcontext(self):
        return self.xmlelement.get("name")

    @staticmethod
    def xml_escape_space(matchobj):
        return matchobj.group(0).replace("  ", r" \u0020")

    @classmethod
    def escape(
        cls, text: str | None, quote_wrapping_whitespaces: bool = True
    ) -> str | None:
        """
        Escape all the characters which need to be escaped in an Android XML
        file.

        :param text: Text to escape
        :param quote_wrapping_whitespaces: If True, heading and trailing
               whitespaces will be quoted placing the entire resulting text in
               double quotes.
        """
        if text is None:
            return None
        if len(text) == 0:
            return ""

        # Escape XML chars and whitespace
        text = text.translate(ESCAPE_TRANSLATE)

        # @ and ? needs to be escaped at start as this would be interpreted
        # as string/style references
        if text.startswith(("@", "?")):
            text = f"\\{text}"

        # Quote strings with more whitespace
        multispace = MULTIWHITESPACE.search(text)
        if quote_wrapping_whitespaces and (
            text[0] in WHITESPACE or text[-1] in WHITESPACE or multispace
        ):
            return f'"{text}"'
        # In xml multispace
        if not quote_wrapping_whitespaces and multispace:
            return MULTIWHITESPACE.sub(cls.xml_escape_space, text)

        return text

    @base.TranslationUnit.source.getter
    def source(self):
        if super().source is None:
            return self.target
        return super().source

    def get_xml_text_value(self, xmltarget):
        raw_xml = etree.tostring(xmltarget, encoding="unicode", with_tail=False)
        # Unescape as plain text in case there is no XML markup. Ufortunately
        # CDATA elements are not listed as childs in lxml, so test for it in raw XML.
        if len(xmltarget) == 0 and "<![CDATA[" not in raw_xml:
            if xmltarget.text is None:
                return ""
            text, cleanup_start, cleanup_end = DecodingXMLParser.process_string(
                xmltarget.text
            )
            if cleanup_start:
                text = text.lstrip()
            if cleanup_end:
                text = text.rstrip()
            return text

        # Use decoding parser to keep XML entitities, CDATA while processing Android escaping
        parser = DecodingXMLParser(raw_xml)
        return parser.parse()

    def set_xml_text_plain(self, target, xmltarget):
        # Remove possible old elements
        for x in xmltarget.iterchildren():
            xmltarget.remove(x)
        # Handle text only
        xmltarget.text = self.escape(target)

    def set_xml_text_value(self, target, xmltarget):
        if "<" in target or "&" in target:
            # Try to handle it as legacy XML
            parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
            if self._store is not None:
                cloned_doc = copy.deepcopy(self._store.document)
                cloned_root = cloned_doc.getroot()
                cloned_root.clear()
                # Add content to the element so that we get a real closing tag
                cloned_root.text = " "
                template = etree.tostring(
                    cloned_doc,
                    encoding="unicode",
                    doctype=copy.copy(self._store.XMLdoctype),
                )
            else:
                template = "<resources></resources>"
            newstring = template.replace(
                "</resources>",
                f"<{xmltarget.tag}>{target}</{xmltarget.tag}></resources>",
            )
            try:
                etree.fromstring(newstring, parser)
            except Exception:
                self.set_xml_text_plain(target, xmltarget)
            else:
                # Escape text parts
                encoding_parser = EncodingXMLParser(newstring)
                newstring = encoding_parser.parse()
                newtree = etree.fromstring(newstring, parser)[0]
                # Copy existing attributes
                for attribute, value in xmltarget.items():
                    newtree.attrib[attribute] = value
                # Update text
                parent = xmltarget.getparent()
                # Parent can be none when operating on Unit only without a storage
                if parent is not None:
                    parent.replace(xmltarget, newtree)
                # Update unit xmlelement if needed (plurals are inner elements here)
                if xmltarget == self.xmlelement:
                    self.xmlelement = newtree
        else:
            self.set_xml_text_plain(target, xmltarget)

    def gettargetlanguage(self):
        if self._store is None:
            return "en"
        return super().gettargetlanguage()

    def get_plural_tags(self):
        locale = self.gettargetlanguage()
        if not locale:
            return data.plural_tags["en"]
        # Handle b+ style language codes
        locale = locale.removeprefix("b+")
        locale = locale.replace("_", "-").replace("+", "-").split("-")[0]
        return data.plural_tags.get(locale, data.plural_tags["en"])

    @property
    def target(self):
        if self.xmlelement.tag != self.PLURAL_TAG:
            return self.get_xml_text_value(self.xmlelement)
        plurals = {
            entry.get("quantity"): self.get_xml_text_value(entry)
            for entry in self.xmlelement.iterchildren("item")
        }
        plural_tags = self.get_plural_tags()
        return multistring([plurals.get(tag, "") for tag in plural_tags])

    @target.setter
    def target(self, target):
        if self.hasplurals(self.source) or self.hasplurals(target):
            # Fix the root tag if mismatching
            if self.xmlelement.tag != self.PLURAL_TAG:
                old_id = self.getid()
                self.xmlelement = etree.Element(self.PLURAL_TAG)
                self.setid(old_id)

            plural_tags = self.get_plural_tags()

            # Sync plural_strings elements to plural_tags count.
            plural_strings = self.sync_plural_count(target, plural_tags)

            # Rebuild plurals.
            for entry in self.xmlelement.iterchildren():
                self.xmlelement.remove(entry)

            self.xmlelement.text = "\n    "

            # Include "other" as copy of "many" if "other" is not present. This avoids crashes
            # of Android builts with broken plurals handling.
            if "other" not in plural_tags and "many" in plural_tags:
                # Create copy here to avoid modifications to laguage.data
                plural_tags = [*plural_tags, "other"]
                plural_strings.append(plural_strings[-1])

            for plural_tag, plural_string in zip(plural_tags, plural_strings):
                item = etree.Element("item")
                item.set("quantity", plural_tag)
                self.xmlelement.append(item)
                self.set_xml_text_value(plural_string, item)
        else:
            # Fix the root tag if mismatching
            if self.xmlelement.tag != self.SINGULAR_TAG:
                old_id = self.getid()
                self.xmlelement = etree.Element(self.SINGULAR_TAG)
                self.setid(old_id)

            self.set_xml_text_value(target, self.xmlelement)

        self._rich_target = None
        self._target = target

    def getlanguageNode(self, lang=None, index=None):
        return self.xmlelement

    # Notes are handled as previous sibling comments.
    def addnote(self, text, origin=None, position="append"):
        if origin in {"programmer", "developer", "source code", None}:
            self.xmlelement.addprevious(etree.Comment(text))
        else:
            super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in {"programmer", "developer", "source code", None}:
            comments = []
            if self.xmlelement is not None:
                prevSibling = self.xmlelement.getprevious()
                while (prevSibling is not None) and (prevSibling.tag is etree.Comment):
                    comments.insert(0, prevSibling.text)
                    prevSibling = prevSibling.getprevious()

            return "\n".join(comments)
        return super().getnotes(origin)

    def removenotes(self, origin=None):
        if (self.xmlelement is not None) and (self.xmlelement.getparent is not None):
            prevSibling = self.xmlelement.getprevious()
            while (prevSibling is not None) and (prevSibling.tag is etree.Comment):
                prevSibling.getparent().remove(prevSibling)
                prevSibling = self.xmlelement.getprevious()

        super().removenotes()

    def __str__(self):
        return etree.tostring(self.xmlelement, pretty_print=True, encoding="unicode")

    def __eq__(self, other):
        return str(self) == str(other)

    @staticmethod
    def hasplurals(thing):
        return isinstance(thing, (multistring, list))


class AndroidResourceFile(lisa.LISAfile):
    """Class representing an Android String resource file store."""

    UnitClass = AndroidResourceUnit
    Name = "Android String Resource"
    Mimetypes = ["application/xml"]
    Extensions = ["xml"]
    rootNode = "resources"
    bodyNode = "resources"
    XMLskeleton = """<?xml version="1.0" encoding="utf-8"?>
<resources></resources>"""
    XMLindent = {"indent": "    ", "leaves": {"string", "item"}, "trailing_eol": True}
    XMLuppercaseEncoding = False

    def initbody(self):
        """
        Initialises self.body so it never needs to be retrieved from the XML
        again.
        """
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.getroot()

    def parse(self, xml):
        """Populates this object from the given xml string."""
        if not hasattr(self, "filename"):
            self.filename = getattr(xml, "name", "")
        if hasattr(xml, "read"):
            xml.seek(0)
            posrc = xml.read()
            xml = posrc
        parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
        self.document = etree.fromstring(xml, parser).getroottree()
        self._encoding = self.document.docinfo.encoding
        self.initbody()
        assert self.document.getroot().tag == self.namespaced(self.rootNode)

        for entry in self.document.getroot().iterchildren():
            term = self.UnitClass.createfromxmlElement(entry)
            if term is not None:
                self.addunit(term, new=False)

    def gettargetlanguage(self):
        target_lang = super().gettargetlanguage()

        # If targetlanguage isn't set, we try to extract it from the filename path (if any).
        if target_lang is None and hasattr(self, "filename") and self.filename:
            # Android standards expect resource files to be in a directory named "values[-<lang>[-r<region>]]".
            parent_dir = os.path.split(os.path.dirname(self.filename))[1]
            match = re.search(r"^values-(\w*)", parent_dir)
            if match is not None:
                target_lang = match.group(1)
            elif parent_dir == "values":
                # If the resource file is inside the "values" directory, then it is the default/source language.
                target_lang = self.sourcelanguage

            # Cache it
            self.settargetlanguage(target_lang)

        return target_lang

    def addunit(self, unit, new=True):
        """
        Adds unit to the document.

        In addition to the standard addunit, it also tries to move
        namespace definitions to the top <resources> element.
        """
        newns = {}
        do_cleanup = False
        if new:
            # Include any possible new namespaces
            newns = self.body.nsmap
            for ns in unit.xmlelement.nsmap:
                if ns not in newns:
                    do_cleanup = True
                    newns[ns] = unit.xmlelement.nsmap[ns]

            # Detect if unit is using XML entities
            hasentity = False
            for xmlelement in unit.xmlelement.iterdescendants():
                if xmlelement.tag is etree.Entity:
                    hasentity = True
                    break

            # Copy doctype to include possibly new entities
            if hasentity:
                cloned_doc = copy.deepcopy(unit._store.document)
                cloned_doc.getroot().clear()
                self.XMLdoctype = etree.tostring(
                    cloned_doc, xml_declaration=False, encoding="unicode"
                ).rsplit("\n", 1)[0]

        super().addunit(unit, new)
        # Move aliased namespaces to the <resources> tag
        # The top_nsmap was introduced in LXML 3.5.0
        if do_cleanup:
            etree.cleanup_namespaces(self.body, top_nsmap=newns)

    def removeunit(self, unit):
        unit.removenotes()
        super().removeunit(unit)


class MOKOResourceUnit(AndroidResourceUnit):
    PLURAL_TAG = "plural"


class MOKOResourceFile(AndroidResourceFile):
    UnitClass = MOKOResourceUnit
