#
# Copyright 2005-2009 Zuza Software Foundation
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

"""module for parsing TMX translation memory files."""

from io import BytesIO

from lxml import etree

from translate import __version__
from translate.misc.xml_helpers import (
    getXMLlang,
    getXMLspace,
    safely_set_text,
    setXMLlang,
)
from translate.storage import lisa


class tmxunit(lisa.MultilingualLISAunit):
    """A single unit in the TMX file."""

    rootNode = "tu"
    languageNode = "tuv"
    textNode = "seg"

    def _get_source_language(self) -> str | None:
        store = getattr(self, "_store", None)
        if store is not None and getattr(store, "_source_language_explicit", False):
            language = super()._get_source_language()
        else:
            language = self.xmlelement.get("srclang")
            if language is None:
                language = super()._get_source_language()
        if lisa.normalize_language(language) == "*all*":
            return None
        return language

    def createlanguageNode(self, lang, text, purpose):  # ty:ignore[invalid-method-override]
        """Returns a langset xml Element setup with given parameters."""
        langset = etree.Element(self.languageNode)
        setXMLlang(langset, lang)
        seg = etree.SubElement(langset, self.textNode)
        # implied by the standard:
        # setXMLspace(seg, "preserve")
        safely_set_text(seg, text)

        return langset

    def _insert_element_before(self, element: etree._Element, tag: str) -> None:
        """
        Insert an element before the first occurrence of the specified tag.

        According to TMX DTD, elements must follow this order: note, prop, tuv.
        This helper method finds the first child matching the tag name
        and inserts the element before it, or appends at the end if none found.

        :param element: The element to insert
        :param tag: Tag name to search for
        """
        needle = self.xmlelement.find(tag)
        if needle is None:
            self.xmlelement.append(element)
        else:
            self.xmlelement.insert(self.xmlelement.index(needle), element)

    def getid(self):
        """
        Returns the identifier for this unit. The optional tuid property is
        used if available, otherwise we inherit .getid(). Note that the tuid
        property is only mandated to be unique from TMX 2.0.
        """
        id = self.xmlelement.get("tuid", "")
        return id or super().getid()

    def istranslatable(self):
        return bool(self.source)

    def addnote(self, text, origin=None, position="append") -> None:
        """
        Add a note specifically in a "note" tag.

        The origin parameter is ignored
        """
        note = etree.Element(self.namespaced("note"))
        safely_set_text(note, text.strip())

        # According to TMX DTD, notes should come before prop and tuv elements
        # Try to insert before prop first, if not found try tuv
        if self.xmlelement.find(self.namespaced("prop")) is not None:
            self._insert_element_before(note, self.namespaced("prop"))
        else:
            self._insert_element_before(note, self.namespaced(self.languageNode))

    def _getnotelist(self, origin: str | None = None) -> list[str]:
        """
        Returns the text from notes.

        :param origin: Ignored
        :return: The text from notes
        """
        note_nodes = self.xmlelement.iterdescendants(self.namespaced("note"))
        return [lisa.getText(note) for note in note_nodes]

    def getnotes(self, origin=None):
        return "\n".join(self._getnotelist(origin=origin))

    def removenotes(self, origin=None) -> None:
        """Remove all the translator notes."""
        notes = self.xmlelement.iterdescendants(self.namespaced("note"))
        for note in notes:
            self.xmlelement.remove(note)

    def adderror(self, errorname, errortext) -> None:
        """Adds an error message to this unit."""
        # TODO: consider factoring out: some duplication between XLIFF and TMX
        text = errorname
        if errortext:
            text += f": {errortext}"
        self.addnote(text, origin="pofilter")

    def geterrors(self):
        """Get all error messages."""
        # TODO: consider factoring out: some duplication between XLIFF and TMX
        notelist = self._getnotelist(origin="pofilter")
        errordict = {}
        for note in notelist:
            errorname, errortext = note.split(": ")
            errordict[errorname] = errortext
        return errordict

    def setcontext(self, context) -> None:
        context_prop = self.xmlelement.find(
            f"{self.namespaced('prop')}[@type='x-context']"
        )
        if context_prop is None:
            context_prop = etree.Element(self.namespaced("prop"))
            context_prop.set("type", "x-context")

            # According to TMX DTD, prop elements come after notes but before tuv elements
            self._insert_element_before(
                context_prop, self.namespaced(self.languageNode)
            )
        safely_set_text(context_prop, context)

    def getcontext(self):
        context_prop = self.xmlelement.find(
            f"{self.namespaced('prop')}[@type='x-context']"
        )
        if context_prop is not None and context_prop.text is not None:
            return context_prop.text
        return ""


class tmxfile(lisa.LISAfile[tmxunit]):
    """Class representing a TMX file store."""

    UnitClass = tmxunit
    Name = "TMX Translation Memory"
    Mimetypes = ["application/x-tmx"]
    Extensions = ["tmx"]
    rootNode = "tmx"
    bodyNode = "body"
    XMLskeleton = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
<header></header>
<body></body>
</tmx>"""

    def __init__(
        self, inputfile=None, sourcelanguage=None, targetlanguage=None, **kwargs
    ) -> None:
        source_language_explicit = sourcelanguage is not None
        self._source_language_explicit = source_language_explicit
        if inputfile is None and sourcelanguage is None:
            sourcelanguage = "en"
        super().__init__(
            inputfile,
            sourcelanguage=sourcelanguage,
            targetlanguage=targetlanguage,
            **kwargs,
        )
        self._source_language_explicit = source_language_explicit
        if inputfile is not None:
            if self._source_language_explicit:
                assert sourcelanguage is not None
                self.setsourcelanguage(sourcelanguage)
            else:
                header = self.document.getroot().find(self.namespaced("header"))
                self.sourcelanguage = (
                    header.get("srclang") if header is not None else None
                )
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

    def _invalidate_indexes(self) -> None:
        self.locationindex = {}
        self.sourceindex = {}
        self.id_index = {}
        self.languageindex = {}

    def setsourcelanguage(self, sourcelanguage: str) -> None:
        self._source_language_explicit = True
        super().setsourcelanguage(sourcelanguage)
        self._invalidate_indexes()

    def settargetlanguage(self, targetlanguage: str | None) -> None:
        super().settargetlanguage(targetlanguage)
        self._invalidate_indexes()

    def makeindex(self) -> None:
        super().makeindex()
        self.languageindex: dict[tuple[str, str], list[tmxunit]] = {}
        for unit in self.units:
            xml_space = getXMLspace(unit.xmlelement, unit._default_xml_space)
            for language_node in unit.getlanguageNodes():
                language = lisa.normalize_language(getXMLlang(language_node))
                text = unit.getNodeText(language_node, xml_space)
                if language is not None and text is not None:
                    self.languageindex.setdefault((language, text), []).append(unit)

    def addsourceunit(self, source, sourcelang=None):
        unit = self.UnitClass(None)
        unit._store = self
        if sourcelang is not None:
            unit.xmlelement.set("srclang", sourcelang)
        unit.setsource(source, sourcelang)
        self.addunit(unit)
        return unit

    def addheader(self) -> None:
        headernode = next(
            self.document.getroot().iterchildren(self.namespaced("header"))
        )
        headernode.set("creationtool", "Translate Toolkit")
        headernode.set("creationtoolversion", __version__.sver)
        headernode.set("segtype", "sentence")
        headernode.set("o-tmf", "UTF-8")
        headernode.set("adminlang", "en")
        # TODO: consider adminlang. Used for notes, etc. Possibly same as
        # targetlanguage
        headernode.set("srclang", self.sourcelanguage or "en")
        headernode.set("datatype", "PlainText")
        # headernode.set("creationdate", "YYYYMMDDTHHMMSSZ"
        # headernode.set("creationid", "CodeSyntax"

    def addtranslation(
        self, source, srclang, translation, translang, comment=None, context=None
    ) -> None:
        """Addtranslation method for testing old unit tests."""
        unit = self.addsourceunit(source, srclang)
        unit.settarget(translation, translang, append=True)
        if comment is not None and len(comment) > 0:
            unit.addnote(comment)
        if context is not None and len(context) > 0:
            unit.setcontext(context)

    def translate(self, sourcetext, sourcelang=None, targetlang=None):  # ty:ignore[invalid-method-override]
        """Return the requested translation for a source string."""
        source_language = lisa.normalize_language(sourcelang)
        if source_language is None:
            unit = self.findunit(sourcetext)
        else:
            self.require_index()
            units = self.languageindex.get((source_language, sourcetext))
            unit = units[0] if units else None
        if unit is None:
            return None
        if targetlang:
            return unit.gettarget(targetlang)
        if source_language is not None and self.targetlanguage is None:
            source_node = unit._get_language_node(source_language)
            target_node = unit._get_fallback_target_node(
                unit.getlanguageNodes(), source_node
            )
            return unit.getNodeText(
                target_node, getXMLspace(unit.xmlelement, unit._default_xml_space)
            )
        return unit.target
