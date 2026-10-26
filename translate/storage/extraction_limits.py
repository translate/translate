#
# Copyright 2026 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""Optional resource budgets for extracting translation units from XML."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from lxml import etree

from translate.storage.base import ParseError


@dataclass
class ExtractionBudget:
    """Share limits across all XML members of one document archive."""

    max_xml_bytes: int | None = None
    max_elements: int | None = None
    max_units: int | None = None
    xml_bytes: int = 0
    elements: int = 0
    units: int = 0

    def check_xml_bytes(self, size: int) -> None:
        if self.max_xml_bytes is not None and size > self.max_xml_bytes:
            raise ParseError(
                f"XML data exceeds the {self.max_xml_bytes} byte extraction limit"
            )

    def add_xml_bytes(self, size: int) -> None:
        self.check_xml_bytes(self.xml_bytes + size)
        self.xml_bytes += size

    def count_elements(self, data: bytes) -> None:
        """Count elements without retaining a second XML tree in memory."""
        if self.max_elements is None:
            return
        for event, element in etree.iterparse(
            BytesIO(data),
            events=("start", "end"),
            resolve_entities=False,
            no_network=True,
            collect_ids=False,
        ):
            if event == "start":
                self.elements += 1
                if self.elements > self.max_elements:
                    raise ParseError(
                        f"XML data exceeds the {self.max_elements} element extraction limit"
                    )
            else:
                element.clear()
                parent = element.getparent()
                if parent is not None:
                    while element.getprevious() is not None:
                        del parent[0]

    def count_unit(self) -> None:
        if self.max_units is None:
            return
        self.units += 1
        if self.units > self.max_units:
            raise ParseError(
                f"Document exceeds the {self.max_units} unit extraction limit"
            )
