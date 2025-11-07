#
# Copyright 2025 Zuza Software Foundation
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
"""

from lxml import etree

from translate.misc.multistring import multistring
from translate.misc.xml_helpers import (
    clear_content,
    getXMLspace,
    safely_set_text,
    setXMLlang,
    setXMLspace,
)
from translate.storage import base, lisa
from translate.storage.placeables.lisa import strelem_to_xml, xml_to_strelem
from translate.storage.workflow import StateEnum as state


class xliff2unit(lisa.LISAunit):
    """A single translation unit in the XLIFF 2.0 file."""

    rootNode = "unit"
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

    def __init__(self, source, empty=False, **kwargs):
        """Override the constructor to set xml:space="preserve"."""
        super().__init__(source, empty, **kwargs)
        if empty:
            return
        setXMLspace(self.xmlelement, "preserve")

    def createlanguageNode(self, lang, text, purpose):
        """Returns an xml Element setup with given parameters."""
        assert purpose
        langset = etree.Element(self.namespaced(purpose))
        safely_set_text(langset, text)
        return langset

    def getlanguageNodes(self):
        """We override this to get source and target nodes within segments."""
        nodes = []
        # In XLIFF 2.0, source and target are within segment elements
        for segment in self.xmlelement.iterchildren(self.namespaced("segment")):
            source = None
            target = None
            try:
                source = next(segment.iterchildren(self.namespaced(self.languageNode)))
                target = next(segment.iterchildren(self.namespaced("target")))
                nodes.extend([source, target])
            except StopIteration:
                if source is not None:
                    nodes.append(source)
                if target is not None:
                    nodes.append(target)
        return nodes

    def get_source_dom(self):
        """Get the source DOM element."""
        segment = self._get_segment()
        if segment is None:
            return None
        return self._get_source_from_segment(segment)

    def set_source_dom(self, dom_node):
        """Set the source DOM element."""
        segment = self._get_or_create_segment()
        # Remove existing source
        existing_source = self._get_source_from_segment(segment)
        if existing_source is not None:
            segment.remove(existing_source)
        # Insert new source at the beginning
        if dom_node is not None:
            segment.insert(0, dom_node)

    source_dom = property(get_source_dom, set_source_dom)

    def get_target_dom(self, lang=None):
        """Get the target DOM element."""
        segment = self._get_segment()
        if segment is None:
            return None
        return self._get_target_from_segment(segment)

    def set_target_dom(self, dom_node, append=False):
        """Set the target DOM element."""
        segment = self._get_or_create_segment()
        # Remove existing target
        existing_target = self._get_target_from_segment(segment)
        if existing_target is not None:
            segment.remove(existing_target)
        # Insert new target after source
        if dom_node is not None:
            source_node = self._get_source_from_segment(segment)
            if source_node is not None:
                source_index = list(segment).index(source_node)
                segment.insert(source_index + 1, dom_node)
            else:
                segment.append(dom_node)

    target_dom = property(get_target_dom, set_target_dom)

    def set_rich_source(self, value, sourcelang="en"):
        """Set the rich source content."""
        # Find or create segment
        segment = self._get_or_create_segment()
        sourcelanguageNode = self._get_source_from_segment(segment)
        if sourcelanguageNode is None:
            sourcelanguageNode = self.createlanguageNode(sourcelang, "", "source")
            segment.insert(0, sourcelanguageNode)

        clear_content(sourcelanguageNode)
        strelem_to_xml(sourcelanguageNode, value[0])

    @property
    def rich_source(self):
        """Get the rich source content."""
        segment = self._get_segment()
        if segment is None:
            return [xml_to_strelem("", getXMLspace(self.xmlelement, self._default_xml_space))]
        source_node = self._get_source_from_segment(segment)
        if source_node is None:
            return [xml_to_strelem("", getXMLspace(self.xmlelement, self._default_xml_space))]
        return [
            xml_to_strelem(
                source_node, getXMLspace(self.xmlelement, self._default_xml_space)
            )
        ]

    @rich_source.setter
    def rich_source(self, value):
        self.set_rich_source(value)

    def set_rich_target(self, value, lang="xx", append=False):
        """Set the rich target content."""
        self._rich_target = None
        segment = self._get_or_create_segment()
        
        if value is None:
            languageNode = self.createlanguageNode(lang, "", "target")
            # Insert target after source
            source_node = self._get_source_from_segment(segment)
            if source_node is not None:
                source_index = list(segment).index(source_node)
                segment.insert(source_index + 1, languageNode)
            else:
                segment.append(languageNode)
            return

        self._ensure_xml_space_preserve()
        languageNode = self._get_target_from_segment(segment)
        if languageNode is None:
            languageNode = self.createlanguageNode(lang, "", "target")
            # Insert target after source
            source_node = self._get_source_from_segment(segment)
            if source_node is not None:
                source_index = list(segment).index(source_node)
                segment.insert(source_index + 1, languageNode)
            else:
                segment.append(languageNode)

        clear_content(languageNode)
        strelem_to_xml(languageNode, value[0])

    def get_rich_target(self, lang=None):
        """Retrieves the target text."""
        if self._rich_target is None:
            segment = self._get_segment()
            if segment is None:
                self._rich_target = [xml_to_strelem("", getXMLspace(self.xmlelement, self._default_xml_space))]
            else:
                target_node = self._get_target_from_segment(segment)
                if target_node is None:
                    self._rich_target = [xml_to_strelem("", getXMLspace(self.xmlelement, self._default_xml_space))]
                else:
                    self._rich_target = [
                        xml_to_strelem(
                            target_node,
                            getXMLspace(self.xmlelement, self._default_xml_space),
                        )
                    ]
        return self._rich_target

    @property
    def rich_target(self):
        return self.get_rich_target()

    @rich_target.setter
    def rich_target(self, value):
        self.set_rich_target(value)

    def _get_segment(self):
        """Get the segment element."""
        try:
            return next(self.xmlelement.iterchildren(self.namespaced("segment")))
        except StopIteration:
            return None

    def _get_or_create_segment(self):
        """Get or create the segment element."""
        segment = self._get_segment()
        if segment is None:
            segment = etree.SubElement(self.xmlelement, self.namespaced("segment"))
        return segment

    def _get_source_from_segment(self, segment):
        """Get source element from segment."""
        try:
            return next(segment.iterchildren(self.namespaced("source")))
        except StopIteration:
            return None

    def _get_target_from_segment(self, segment):
        """Get target element from segment."""
        try:
            return next(segment.iterchildren(self.namespaced("target")))
        except StopIteration:
            return None

    def _ensure_xml_space_preserve(self):
        """Ensure xml:space='preserve' is set on the unit."""
        if getXMLspace(self.xmlelement) != "preserve":
            setXMLspace(self.xmlelement, "preserve")

    def addnote(self, text, origin=None, position="append"):
        """Add a note specifically in the XLIFF 2.0 way."""
        if not text:
            return
        # In XLIFF 2.0, notes are added at the unit level in a notes container
        notes_container = self.xmlelement.find(self.namespaced("notes"))
        if notes_container is None:
            notes_container = etree.SubElement(self.xmlelement, self.namespaced("notes"))
        
        note_elem = etree.SubElement(notes_container, self.namespaced("note"))
        note_elem.text = text
        if origin:
            note_elem.set("category", origin)

    def getnotes(self, origin=None):
        """Get notes from the unit."""
        notes_text = []
        notes_container = self.xmlelement.find(self.namespaced("notes"))
        if notes_container is not None:
            for note in notes_container.iterchildren(self.namespaced("note")):
                if origin is None or note.get("category") == origin:
                    if note.text:
                        notes_text.append(note.text)
        return "\n".join(notes_text)

    def removenotes(self, origin=None):
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
                if len(list(notes_container.iterchildren(self.namespaced("note")))) == 0:
                    self.xmlelement.remove(notes_container)

    def getid(self):
        """Get the unit id."""
        return self.xmlelement.get("id")

    def setid(self, value):
        """Set the unit id."""
        if value:
            self.xmlelement.set("id", value)

    @classmethod
    def multistring_to_rich(cls, mstr):
        """Convert multistring to rich format."""
        strings = mstr
        if isinstance(mstr, multistring):
            strings = mstr.strings
        elif isinstance(mstr, str):
            strings = [mstr]
        return [xml_to_strelem(s) for s in strings]

    @classmethod
    def rich_to_multistring(cls, elem_list):
        """Convert rich format to multistring."""
        return multistring([str(elem) for elem in elem_list])

    def merge(self, otherunit, overwrite=False, comments=True, authoritative=False):
        """Merge another unit into this one."""
        super().merge(otherunit, overwrite, comments)
        if self.target and hasattr(otherunit, 'source'):
            # Set state to translated
            segment = self._get_segment()
            if segment is not None:
                segment.set("state", "translated")


class xliff2file(lisa.LISAfile):
    """Class representing an XLIFF 2.0 file store."""

    UnitClass = xliff2unit
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

    def __init__(self, *args, **kwargs):
        self._filename = None
        super().__init__(*args, **kwargs)

    def initbody(self):
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

    def addheader(self):
        """Initialise the file header."""

    def createfilenode(
        self, filename, sourcelanguage=None, targetlanguage=None, datatype="plaintext"
    ):
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

    def getfilenames(self):
        """Returns all file ids in this XLIFF 2.0 file."""
        filenodes = self.document.getroot().iterchildren(self.namespaced("file"))
        filenames = [self.getfilename(filenode) for filenode in filenodes]
        return list(filter(None, filenames))

    def getfilenode(self, filename, createifmissing=False):
        """Finds the file node with the given id."""
        filenodes = self.document.getroot().iterchildren(self.namespaced("file"))
        for filenode in filenodes:
            if self.getfilename(filenode) == filename:
                return filenode
        if not createifmissing:
            return None
        return self.createfilenode(filename)

    def addunit(self, unit, new=True):
        """Adds the given unit to the file."""
        if new:
            unit.setid(self._getuniqueid())
        super().addunit(unit, new=new)

    def _getuniqueid(self):
        """Return a unique numeric id for a unit."""
        max_id = 0
        for unit in self.units:
            try:
                unit_id = unit.getid()
                if unit_id and unit_id.isdigit():
                    max_id = max(max_id, int(unit_id))
            except (ValueError, AttributeError):
                continue
        return str(max_id + 1)

    def getsourcelanguage(self):
        """Get the source language for this file."""
        return self.document.getroot().get("srcLang", "en")

    def setsourcelanguage(self, lang):
        """Set the source language for this file."""
        self.document.getroot().set("srcLang", lang)

    def gettargetlanguage(self):
        """Get the target language for this file."""
        return self.document.getroot().get("trgLang")

    def settargetlanguage(self, lang):
        """Set the target language for this file."""
        if lang:
            self.document.getroot().set("trgLang", lang)
