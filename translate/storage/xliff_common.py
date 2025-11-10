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

from translate.misc.multistring import multistring
from translate.misc.xml_helpers import getXMLspace, setXMLspace
from translate.storage import lisa
from translate.storage.placeables.lisa import xml_to_strelem


class XliffUnit(lisa.LISAunit):
    """Base class providing common functionality for XLIFF units."""

    def _ensure_xml_space_preserve(self):
        """Ensure xml:space='preserve' is set on the unit."""
        if getXMLspace(self.xmlelement) != "preserve":
            setXMLspace(self.xmlelement, "preserve")

    @classmethod
    def multistring_to_rich(cls, mstr):
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
    def rich_to_multistring(cls, elem_list):
        """
        Convert rich format to multistring.

        Override :meth:`TranslationUnit.rich_to_multistring` which is used
        by the ``rich_source`` and ``rich_target`` properties.
        """
        return multistring([str(elem) for elem in elem_list])
