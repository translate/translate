#
# Copyright 2025 Translate toolkit contributors
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

"""
Module for handling XLIFF 2.0 files for translation.

XLIFF 2.0 is a major revision from XLIFF 1.x with significant structural changes.
The official recommendation is to use the extension .xlf for XLIFF files.

Multiple Segments Support:
--------------------------
When a <unit> contains multiple <segment> elements, each segment is exposed as
a separate unit for easier handling across the translation stack. The unit ID
is composed as "unitId::segmentId" for multi-segment units.
"""

from __future__ import annotations

from lxml import etree

from translate.storage.workflow import StateEnum as state
from translate.storage.xliff_common import XliffFile, XliffUnit

SEGMENT_SEPARATOR = "::"
SEGMENT_AUTO_ID = "segment-"


class Xliff2Unit(XliffUnit):
    """A single translation unit in the XLIFF 2.0 file."""

    rootNode = "segment"
    languageNode = "source"
    textNode = ""
    namespace = "urn:oasis:names:tc:xliff:document:2.0"

    _default_xml_space = "default"

    # XLIFF 2.0 state values
    S_INITIAL = state.EMPTY
    S_TRANSLATED = state.UNREVIEWED
    S_REVIEWED = state.NEEDS_REVIEW
    S_FINAL = state.FINAL

    statemap = {
        "initial": S_INITIAL,
        "translated": S_TRANSLATED,
        "reviewed": S_REVIEWED,
        "final": S_FINAL,
    }

    statemap_r = {i[1]: i[0] for i in statemap.items()}

    STATE = {
        S_INITIAL: (state.EMPTY, state.NEEDS_WORK),
        S_TRANSLATED: (state.UNREVIEWED, state.NEEDS_REVIEW),
        S_REVIEWED: (state.NEEDS_REVIEW, state.FINAL),
        S_FINAL: (state.FINAL, state.MAX),
    }

    def __init__(self, source, empty: bool = False, **kwargs) -> None:
        """Override the constructor to set xml:space="preserve"."""
        super().__init__(source, empty, **kwargs)
        if empty:
            return
        self._ensure_xml_space_preserve()

    def addnote(self, text: str, origin: str | None = None) -> None:
        """Add a note specifically in the XLIFF 2.0 way."""
        if not text:
            return
        # In XLIFF 2.0, notes are added at the unit level in a notes container
        notes_container = self.xmlelement.find(self.namespaced("notes"))
        if notes_container is None:
            notes_container = etree.SubElement(
                self.xmlelement, self.namespaced("notes")
            )

        note_elem = etree.SubElement(notes_container, self.namespaced("note"))
        note_elem.text = text
        if origin:
            note_elem.set("category", origin)

    def getnotes(self, origin: str | None = None) -> str:
        """Get notes from the unit."""
        notes_text = []
        notes_container = self.xmlelement.find(self.namespaced("notes"))
        if notes_container is not None:
            notes_text.extend(
                note.text
                for note in notes_container.iterchildren(self.namespaced("note"))
                if (origin is None or note.get("category") == origin) and note.text
            )
        return "\n".join(notes_text)

    def removenotes(self, origin: str | None = None) -> None:
        """Remove notes from the unit."""
        notes_container = self.xmlelement.find(self.namespaced("notes"))
        if notes_container is not None:
            if origin is None:
                # Remove entire notes container
                self.xmlelement.remove(notes_container)
            else:
                # Remove only notes with specific origin
                for note in list(notes_container.iterchildren(self.namespaced("note"))):
                    if note.get("category") == origin:
                        notes_container.remove(note)
                # If notes container is now empty, remove it
                if (
                    len(list(notes_container.iterchildren(self.namespaced("note"))))
                    == 0
                ):
                    self.xmlelement.remove(notes_container)

    def getunitelement(self) -> etree._Element:
        if unit_element := self.xmlelement.getparent():
            return unit_element

        unit_element = etree.Element(self.namespaced("unit"))
        unit_element.append(self.xmlelement)
        return unit_element

    def getid(self) -> str | None:
        """Get the unit id."""
        segment_id = self.xmlelement.get("id")
        unit_element = self.getunitelement()
        unit_id = unit_element.get("id")
        if segment_id:
            return f"{unit_id}{SEGMENT_SEPARATOR}{segment_id}"

        all_segments = list(unit_element.iterchildren(self.namespaced("segment")))
        if len(all_segments) == 1:
            return unit_id

        segment_index = all_segments.index(self.xmlelement) + 1
        return f"{unit_id}{SEGMENT_SEPARATOR}{SEGMENT_AUTO_ID}{segment_index}"

    def setid(self, value: str) -> None:
        """Set the unit id."""
        if value:
            segment_id = None
            if SEGMENT_SEPARATOR in value:
                unit_id, segment_id = value.split(SEGMENT_SEPARATOR, 1)
            else:
                unit_id = value
            self.getunitelement().set("id", unit_id)
            if segment_id and not segment_id.startswith(SEGMENT_AUTO_ID):
                self.xmlelement.sedid(segment_id)

    def isfuzzy(self) -> bool:
        return bool(self.target) and self.xmlelement.get("state", None) == "initial"

    def istranslated(self) -> bool:
        return bool(self.target) and self.xmlelement.get("state", None) in {
            "translated",
            "reviewed",
            "final",
            None,
        }

    def isapproved(self):
        return bool(self.target) and self.xmlelement.get("state", None) in {
            "reviewed",
            "final",
        }

    def marktranslated(self):
        self.xmlelement.set("state", "translated")

    def markapproved(self, value=True):
        if value:
            self.xmlelement.set("state", "reviewed")
        else:
            self.xmlelement.set("state", "translated")

    def markfuzzy(self, value=True):
        if value:
            self.xmlelement.set("state", "initial")
        else:
            self.xmlelement.set("state", "translated")


class Xliff2File(XliffFile):
    """Class representing an XLIFF 2.0 file store."""

    UnitClass = Xliff2Unit
    Name = "XLIFF 2.0 Translation File"
    Mimetypes = ["application/x-xliff+xml"]
    Extensions = ["xlf", "xliff"]
    rootNode = "xliff"
    bodyNode = "file"
    XMLskeleton = """<?xml version="1.0" ?>
<xliff version='2.0' xmlns='urn:oasis:names:tc:xliff:document:2.0' srcLang='en'>
<file id='f1'>
</file>
</xliff>"""
    XMLindent = {
        "indent": "  ",
        "max_level": 8,
        "leaves": {"note", "source", "target"},
        "toplevel": False,
        "ignore_preserve": {"unit"},
    }
    namespace = "urn:oasis:names:tc:xliff:document:2.0"

    suggestions_in_format = False

    def initbody(self) -> None:
        """Initialize the file body."""
        self.namespace = self.document.getroot().nsmap.get(None, self.namespace)

        # Get the file node
        if self._filename:
            filenode = self.getfilenode(self._filename, createifmissing=True)
        else:
            try:
                filenode = next(
                    self.document.getroot().iterchildren(self.namespaced("file"))
                )
            except StopIteration:
                # Create a default file node
                filenode = etree.SubElement(
                    self.document.getroot(), self.namespaced("file")
                )
                filenode.set("id", "f1")
        self.body = filenode

    def createfilenode(self, filename, sourcelanguage=None, targetlanguage=None):
        """Creates a file node with the given filename."""
        if sourcelanguage is None:
            sourcelanguage = self.sourcelanguage
        if targetlanguage is None:
            targetlanguage = self.targetlanguage

        filenode = etree.Element(self.namespaced("file"))
        filenode.set("id", filename or "f1")
        if sourcelanguage:
            # In XLIFF 2.0, srcLang is on the xliff root element
            self.document.getroot().set("srcLang", sourcelanguage)
        if targetlanguage:
            # In XLIFF 2.0, trgLang is on the xliff root element
            self.document.getroot().set("trgLang", targetlanguage)
        return filenode

    @staticmethod
    def getfilename(filenode):
        """Returns the id of the given file node."""
        return filenode.get("id")

    @staticmethod
    def setfilename(filenode, filename):
        """Set the id of the given file."""
        return filenode.set("id", filename)

    def addunit(self, unit: Xliff2Unit, new: bool = True) -> None:
        """Adds the given unit to the file."""
        super().addunit(unit, new=False)
        if new:
            # TODO: merge units with same ID and different segment
            self.body.append(unit.getunitelement())

    def getsourcelanguage(self) -> str:
        """Get the source language for this file."""
        return self.document.getroot().get("srcLang", "en")

    def setsourcelanguage(self, lang: str) -> None:
        """Set the source language for this file."""
        self.document.getroot().set("srcLang", lang)

    def gettargetlanguage(self) -> str | None:
        """Get the target language for this file."""
        return self.document.getroot().get("trgLang")

    def settargetlanguage(self, lang: str) -> None:
        """Set the target language for this file."""
        if lang:
            self.document.getroot().set("trgLang", lang)

    sourcelanguage = property(getsourcelanguage, setsourcelanguage)
    targetlanguage = property(gettargetlanguage, settargetlanguage)
