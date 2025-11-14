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

"""Common functionality shared between XLIFF 1.x and XLIFF 2.0 implementations."""

from typing import Any

from lxml import etree

from translate.misc.multistring import multistring
from translate.misc.xml_helpers import (
    clear_content,
    getXMLspace,
    safely_set_text,
    setXMLspace,
)
from translate.storage import lisa
from translate.storage.placeables.lisa import strelem_to_xml, xml_to_strelem


class XliffFile(lisa.LISAfile):
    """Base class providing common functionality for XLIFF file stores."""

    def __init__(self, *args, **kwargs):
        """Initialize XLIFF file with filename tracking."""
        self._filename = None
        super().__init__(*args, **kwargs)

    @staticmethod
    def getfilename(filenode):
        """
        Returns the identifier of the given file node.

        Must be overridden by subclasses to specify which attribute to use.
        """
        raise NotImplementedError("Subclasses must implement getfilename()")

    @staticmethod
    def setfilename(filenode, filename):
        """
        Set the identifier of the given file node.

        Must be overridden by subclasses to specify which attribute to use.
        """
        raise NotImplementedError("Subclasses must implement setfilename()")

    def getfilenames(self):
        """Returns all file identifiers in this XLIFF file."""
        filenodes = self.document.getroot().iterchildren(self.namespaced("file"))
        filenames = [self.getfilename(filenode) for filenode in filenodes]
        return list(filter(None, filenames))

    def getfilenode(self, filename, createifmissing=False):
        """Finds the file node with the given identifier."""
        filenodes = self.document.getroot().iterchildren(self.namespaced("file"))
        for filenode in filenodes:
            if self.getfilename(filenode) == filename:
                return filenode
        if not createifmissing:
            return None
        return self.createfilenode(filename)


class XliffUnit(lisa.LISAunit):
    """Base class providing common functionality for XLIFF units."""

    def _ensure_xml_space_preserve(self) -> None:
        """Ensure xml:space='preserve' is set on the unit."""
        if getXMLspace(self.xmlelement) != "preserve":
            setXMLspace(self.xmlelement, "preserve")

    def createlanguageNode(self, lang: str, text: str, purpose: str) -> etree._Element:
        """
        Create and return an xml Element setup with given parameters.

        This is a common implementation that works for both XLIFF 1.x and 2.0.
        """
        assert purpose
        langset = etree.Element(self.namespaced(purpose))
        safely_set_text(langset, text)
        return langset

    @classmethod
    def multistring_to_rich(cls, mstr: Any) -> list[Any]:
        """
        Convert a multistring to rich format.

        Override :meth:`TranslationUnit.multistring_to_rich` which is used
        by the ``rich_source`` and ``rich_target`` properties.
        """
        strings = mstr
        if isinstance(mstr, multistring):
            strings = mstr.strings
        elif isinstance(mstr, str):
            strings = [mstr]
        return [xml_to_strelem(s) for s in strings]

    @classmethod
    def rich_to_multistring(cls, elem_list: list[Any]) -> multistring:
        """
        Convert rich format to multistring.

        Override :meth:`TranslationUnit.rich_to_multistring` which is used
        by the ``rich_source`` and ``rich_target`` properties.
        """
        return multistring([str(elem) for elem in elem_list])

    def getlanguageNodes(self):
        """We override this to get source and target nodes."""
        source = None
        target = None
        nodes = []
        try:
            source = next(
                self.xmlelement.iterchildren(self.namespaced(self.languageNode))
            )
            target = next(self.xmlelement.iterchildren(self.namespaced("target")))
            nodes = [source, target]
        except StopIteration:
            if source is not None:
                nodes.append(source)
            if target is not None:
                nodes.append(target)
        return nodes

    def set_rich_source(self, value, sourcelang="en"):
        sourcelanguageNode = self.get_source_dom()
        if sourcelanguageNode is None:
            sourcelanguageNode = self.createlanguageNode(sourcelang, "", "source")
            self.set_source_dom(sourcelanguageNode)

        # Clear sourcelanguageNode first
        clear_content(sourcelanguageNode)

        strelem_to_xml(sourcelanguageNode, value[0])

    @property
    def rich_source(self):
        # rsrc = xml_to_strelem(self.source_dom)
        # logger.debug('rich source: %s' % (repr(rsrc)))
        # from dubulib.debug.misc import print_stack_funcs
        # print_stack_funcs()
        return [
            xml_to_strelem(
                self.source_dom, getXMLspace(self.xmlelement, self._default_xml_space)
            )
        ]

    @rich_source.setter
    def rich_source(self, value):
        self.set_rich_source(value)

    def set_rich_target(self, value, lang="xx", append=False):
        self._rich_target = None
        if value is None:
            self.set_target_dom(self.createlanguageNode(lang, "", "target"))
            return

        self._ensure_xml_space_preserve()
        languageNode = self.get_target_dom()
        if languageNode is None:
            languageNode = self.createlanguageNode(lang, "", "target")
            self.set_target_dom(languageNode, append)

        # Clear languageNode first
        clear_content(languageNode)

        strelem_to_xml(languageNode, value[0])
        ### currently giving some issues in Virtaal: self._rich_target = value

    def get_rich_target(self, lang=None):
        """
        Retrieves the "target" text (second entry), or the entry in the
        specified language, if it exists.
        """
        if self._rich_target is None:
            self._rich_target = [
                xml_to_strelem(
                    self.get_target_dom(lang),
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

    def merge(self, otherunit, overwrite=False, comments=True, authoritative=False):
        # TODO: consider other attributes like "approved"
        super().merge(otherunit, overwrite, comments)
        if self.target:
            self.marktranslated()
            if otherunit.isfuzzy():
                self.markfuzzy()
            elif otherunit.source == self.source:
                self.markfuzzy(False)
            elif otherunit.source != self.source:
                self.markfuzzy(True)
        if comments:
            self.addnote(otherunit.getnotes())
