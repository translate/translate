#
# Copyright 2006-2010 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""module for handling TBX glossary files."""

from io import BytesIO

from lxml import etree

from translate.misc.xml_helpers import (
    getXMLlang,
    getXMLspace,
    safely_set_text,
    setXMLlang,
)
from translate.storage import lisa


def _normalize_language(language: str | None) -> str | None:
    if not language:
        return None
    return language.replace("_", "-").lower()


class tbxunit(lisa.LISAunit):
    """
    A single term in the TBX file.  Provisional work is done to make several
    languages possible.
    """

    rootNode = "termEntry"
    languageNode = "langSet"
    textNode = "term"

    def _store_language(self, name: str) -> str | None:
        store = getattr(self, "_store", None)
        if store is None:
            return None
        return getattr(store, name, None)

    def _store_language_or_default(self, name: str, default: str) -> str:
        return self._store_language(name) or default

    def _get_language_node(self, language: str | None):
        language = _normalize_language(language)
        if language is None:
            return None
        for node in self.getlanguageNodes():
            if _normalize_language(getXMLlang(node)) == language:
                return node
        return None

    def _get_source_language_node(self):
        return self._get_language_node(self._store_language("sourcelanguage"))

    def _get_target_language_node(self):
        return self._get_language_node(self._store_language("targetlanguage"))

    def _get_fallback_source_node(self):
        language_nodes = self.getlanguageNodes()
        target_node = self._get_target_language_node()
        for node in language_nodes:
            if node is not target_node:
                return node
        return self.getlanguageNode(lang=None, index=0)

    def _get_fallback_target_node(self, language_nodes, source_node=None):
        if len(language_nodes) < 2:
            return None
        target_node = self.getlanguageNode(lang=None, index=1)
        if target_node is not None and target_node is not source_node:
            return target_node
        for node in language_nodes:
            if node is not source_node:
                return node
        return None

    def get_source_dom(self):
        source_language = self._store_language("sourcelanguage")
        if _normalize_language(source_language) is not None:
            return self._get_source_language_node()
        return self._get_fallback_source_node()

    def set_source_dom(self, dom_node) -> None:
        source_node = self.get_source_dom()
        if source_node is not None:
            self.xmlelement.replace(source_node, dom_node)
        else:
            self.xmlelement.append(dom_node)

    source_dom = property(get_source_dom, set_source_dom)

    @property
    def source(self):
        return self.getNodeText(
            self.source_dom, getXMLspace(self.xmlelement, self._default_xml_space)
        )

    @source.setter
    def source(self, source) -> None:
        self.setsource(source)

    def setsource(self, text, sourcelang=None) -> None:
        super().setsource(
            text, sourcelang or self._store_language_or_default("sourcelanguage", "en")
        )

    def set_target_dom(self, dom_node, append=False) -> None:
        language_nodes = self.getlanguageNodes()
        target_node = self.get_target_dom()
        if dom_node is None:
            if not append and target_node is not None:
                self.xmlelement.remove(target_node)
            return

        if append:
            self.xmlelement.append(dom_node)
        elif target_node is not None:
            self.xmlelement.replace(target_node, dom_node)
        elif not language_nodes:
            self.xmlelement.append(dom_node)
        else:
            source_node = self.get_source_dom()
            if source_node is None:
                self.xmlelement.insert(1, dom_node)
            else:
                self.xmlelement.insert(self.xmlelement.index(source_node) + 1, dom_node)

    def get_target_dom(self, lang=None):
        if lang:
            return self._get_language_node(lang)

        target_language = self._store_language("targetlanguage")
        if _normalize_language(target_language) is not None:
            return self._get_target_language_node()

        language_nodes = self.getlanguageNodes()
        if len(language_nodes) == 2:
            source_node = self._get_source_language_node()
            if source_node is not None:
                return (
                    language_nodes[1]
                    if language_nodes[0] is source_node
                    else language_nodes[0]
                )
            target_node = self._get_target_language_node()
            if target_node is not None:
                return target_node
            return self._get_fallback_target_node(language_nodes)

        if len(language_nodes) > 2:
            source_node = self.get_source_dom()
            target_node = self._get_target_language_node()
            if target_node is not None and target_node is not source_node:
                return target_node
            return self._get_fallback_target_node(language_nodes, source_node)

        return self._get_fallback_target_node(language_nodes)

    target_dom = property(get_target_dom)

    def settarget(self, target, lang=None, append=False) -> None:
        super().settarget(
            target,
            lang or self._store_language_or_default("targetlanguage", "xx"),
            append=append,
        )

    def createlanguageNode(self, lang, text, purpose):  # ty:ignore[invalid-method-override]
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

    def _get_origin_element(self, origin: str | None):
        if origin == "pos":
            return self.namespaced("termNote")
        if origin == "definition":
            return self.namespaced("descrip")
        return self.namespaced("note")

    def _matches_note_origin(self, node, origin=None) -> bool:
        return (
            origin in {"pos", "definition", None} or node.get("from") == origin
        ) and not (
            self._is_administrative_status_term_node(node)
            or self._is_translation_needed_node(node)
        )

    def removenotes(self, origin=None) -> None:
        """Remove all the translator notes."""
        notes = [
            note
            for note in self._getnotenodes(origin=origin)
            if self._matches_note_origin(note, origin)
        ]
        for note in notes:
            parent = note.getparent()
            if parent is not None:
                parent.remove(note)

    def addnote(self, text, origin=None, position="append") -> None:
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

    def _getnotelist(self, origin=None) -> list[str]:
        """
        Returns the text from notes matching ``origin`` or all notes.

        :param origin: The origin of the note (or note type)
        :return: The text from notes matching ``origin``
        """
        note_nodes = self._getnotenodes(origin=origin)
        # TODO: consider using xpath to construct initial_list directly
        # or to simply get the correct text from the outset (just remember to
        # check for duplication.
        initial_list = [
            self._getnodetext(node)
            for node in note_nodes
            if self._matches_note_origin(node, origin)
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


class tbxfile(lisa.LISAfile[tbxunit]):
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

    def __init__(
        self, inputfile=None, sourcelanguage=None, targetlanguage=None, **kwargs
    ) -> None:
        if inputfile is None and sourcelanguage is None:
            sourcelanguage = "en"
        super().__init__(
            inputfile,
            sourcelanguage=sourcelanguage,
            targetlanguage=targetlanguage,
            **kwargs,
        )
        if inputfile is not None:
            if sourcelanguage is not None:
                self.setsourcelanguage(sourcelanguage)
            if targetlanguage is not None:
                self.settargetlanguage(targetlanguage)

    @classmethod
    def parsestring(cls, storestring, sourcelanguage=None, targetlanguage=None):
        if isinstance(storestring, str):
            storestring = storestring.encode(cls.default_encoding)
        return cls(
            BytesIO(storestring),
            sourcelanguage=sourcelanguage,
            targetlanguage=targetlanguage,
        )

    def addsourceunit(self, source):
        unit = self.UnitClass(None)
        unit._store = self
        unit.source = source
        self.addunit(unit)
        return unit

    def addheader(self) -> None:
        """Initialise headers with TBX specific things."""
        setXMLlang(self.document.getroot(), self.sourcelanguage)
