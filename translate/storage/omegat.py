#
# Copyright 2009 Zuza Software Foundation
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
Manage the OmegaT glossary format.

OmegaT glossary format is used by the
`OmegaT <http://www.omegat.org/en/omegat.html>`_ computer aided
translation tool.

It is a bilingual base class derived format with :class:`OmegaTFile`
and :class:`OmegaTUnit` providing file and unit level access.

Format Implementation
    The OmegaT glossary format is a simple Tab Separated Value (TSV) file
    with the columns: source, target, comment.

    The dialect of the TSV files is specified by :class:`OmegaTDialect`.

Encoding
    The files are either UTF-8 or encoded using the system default.  UTF-8
    encoded files use the .utf8 extension while system encoded files use
    the .tab extension.
"""

import csv
import locale
from io import StringIO

from translate.storage import base

OMEGAT_FIELDNAMES = ["source", "target", "comment"]
"""Field names for an OmegaT glossary unit"""


class OmegaTDialect(csv.Dialect):
    """
    Describe the properties of an OmegaT generated TAB-delimited glossary
    file.
    """

    delimiter = "\t"
    lineterminator = "\r\n"
    quoting = csv.QUOTE_NONE


csv.register_dialect("omegat", OmegaTDialect)


class OmegaTUnit(base.MetadataTranslationUnit):
    """An OmegaT glossary unit."""

    def _get_field(self, key):
        if key not in self._metadata_dict:
            return None
        if self._metadata_dict[key]:
            return self._metadata_dict[key]
        return ""

    def _set_field(self, key, newvalue) -> None:
        if newvalue is None:
            self._metadata_dict[key] = None
        if key not in self._metadata_dict or newvalue != self._metadata_dict[key]:
            self._metadata_dict[key] = newvalue

    def getnotes(self, origin=None):
        return self._get_field("comment")

    def addnote(self, text, origin=None, position="append") -> None:
        currentnote = self._get_field("comment")
        if position == "append" and currentnote:
            self._set_field("comment", f"{currentnote}\n{text}")
        else:
            self._set_field("comment", text)

    def removenotes(self, origin=None) -> None:
        self._set_field("comment", "")

    @property
    def source(self):
        return self._get_field("source")

    @source.setter
    def source(self, source) -> None:
        self._rich_source = None
        self._set_field("source", source)

    @property
    def target(self):
        return self._get_field("target")

    @target.setter
    def target(self, target) -> None:
        self._rich_target = None
        self._set_field("target", target)

    def settargetlang(self, newlang: str) -> None:
        self._metadata_dict["target-lang"] = newlang

    targetlang = property(None, settargetlang)

    def __str__(self) -> str:
        return str(self._metadata_dict)

    def istranslated(self):
        return bool(self._metadata_dict.get("target", None))


class OmegaTFile(base.TranslationStore):
    """An OmegaT glossary file."""

    Name = "OmegaT Glossary"
    Mimetypes = ["application/x-omegat-glossary"]
    Extensions = ["utf8"]
    UnitClass = OmegaTUnit

    def __init__(self, inputfile=None, **kwargs) -> None:
        """Construct an OmegaT glossary, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self.extension = ""
        if inputfile is not None:
            self.parse(inputfile)

    def parse(self, input) -> None:  # ty:ignore[invalid-method-override]
        """Parsese the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            tmsrc = input.read()
            input.close()
            input = tmsrc
        try:
            input = input.decode(self.encoding)
        except UnicodeDecodeError as error:
            raise ValueError(
                "OmegaT files are either UTF-8 encoded or use the default system encoding"
            ) from error
        lines = csv.DictReader(
            input.split("\n"), fieldnames=OMEGAT_FIELDNAMES, dialect="omegat"
        )
        for line in lines:
            newunit = OmegaTUnit()
            newunit.metadata = line
            self.addunit(newunit)

    def serialize(self, out) -> None:
        # Check first if there is at least one translated unit
        translated_units = [u for u in self.units if u.istranslated()]
        if not translated_units:
            return

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=OMEGAT_FIELDNAMES, dialect="omegat")
        for unit in translated_units:
            writer.writerow(unit.metadata)
        out.write(output.getvalue().encode(self.encoding))


class OmegaTFileTab(OmegaTFile):
    """An OmegaT glossary file in the default system encoding."""

    Name = "OmegaT Glossary"
    Mimetypes = ["application/x-omegat-glossary"]
    Extensions = ["tab"]

    @property
    def encoding(self):
        return locale.getlocale()[1]
