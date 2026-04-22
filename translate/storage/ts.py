#
# Copyright 2004-2007 Zuza Software Foundation
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
#

"""
Module for parsing Qt .ts files for translation.

Currently this module supports the old format of .ts files. Some applications
use the newer .ts format which are documented here:
`TS file format 4.3 <http://doc.qt.io/archives/4.3/linguist-ts-file-format.html>`_,
`Example <http://svn.ez.no/svn/ezcomponents/trunk/Translation/docs/linguist-format.txt>`_

`Specification of the valid variable entries <http://doc.qt.io/qt-5/qstring.html#arg>`_,
`2 <http://doc.qt.io/qt-5/qstring.html#arg-2>`_
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, BinaryIO, TextIO

from lxml import etree

from translate.misc.xml_helpers import parse_xml

if TYPE_CHECKING:
    from collections.abc import Iterator

TSInput = str | bytes | BinaryIO | TextIO
MessageNode = etree._Element
ContextNode = etree._Element
XML_DECLARATION_RE = re.compile(
    r"""^\s*<\?xml(?P<attrs>[^?]*?)\?>""",
    re.IGNORECASE | re.DOTALL,
)


class QtTsParser:
    def __init__(self, inputfile: TSInput | None = None) -> None:
        """Make a new QtTsParser, reading from the given inputfile if required."""
        self.filename = getattr(inputfile, "filename", None)
        self.knowncontextnodes: dict[str, ContextNode] = {}
        self.doctype: str | None
        self.document: etree._ElementTree
        if inputfile is None:
            self.doctype = "<!DOCTYPE TS>"
            self.document = self._parse_content(b"<TS></TS>")
        else:
            if isinstance(inputfile, bytes):
                content = inputfile
            elif isinstance(inputfile, str) and not self._looks_like_xml(inputfile):
                self.filename = inputfile
                with open(inputfile, "rb") as input_handle:
                    content = input_handle.read()
            elif isinstance(inputfile, str):
                content = inputfile
            else:
                content = inputfile.read()
            self.document = self._parse_content(content)
            # Preserve the original doctype so round-tripped TS files keep the
            # same declaration shape as the input.
            self.doctype = self.document.docinfo.doctype or None
            assert self.document.getroot().tag == "TS"

    @staticmethod
    def _parse_content(content: str | bytes) -> etree._ElementTree:
        if isinstance(content, str):
            content = QtTsParser._normalize_text_input(content).encode("utf-8")
        root = parse_xml(content)
        return root.getroottree()

    @staticmethod
    def _looks_like_xml(content: str) -> bool:
        return content.lstrip().startswith("<")

    @staticmethod
    def _normalize_text_input(content: str) -> str:
        """
        Normalize text input before parsing as UTF-8 bytes.

        Text streams are already decoded, so any XML encoding declaration no
        longer reflects the in-memory string. Drop just the encoding attribute
        to preserve the remaining declaration fields without corrupting text.
        """
        declaration = XML_DECLARATION_RE.match(content)
        if declaration is None:
            return content
        attrs = QtTsParser._strip_xml_encoding_attribute(declaration.group("attrs"))
        return f"<?xml{attrs}?>{content[declaration.end() :]}"

    @staticmethod
    def _strip_xml_encoding_attribute(attrs: str) -> str:
        result: list[str] = []
        index = 0
        attr_count = len(attrs)

        while index < attr_count:
            whitespace_start = index
            while index < attr_count and attrs[index].isspace():
                index += 1

            if index >= attr_count:
                result.append(attrs[whitespace_start:index])
                break

            name_start = index
            while index < attr_count and (
                attrs[index].isalnum() or attrs[index] in "._:-"
            ):
                index += 1
            if name_start == index:
                return attrs

            name = attrs[name_start:index]

            while index < attr_count and attrs[index].isspace():
                index += 1
            if index >= attr_count or attrs[index] != "=":
                return attrs
            index += 1

            while index < attr_count and attrs[index].isspace():
                index += 1
            if index >= attr_count or attrs[index] not in {'"', "'"}:
                return attrs

            quote = attrs[index]
            index += 1
            value_end = attrs.find(quote, index)
            if value_end == -1:
                return attrs
            index = value_end + 1

            if name.lower() != "encoding":
                result.append(attrs[whitespace_start:index])

        return "".join(result)

    @property
    def documentElement(self) -> etree._Element:
        return self.document.getroot()

    def addtranslation(
        self,
        contextname: str,
        source: str,
        translation: str,
        comment: str | None = None,
        transtype: str | None = None,
        createifmissing: bool = False,
    ) -> bool:
        """Adds the given translation (will create the nodes required if asked). Returns success."""
        contextnode = self.getcontextnode(contextname)
        if contextnode is None:
            if not createifmissing:
                return False
            contextnode = etree.SubElement(self.documentElement, "context")
            etree.SubElement(contextnode, "name").text = contextname
            self.knowncontextnodes[contextname] = contextnode
        if not createifmissing:
            return False
        messagenode = etree.SubElement(contextnode, "message")
        etree.SubElement(messagenode, "source").text = source
        if comment:
            etree.SubElement(messagenode, "comment").text = comment
        translationnode = etree.SubElement(messagenode, "translation")
        translationnode.text = translation
        if transtype:
            translationnode.set("type", transtype)
        return True

    def getxml(self) -> str:
        """Return the ts file as xml."""
        xml = etree.tostring(
            self.document,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
            doctype=self.doctype,
        ).decode("utf-8")
        # Keep output compact and match the historic behavior of dropping
        # blank lines introduced by pretty printing.
        return "\n".join(line for line in xml.split("\n") if line.strip())

    @staticmethod
    def getcontextname(contextnode: ContextNode) -> str:
        """Returns the name of the given context."""
        return contextnode.findtext("name", default="")

    def getcontextnode(self, contextname: str) -> ContextNode | None:
        """Finds the contextnode with the given name."""
        contextnode = self.knowncontextnodes.get(contextname)
        if contextnode is not None:
            return contextnode
        # Cache by context name because repeated lookups are common during
        # addtranslation() and iterative reads.
        for contextnode in self.documentElement.findall("context"):
            if self.getcontextname(contextnode) == contextname:
                self.knowncontextnodes[contextname] = contextnode
                return contextnode
        return None

    def getmessagenodes(
        self, context: str | ContextNode | None = None
    ) -> list[MessageNode]:
        """Returns all the messagenodes, limiting to the given context (name or node) if given."""
        if context is None:
            return self.documentElement.findall("./context/message")
        if isinstance(context, str):
            context = self.getcontextnode(context)
            if context is None:
                return []
        return context.findall("message")

    @staticmethod
    def getmessagesource(message: MessageNode) -> str:
        """Returns the message source for a given node."""
        return message.findtext("source", default="")

    @staticmethod
    def getmessagetranslation(message: MessageNode) -> str:
        """Returns the message translation for a given node."""
        return message.findtext("translation", default="")

    @staticmethod
    def getmessagetype(message: MessageNode) -> str:
        """Returns the message translation attributes for a given node."""
        translationnode = message.find("translation")
        if translationnode is None:
            return ""
        return translationnode.get("type", "")

    @staticmethod
    def getmessagecomment(message: MessageNode) -> str:
        """Returns the message comment for a given node."""
        return message.findtext("comment", default="")

    def iteritems(self) -> Iterator[tuple[str, list[MessageNode]]]:
        """Iterates through (contextname, messages)."""
        for contextnode in self.documentElement.findall("context"):
            yield self.getcontextname(contextnode), self.getmessagenodes(contextnode)
