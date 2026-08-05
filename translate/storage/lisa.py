#
# Copyright 2006-2011 Zuza Software Foundation
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

"""Parent class for LISA standards (TMX, TBX, XLIFF)."""

from __future__ import annotations

import contextlib
import copy
from typing import TypeVar

from lxml import etree

from translate.misc.xml_helpers import (
    expand_closing_tags,
    getText,
    getXMLlang,
    getXMLspace,
    namespaced,
    parse_xml,
    reindent,
)
from translate.storage import base


class LISAunit(base.TranslationUnit):
    """
    A single unit in the file.  Provisional work is done to make several
    languages possible.
    """

    # The name of the root element of this unit type:(termEntry, tu, trans-unit)
    rootNode = ""
    # The name of the per language element of this unit type:(termEntry, tu,
    # trans-unit)
    languageNode = ""
    # The name of the innermost element of this unit type:(term, seg)
    textNode = ""

    namespace = None
    _default_xml_space = "preserve"
    """The default handling of spacing in the absence of an xml:space
    attribute.

    This is mostly for correcting XLIFF behaviour."""

    def __init__(self, source, empty=False, **kwargs) -> None:
        """Constructs a unit containing the given source string."""
        self._rich_source = None
        self._rich_target = None
        if empty:
            self._state_n = 0
            return
        self.xmlelement = etree.Element(self.namespaced(self.rootNode))
        # add descrip, note, etc.
        super().__init__(source)

    def __eq__(self, other):
        """Compares two units."""
        if not isinstance(other, LISAunit):
            return super().__eq__(other)
        languageNodes = self.getlanguageNodes()
        otherlanguageNodes = other.getlanguageNodes()
        if len(languageNodes) != len(otherlanguageNodes):
            return False
        for i, language_node in enumerate(languageNodes):
            mytext = self.getNodeText(
                language_node, getXMLspace(self.xmlelement, self._default_xml_space)
            )
            othertext = other.getNodeText(
                otherlanguageNodes[i],
                getXMLspace(self.xmlelement, self._default_xml_space),
            )
            if mytext != othertext:
                # TODO:^ maybe we want to take children and notes into account
                return False
        return True

    def copy(self) -> LISAunit:
        """
        Make a copy of the translation unit.

        Copy the XML subtree directly instead of serializing and reparsing it.
        """
        new_unit = self.__class__(None, empty=True)
        new_unit.xmlelement = copy.deepcopy(self.xmlelement)
        return new_unit

    def namespaced(self, name):
        """
        Returns name in Clark notation.

        For example ``namespaced("source")`` in an XLIFF document
        might return::

            {urn:oasis:names:tc:xliff:document:1.1}source

        This is needed throughout lxml.
        """
        return namespaced(self.namespace, name)

    def set_source_dom(self, dom_node) -> None:
        languageNodes = self.getlanguageNodes()
        if len(languageNodes) > 0:
            self.xmlelement.replace(languageNodes[0], dom_node)
        else:
            self.xmlelement.append(dom_node)

    def get_source_dom(self):
        return self.getlanguageNode(lang=None, index=0)

    source_dom = property(get_source_dom, set_source_dom)

    @property
    def source(self):
        return self.getNodeText(
            self.source_dom, getXMLspace(self.xmlelement, self._default_xml_space)
        )

    @source.setter
    def source(self, source) -> None:
        self.setsource(source, sourcelang="en")

    def setsource(self, text, sourcelang="en") -> None:
        self._rich_source = None
        self.source_dom = self.createlanguageNode(sourcelang, text, "source")

    def set_target_dom(self, dom_node, append=False) -> None:
        languageNodes = self.getlanguageNodes()
        if dom_node is not None:
            if append or len(languageNodes) == 0:
                self.xmlelement.append(dom_node)
            else:
                self.xmlelement.insert(1, dom_node)
        if not append and len(languageNodes) > 1:
            self.xmlelement.remove(languageNodes[1])

    def get_target_dom(self, lang=None):
        if lang:
            return self.getlanguageNode(lang=lang)
        return self.getlanguageNode(lang=None, index=1)

    target_dom = property(get_target_dom)

    def gettarget(self, lang=None):
        """
        Retrieves the "target" text (second entry), or the entry in the
        specified language, if it exists.
        """
        return self.getNodeText(
            self.get_target_dom(lang),
            getXMLspace(self.xmlelement, self._default_xml_space),
        )

    def settarget(self, target, lang="xx", append=False) -> None:
        """
        Sets the "target" string (second language), or alternatively appends
        to the list.
        """
        # XXX: we really need the language - can't really be optional, and we
        # need to propagate it
        if self._rich_target is not None:
            self._rich_target = None
        # Firstly deal with reinitialising to None or setting to identical
        # string
        if self.target == target:
            return
        languageNode = self.target_dom
        if target is not None:
            if languageNode is None:
                languageNode = self.createlanguageNode(lang, target, "target")
                self.set_target_dom(languageNode, append)
            else:
                if self.textNode:
                    terms = languageNode.iter(self.namespaced(self.textNode))
                    with contextlib.suppress(StopIteration):
                        languageNode = next(terms)
                languageNode.text = target
        else:
            self.set_target_dom(None, False)

    @property
    def target(self):
        return self.gettarget()

    @target.setter
    def target(self, target) -> None:
        self.settarget(target)

    @staticmethod
    def createlanguageNode(lang, text, purpose=None) -> None:
        """
        Returns a xml Element setup with given parameters to represent a
        single language entry. Has to be overridden.
        """
        return

    def getlanguageNodes(self):
        """Returns a list of all nodes that contain per language information."""
        return list(self.xmlelement.iterchildren(self.namespaced(self.languageNode)))

    def getlanguageNode(self, lang=None, index=None):
        """Retrieves a :attr:`languageNode` either by language or by index."""
        if lang is None and index is None:
            raise KeyError("No criteria for languageNode given")
        languageNodes = self.getlanguageNodes()
        if lang:
            for set in languageNodes:
                if getXMLlang(set) == lang:
                    return set
        else:  # have to use index
            if index >= len(languageNodes):  # ty:ignore[unsupported-operator]
                return None
            return languageNodes[index]
        return None

    def getNodeText(self, languageNode, xml_space="preserve"):
        """Retrieves the term from the given :attr:`languageNode`."""
        if languageNode is None:
            return None
        if self.textNode:
            terms = languageNode.iterdescendants(self.namespaced(self.textNode))
            if terms is None:
                return None
            node = next(terms, None)
            if node is not None:
                return getText(node, xml_space)
            # didn't have the structure we expected
            return None
        return getText(languageNode, xml_space)

    def __str__(self) -> str:
        # 'unicode' encoding keeps the unicode status of the output
        return etree.tostring(self.xmlelement, pretty_print=True, encoding="unicode")

    def _set_property(self, name, value) -> None:
        self.xmlelement.attrib[name] = value

    xid = property(
        lambda self: self.xmlelement.attrib[self.namespaced("xid")],
        lambda self, value: self._set_property(self.namespaced("xid"), value),
    )

    rid = property(
        lambda self: self.xmlelement.attrib[self.namespaced("rid")],
        lambda self, value: self._set_property(self.namespaced("rid"), value),
    )

    @classmethod
    def createfromxmlElement(cls, element):
        term = cls(None, empty=True)
        term.xmlelement = element
        return term


def normalize_language(language: str | None) -> str | None:
    """Normalize an XML language tag for comparison."""
    if not language:
        return None
    return language.replace("_", "-").lower()


class MultilingualLISAunit(LISAunit):
    """A LISA unit with sibling nodes representing different languages."""

    def _store_language(self, name: str) -> str | None:
        store = getattr(self, "_store", None)
        if store is None:
            return None
        return getattr(store, name, None)

    def _store_language_or_default(self, name: str, default: str) -> str:
        return self._store_language(name) or default

    def _get_source_language(self) -> str | None:
        return self._store_language("sourcelanguage")

    def _get_target_language(self) -> str | None:
        return self._store_language("targetlanguage")

    def _get_language_node(self, language: str | None):
        language = normalize_language(language)
        if language is None:
            return None
        for node in self.getlanguageNodes():
            if normalize_language(getXMLlang(node)) == language:
                return node
        return None

    def _get_source_language_node(self):
        return self._get_language_node(self._get_source_language())

    def _get_target_language_node(self):
        return self._get_language_node(self._get_target_language())

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
        source_language = self._get_source_language()
        if normalize_language(source_language) is not None:
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

    def _invalidate_store_indexes(self) -> None:
        store = getattr(self, "_store", None)
        if store is not None:
            if hasattr(store, "_invalidate_indexes"):
                store._invalidate_indexes()
            else:
                store.locationindex = {}
                store.sourceindex = {}
                store.id_index = {}

    def setsource(self, text, sourcelang=None) -> None:
        super().setsource(text, sourcelang or self._get_source_language() or "en")
        self._invalidate_store_indexes()

    def set_target_dom(self, dom_node, append=False) -> None:
        language_nodes = self.getlanguageNodes()
        target_node = (
            self._get_language_node(getXMLlang(dom_node))
            if dom_node is not None
            else self.get_target_dom()
        )
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
            insert_index = self.xmlelement.index(language_nodes[0])
            if source_node is not None:
                insert_index = self.xmlelement.index(source_node) + 1
            else:
                insert_index += 1
            self.xmlelement.insert(insert_index, dom_node)

    def get_target_dom(self, lang=None):
        if lang:
            return self._get_language_node(lang)

        target_language = self._get_target_language()
        if normalize_language(target_language) is not None:
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
        if self._rich_target is not None:
            self._rich_target = None
        target_language = lang or self._store_language_or_default(
            "targetlanguage", "xx"
        )
        language_node = (
            self._get_language_node(target_language)
            if lang is not None
            else self.target_dom
        )
        if target is not None:
            if language_node is None:
                language_node = self.createlanguageNode(
                    target_language, target, "target"
                )
                self.set_target_dom(language_node, append)
            else:
                if self.textNode:
                    terms = language_node.iter(self.namespaced(self.textNode))
                    with contextlib.suppress(StopIteration):
                        language_node = next(terms)
                language_node.text = target
        elif language_node is not None:
            self.xmlelement.remove(language_node)
        self._invalidate_store_indexes()


U = TypeVar("U", bound=LISAunit)


class LISAfile(base.TranslationStore[U]):
    """A class representing a file store for one of the LISA file formats."""

    UnitClass = LISAunit
    # The root node of the XML document:
    rootNode = ""
    # The root node of the content section:
    bodyNode = ""
    # The XML skeleton to use for empty construction:
    XMLskeleton = ""
    XMLindent = {}
    XMLdoublequotes = True
    XMLdoctype = None
    XMLuppercaseEncoding = True
    # Determine how empty tags should be serialized (<note></note> or <note />)
    XMLSelfClosingTags = True

    namespace = None

    def __init__(
        self, inputfile=None, sourcelanguage="en", targetlanguage=None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        if inputfile is not None:
            self.parse(inputfile)
            assert self.document.getroot().tag == self.namespaced(self.rootNode)
        else:
            # We strip out newlines to ensure that spaces in the skeleton
            # doesn't interfere with the the pretty printing of lxml
            self.parse(self.XMLskeleton.replace("\n", "").encode("utf-8"))
            self.setsourcelanguage(sourcelanguage)
            self.settargetlanguage(targetlanguage)
            self.addheader()

    def addheader(self) -> None:
        """Method to be overridden to initialise headers, etc."""

    def namespaced(self, name):
        """
        Returns name in Clark notation.

        For example ``namespaced("source")`` in an XLIFF document
        might return::

            {urn:oasis:names:tc:xliff:document:1.1}source

        This is needed throughout lxml.
        """
        return namespaced(self.namespace, name)

    def initbody(self) -> None:
        """
        Initialises self.body so it never needs to be retrieved from the XML
        again.
        """
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.find(f".//{self.namespaced(self.bodyNode)}")

    def addsourceunit(self, source):
        """Adds and returns a new unit with the given string as first entry."""
        newunit = self.UnitClass(source)
        self.addunit(newunit)
        return newunit

    def addunit(self, unit, new=True) -> None:
        old_ns = (
            etree.QName(unit.xmlelement).namespace
            if hasattr(unit, "xmlelement") and unit.xmlelement is not None
            else None
        )
        unit.namespace = self.namespace
        if old_ns and old_ns != self.namespace and unit.xmlelement is not None:
            # Remap XML element namespaces so they match the store's namespace.
            # This is needed when a freshly-created unit (using the class default
            # namespace) is added to a store with a different namespace, ensuring
            # round-trip serialization works correctly.
            for node in unit.xmlelement.iter():
                if isinstance(node.tag, str):
                    qname = etree.QName(node)
                    if qname.namespace == old_ns:
                        node.tag = namespaced(self.namespace, qname.localname)
        super().addunit(unit)
        if new:
            self.body.append(unit.xmlelement)  # ty:ignore[unresolved-attribute]

    def removeunit(self, unit) -> None:
        super().removeunit(unit)
        unit.xmlelement.getparent().remove(unit.xmlelement)

    def serialize_hook(self, treestring: str) -> bytes:
        return treestring.encode(self.encoding)

    def serialize(self, out) -> None:
        """Converts to a string containing the file's XML."""
        root = self.document.getroot()
        xml_quote_format = '"' if self.XMLdoublequotes else "'"
        xml_encoding = (
            self.encoding.upper()
            if self.XMLuppercaseEncoding
            else self.encoding.lower()
        )

        xml_declaration = f"<?xml version={xml_quote_format}1.0{xml_quote_format} encoding={xml_quote_format}{xml_encoding}{xml_quote_format}?>\n"

        out.write(self.serialize_hook(xml_declaration))

        if self.XMLindent:
            reindent(root, **self.XMLindent)

        if not self.XMLSelfClosingTags:
            expand_closing_tags(root)

        treestring = etree.tostring(
            self.document,
            pretty_print=not self.XMLindent,
            xml_declaration=False,
            encoding="unicode",
            doctype=self.XMLdoctype,
        )

        out.write(self.serialize_hook(treestring))  # ty:ignore[invalid-argument-type]

    def parse(self, xml) -> None:  # ty:ignore[invalid-method-override]
        """Populates this object from the given xml string."""
        if not hasattr(self, "filename"):
            self.filename = getattr(xml, "name", "")
        if hasattr(xml, "read"):
            xml.seek(0)
            posrc = xml.read()
            xml = posrc
        self.document = parse_xml(xml, strip_cdata=False).getroottree()
        self.encoding = self.document.docinfo.encoding
        self.initbody()
        assert self.document.getroot().tag == self.namespaced(self.rootNode)
        for entry in self.document.getroot().iterdescendants(
            self.namespaced(self.UnitClass.rootNode)
        ):
            term = self.UnitClass.createfromxmlElement(entry)
            self.addunit(term, new=False)
