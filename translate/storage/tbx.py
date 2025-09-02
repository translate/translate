#
# Copyright 2006-2010 Zuza Software Foundation
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

"""module for handling TBX glossary files."""

from lxml import etree

from translate.misc.xml_helpers import (
    getXMLspace,
    safely_set_text,
    setXMLlang,
)
from translate.storage import lisa


class tbxunit(lisa.LISAunit):
    """
    A single term in the TBX file.  Provisional work is done to make several
    languages possible.
    """

    rootNode = "termEntry"
    languageNode = "langSet"
    textNode = "term"

    def createlanguageNode(self, lang, text, purpose):
        """Returns a langset xml Element setup with given parameters."""
        langset = etree.Element(self.languageNode)
        setXMLlang(langset, lang)
        tig = etree.SubElement(langset, "tig")  # or ntig with termGrp inside
        term = etree.SubElement(tig, self.textNode)
        # probably not what we want:
        # lisa.setXMLspace(term, "preserve")
        safely_set_text(term, text)
        return langset

    def getid(self):
        # The id attribute is optional
        return self.xmlelement.get("id") or self.source

    def setid(self, value):
        return self.xmlelement.set("id", value)

    def _get_origin_element(self, origin: str):
        if origin == "pos":
            return self.namespaced("termNote")
        if origin == "definition":
            return self.namespaced("descrip")
        return self.namespaced("note")

    def removenotes(self, origin=None):
        """Remove all the translator notes."""
        notes = self.xmlelement.iterdescendants(self._get_origin_element(origin))
        for note in notes:
            self.xmlelement.remove(note)

    def addnote(self, text, origin=None, position="append"):
        """Add a note specifically in a "note" tag."""
        if position != "append":
            self.removenotes(origin=origin)

        if text:
            text = text.strip()
        if not text:
            return
        note = etree.SubElement(self.xmlelement, self._get_origin_element(origin))
        safely_set_text(note, text)
        if origin and origin not in {"pos", "definition"}:
            note.set("from", origin)

    def _getnotenodes(self, origin=None):
        """Get all nodes matching ``origin`` in the XML document."""
        return self.xmlelement.iterdescendants(self._get_origin_element(origin))

    def _getnodetext(self, node):
        """
        Get the plaintext content of the given node considering the xml namespace
        and space configuration.
        """
        return lisa.getText(node, getXMLspace(self.xmlelement, self._default_xml_space))

    def _is_administrative_status_term_node(self, node) -> bool:
        """Checks if the node is a `<termNote type="administrativeStatus">` node."""
        return (
            self.namespaced("termNote") == node.tag
            and node.get("type") == "administrativeStatus"
        )

    def _is_translation_needed_node(self, node) -> bool:
        """Checks if the node is a `<descrip type="Translation needed">` node."""
        return (
            self.namespaced("descrip") == node.tag
            and node.get("type") == "Translation needed"
        )

    def _getnotelist(self, origin=None):
        """
        Returns the text from notes matching ``origin`` or all notes.

        :param origin: The origin of the note (or note type)
        :type origin: String
        :return: The text from notes matching ``origin``
        :rtype: List
        """
        note_nodes = self._getnotenodes(origin=origin)
        # TODO: consider using xpath to construct initial_list directly
        # or to simply get the correct text from the outset (just remember to
        # check for duplication.
        initial_list = [
            self._getnodetext(node)
            for node in note_nodes
            if (
                (origin in {"pos", "definition", None} or node.get("from") == origin)
                and not (
                    self._is_administrative_status_term_node(node)
                    or self._is_translation_needed_node(node)
                )
            )
        ]

        # Remove duplicate entries from list:
        dictset = {}
        return [
            dictset.setdefault(note, note)
            for note in initial_list
            if note not in dictset
        ]

    def getnotes(self, origin=None):
        return "\n".join(self._getnotelist(origin=origin))

    def istranslatable(self) -> bool:
        for node in self._getnotenodes(origin="definition"):
            if self._is_translation_needed_node(node):
                return self._getnodetext(node).strip().lower() == "yes"
        return super().istranslatable()

    def isobsolete(self) -> bool:
        """
        Indicate whether a unit is obsolete.

        The deprecated administrative status in TBX basic maps to translate toolkit's
        concept of obsolete units.

        :rtype: bool
        """
        for note in self._getnotenodes(origin="pos"):
            if self._is_administrative_status_term_node(note) and self._getnodetext(
                note
            ).strip().lower() in {
                "deprecated",
                "deprecatedtermadmnsts",
                "deprecatedterm-admn-sts",  # codespell:ignore
            }:
                return True

        return super().isobsolete()


class tbxfile(lisa.LISAfile):
    """Class representing a TBX file store."""

    UnitClass = tbxunit
    Name = "TBX Glossary"
    Mimetypes = ["application/x-tbx"]
    Extensions = ["tbx"]
    rootNode = "martif"
    bodyNode = "body"
    XMLskeleton = """<?xml version="1.0"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX">
<martifHeader>
<fileDesc>
<sourceDesc><p>Translate Toolkit</p></sourceDesc>
</fileDesc>
</martifHeader>
<text><body></body></text>
</martif>"""
    XMLindent = {"indent": "    ", "toplevel": False}

    def addheader(self):
        """Initialise headers with TBX specific things."""
        setXMLlang(self.document.getroot(), self.sourcelanguage)
