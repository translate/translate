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

from collections import defaultdict, deque
from dataclasses import dataclass
from io import BytesIO
from typing import Literal

from lxml import etree

from translate.misc.xml_helpers import (
    getXMLspace,
    getXMLspaceInherited,
    safely_set_text,
    setXMLlang,
)
from translate.storage import lisa


@dataclass(frozen=True)
class TBXNote:
    """A note with its original category and origin."""

    text: str
    origin: str | None = None
    category: str | None = None
    scope: Literal["concept", "language", "term"] = "term"


@dataclass(frozen=True)
class TBXTerm:
    """One terminology alternative, independent of other languages' terms."""

    text: str
    id: str | None = None
    administrative_status: str | None = None
    notes: tuple[TBXNote, ...] = ()

    @property
    def deprecated(self) -> bool:
        return (self.administrative_status or "").strip().lower() in {
            "deprecated",
            "deprecatedtermadmnsts",
            "deprecatedterm-admn-sts",  # codespell:ignore
        }


def match_term_indices(old: list[str], new: list[str]) -> list[int | None]:
    """Match unchanged occurrences first, then unmatched terms in XML order."""
    available: dict[str, deque[int]] = defaultdict(deque)
    for index, text in enumerate(old):
        available[text].append(index)
    matches = [available[text].popleft() if available[text] else None for text in new]
    used = {index for index in matches if index is not None}
    remaining = iter(index for index in range(len(old)) if index not in used)
    return [next(remaining, None) if index is None else index for index in matches]


class tbxunit(lisa.MultilingualLISAunit):
    """
    A single term in the TBX file.  Provisional work is done to make several
    languages possible.
    """

    rootNode = "termEntry"
    languageNode = "langSet"
    textNode = "term"

    def _metadata_nodes(self, node):
        """Walk metadata without entering a different language or term scope."""
        for child in node:
            if child.tag in {
                self.namespaced("langSet"),
                self.namespaced("tig"),
                self.namespaced("ntig"),
            }:
                continue
            yield child
            yield from self._metadata_nodes(child)

    def _notes_in_scope(
        self, node, scope: Literal["concept", "language", "term"]
    ) -> tuple[TBXNote, ...]:
        result = []
        for child in self._metadata_nodes(node):
            if self._is_translation_needed_node(
                child
            ) or self._is_administrative_status_term_node(child):
                continue
            if child.tag == self.namespaced("descrip"):
                origin = "definition"
            elif child.tag == self.namespaced("termNote"):
                origin = "pos"
            elif child.tag == self.namespaced("note"):
                origin = child.get("from")
            else:
                continue
            result.append(
                TBXNote(self._getnodetext(child), origin, child.get("type"), scope)
            )
        return tuple(result)

    def get_common_notes(self, *, source: bool = False) -> tuple[TBXNote, ...]:
        """Return concept and selected-language notes, excluding term notes."""
        notes = self._notes_in_scope(self.xmlelement, "concept")
        language = self.source_dom if source else self.target_dom
        if language is not None:
            notes += self._notes_in_scope(language, "language")
        return notes

    def set_common_note(self, text: str, *, source: bool = False) -> None:
        """Replace an explanation without modifying any term-level metadata."""
        origin = "definition" if source else "translator"
        scopes = [self.xmlelement] if source else []
        language = self.source_dom if source else self.target_dom
        if not source and language is None and text:
            language = self.createlanguageNode(
                self._get_target_language() or "xx", "", "target"
            )
            self._insert_target_language(language)
        if language is not None:
            scopes.append(language)
        replacement = None
        for scope in scopes:
            for node in list(self._metadata_nodes(scope)):
                if node.tag != self._get_origin_element(origin):
                    continue
                if source:
                    matches = node.get("type") in {None, "definition"}
                else:
                    matches = node.get("from") == "translator"
                if matches:
                    parent = node.getparent()
                    grouped = parent.tag == self.namespaced("descripGrp")
                    if source and text and replacement is None:
                        replacement = node
                        continue
                    parent.remove(node)
                    if grouped and parent.find(self.namespaced("descrip")) is None:
                        # The group's auxiliary information belongs to its
                        # description and cannot remain without that description.
                        parent.getparent().remove(parent)
        if not text:
            return
        if replacement is not None:
            replacement.set("type", "definition")
            for child in list(replacement):
                replacement.remove(child)
            safely_set_text(replacement, text)
            return
        parent = self.xmlelement if source or language is None else language
        node = etree.Element(self._get_origin_element(origin))
        containers = {
            self.namespaced("langSet"),
            self.namespaced("tig"),
            self.namespaced("ntig"),
        }
        for child in parent:
            if child.tag in containers:
                child.addprevious(node)
                break
        else:
            parent.append(node)
        if source:
            node.set("type", "definition")
        else:
            node.set("from", "translator")
        safely_set_text(node, text)

    def _get_terms(self, language) -> list[TBXTerm]:
        if language is None:
            return []
        common = self._notes_in_scope(
            self.xmlelement, "concept"
        ) + self._notes_in_scope(language, "language")
        result = []
        for tig in language.findall(self.namespaced("tig")):
            term = tig.find(self.namespaced("term"))
            status = next(
                (
                    self._getnodetext(node)
                    for node in self._metadata_nodes(tig)
                    if self._is_administrative_status_term_node(node)
                ),
                None,
            )
            result.append(
                TBXTerm(
                    text=self.getNodeText(
                        tig, getXMLspaceInherited(tig, self._default_xml_space)
                    )
                    or "",
                    id=tig.get("id") or (term.get("id") if term is not None else None),
                    administrative_status=status,
                    notes=common + self._notes_in_scope(tig, "term"),
                )
            )
        return result

    def get_source_terms(self) -> list[TBXTerm]:
        """Return every source tig, retaining order, IDs and scoped metadata."""
        return self._get_terms(self.source_dom)

    def get_target_terms(self, lang: str | None = None) -> list[TBXTerm]:
        """Return all terms for the selected or explicitly requested target."""
        return self._get_terms(self.get_target_dom(lang))

    def _insert_target_language(self, language) -> None:
        """Keep a newly selected target and its source in the fallback pair."""
        source = self.source_dom
        languages = self.getlanguageNodes()
        if source is not None and languages[0] is not source:
            languages[0].addprevious(source)
        self.set_target_dom(language)

    def _set_terms(
        self, language, values: list[str], lang: str, *, source: bool = False
    ) -> None:
        if any(not isinstance(value, str) for value in values):
            raise TypeError("TBX terms must be strings")
        if language is None:
            if not values:
                return
            language = etree.SubElement(self.xmlelement, self.namespaced("langSet"))
            setXMLlang(language, lang)
            # Use the same lookup as readers, including default-country matches
            # and exact-match precedence, to decide whether to update fallback order.
            selected = self.source_dom if source else self.target_dom
            if selected is language:
                self.xmlelement.remove(language)
                if source:
                    languages = self.getlanguageNodes()
                    if languages:
                        languages[0].addprevious(language)
                    else:
                        self.xmlelement.append(language)
                else:
                    self._insert_target_language(language)
        nodes = language.findall(self.namespaced("tig"))
        old = [term.text for term in self._get_terms(language)]
        if old == values and (values or nodes):
            return
        indices = match_term_indices(old, values)
        replacements = []
        for text, index in zip(values, indices, strict=True):
            if index is None:
                tig = etree.Element(self.namespaced("tig"))
                term = etree.Element(self.namespaced("term"))
                tig.insert(0, term)
            else:
                tig = nodes[index]
                term = tig.find(self.namespaced("term"))
                if term is None:
                    term = etree.Element(self.namespaced("term"))
                    tig.insert(0, term)
            if index is None or old[index] != text:
                # A text edit replaces inline content only in the edited term.
                for child in list(term):
                    term.remove(child)
                safely_set_text(term, text)
            replacements.append(tig)
        position = language.index(nodes[0]) if nodes else len(language)
        for node in nodes:
            language.remove(node)
        if not replacements:
            tig = etree.Element(self.namespaced("tig"))
            etree.SubElement(tig, self.namespaced("term"))
            replacements.append(tig)
        for offset, node in enumerate(replacements):
            language.insert(position + offset, node)
        self._rich_source = self._rich_target = None
        self._invalidate_store_indexes()

    def set_source_terms(self, values: list[str], lang: str | None = None) -> None:
        """Replace source alternatives using text matching followed by position."""
        language = (
            self._get_language_node(lang) if lang is not None else self.source_dom
        )
        self._set_terms(
            language,
            values,
            lang or self._get_source_language() or "en",
            source=True,
        )

    def set_target_terms(self, values: list[str], lang: str | None = None) -> None:
        """Replace target alternatives, preserving metadata of reused terms."""
        self._set_terms(
            self.get_target_dom(lang),
            values,
            lang or self._get_target_language() or "xx",
        )

    def setsource(self, text, sourcelang=None) -> None:
        self._invalidate_store_indexes()
        language = self.source_dom
        if language is not None:
            if sourcelang and self._get_language_node(sourcelang) is not language:
                setXMLlang(language, sourcelang)
            term = language.find(f".//{self.namespaced('term')}")
            if term is None:
                tig = language.find(self.namespaced("tig"))
                if tig is None:
                    tig = etree.SubElement(language, self.namespaced("tig"))
                term = etree.Element(self.namespaced("term"))
                tig.insert(0, term)
            if self.getNodeText(language) == text:
                return
            for child in list(term):
                term.remove(child)
            safely_set_text(term, text)
            self._rich_source = None
            return
        super().setsource(text, sourcelang)

    def settarget(self, target, lang=None, append=False) -> None:
        """Populate empty language sets before delegating scalar target writes."""
        language = self.get_target_dom(lang)
        if target is None and language is not None:
            term = language.find(f".//{self.namespaced('term')}")
            if term is not None:
                term.text = None
                for child in list(term):
                    term.remove(child)
            self._rich_target = None
            self._invalidate_store_indexes()
            return
        if (
            target is not None
            and language is not None
            and language.find(f".//{self.namespaced('term')}") is None
        ):
            tig = language.find(self.namespaced("tig"))
            if tig is None:
                tig = etree.SubElement(language, self.namespaced("tig"))
            tig.insert(0, etree.Element(self.namespaced("term")))
        super().settarget(target, lang, append)

    def istranslated(self) -> bool:
        return (
            any(term.text for term in self.get_target_terms()) or bool(self.target)
        ) and not self.isfuzzy()

    def isblank(self) -> bool:
        return (
            not any(
                term.text
                for language in self.getlanguageNodes()
                for term in self._get_terms(language)
            )
            and super().isblank()
        )

    def createlanguageNode(self, lang, text, purpose):  # ty:ignore[invalid-method-override]
        """Returns a langset xml Element setup with given parameters."""
        langset = etree.Element(self.namespaced(self.languageNode))
        setXMLlang(langset, lang)
        tig = etree.SubElement(langset, self.namespaced("tig"))
        term = etree.SubElement(tig, self.namespaced(self.textNode))
        # probably not what we want:
        # lisa.setXMLspace(term, "preserve")
        safely_set_text(term, text)
        return langset

    def getid(self):
        # The id attribute is optional
        return self.xmlelement.get("id") or self.source

    def setid(self, value):
        self._invalidate_store_indexes()
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
        # Translation-needed flags retain their concept-wide meaning even when
        # stored within language or term metadata.
        for node in self.xmlelement.iterdescendants():
            if self._is_translation_needed_node(node):
                return self._getnodetext(node).strip().lower() == "yes"
        return (
            any(term.text for term in self.get_source_terms())
            or super().istranslatable()
        )

    def isobsolete(self) -> bool:
        """
        Indicate whether a unit is obsolete.

        The deprecated administrative status in TBX basic maps to translate toolkit's
        concept of obsolete units.
        """
        terms = [
            term
            for language in self.getlanguageNodes()
            for term in self._get_terms(language)
            if term.text
        ]
        return bool(terms) and all(term.deprecated for term in terms)


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

    def setsourcelanguage(self, sourcelanguage: str) -> None:
        super().setsourcelanguage(sourcelanguage)
        self._invalidate_indexes()

    def add_unit_to_index(self, unit) -> None:
        """Keep empty placeholder terms out of identity and source lookups."""
        super().add_unit_to_index(unit)
        # Empty source keys are meaningful in other formats, such as PO.
        self.id_index.pop("", None)
        self.sourceindex.pop("", None)

    def settargetlanguage(self, targetlanguage: str | None) -> None:
        super().settargetlanguage(targetlanguage)
        self._invalidate_indexes()

    def addheader(self) -> None:
        """Initialise headers with TBX specific things."""
        setXMLlang(self.document.getroot(), self.sourcelanguage)
