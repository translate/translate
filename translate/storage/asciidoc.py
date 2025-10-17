#
# Copyright 2025 Translate.org
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
Module for parsing AsciiDoc files for translation.

The principles for extraction of translation units are as follows:

1. Extract all content relevant for translation, at the cost of also
   including some formatting.
2. One translation unit per paragraph.
3. Keep formatting out of the translation units as much as possible.
   Use placeholders {1}, {2}, ..., as needed for complex inline elements.
4. Support common AsciiDoc elements: headings, paragraphs, lists, etc.

White space within translation units is normalized.
"""

from __future__ import annotations

import re

from translate.storage import base


class AsciiDocUnit(base.TranslationUnit):
    """A unit of translatable/localisable AsciiDoc content."""

    def __init__(self, source=None):
        super().__init__(source)
        self.locations = []
        self._element_type = "paragraph"
        self._prefix = ""
        self._suffix = ""

    def addlocation(self, location):
        self.locations.append(location)

    def getlocations(self):
        return self.locations

    def set_element_info(self, element_type: str, prefix: str = "", suffix: str = ""):
        """Store element type and formatting information."""
        self._element_type = element_type
        self._prefix = prefix
        self._suffix = suffix


class AsciiDocHeaderUnit(AsciiDocUnit):
    @staticmethod
    def isheader():
        return True


class AsciiDocFile(base.TranslationStore):
    UnitClass = AsciiDocUnit

    def __init__(self, inputfile=None, callback=None):
        """
        Construct a new object instance.

        :param inputfile: if specified, the content of this file is read and parsed.
        :param callback: a function which takes a chunk of untranslated content as
          input and returns the corresponding translated content. Defaults to
          a no-op.
        """
        base.TranslationStore.__init__(self)
        self.filename = getattr(inputfile, "name", None)
        self.callback = callback or self._dummy_callback
        self.filesrc = ""
        self._elements = []  # Store parsed elements for reconstruction
        if inputfile is not None:
            adoc_src = inputfile.read()
            inputfile.close()
            self.parse(adoc_src)

    def parse(self, data):
        """Process the given source string (binary)."""
        text = data.decode()
        lines = text.splitlines(keepends=True)

        # Check for document header (first line starting with = )
        header_end = -1
        if lines and lines[0].startswith("= "):
            # The header includes: title line, optional author/revision lines, and attributes
            # Keep going until we hit a blank line followed by content or just content
            header_end = 0  # At minimum, include the title
            for i in range(1, len(lines)):
                line = lines[i]
                # Attributes start with :
                if line.startswith(":"):
                    header_end = i
                # Empty line might be end of header or separator within header
                elif not line.strip():
                    # Check if next line is content (starts new section)
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # If next line is a section header or regular content, end header here
                        if next_line.strip() and not next_line.startswith(":"):
                            header_end = i
                            break
                    header_end = i
                # First non-empty, non-attribute line after title could be author/date
                # but only if we haven't seen a blank line yet
                elif i == 1 or (i == 2 and not lines[1].strip()):
                    # Author or date line
                    header_end = i
                else:
                    # Regular content starts
                    break

            if header_end >= 0:
                header_content = "".join(lines[: header_end + 1])
                header = AsciiDocHeaderUnit(header_content)
                self.addunit(header)
                self._elements.append(
                    {"type": "header", "content": header_content, "unit": header}
                )
                lines = lines[header_end + 1 :]

        # Parse the rest of the document
        self._parse_content(lines)

        # Reconstruct the document
        self._reconstruct()

    def _parse_content(self, lines: list[str]):
        """Parse AsciiDoc content and extract translation units."""
        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                self._elements.append({"type": "empty", "content": line})
                i += 1
                continue

            # Heading (section titles)
            heading_match = re.match(r"^(={2,6})\s+(.+?)(?:\s+={2,6})?\s*$", line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                unit = self.addsourceunit(title)
                unit.addlocation(f"{self.filename or ''}:{i + 1}")
                unit.set_element_info(
                    "heading",
                    heading_match.group(1) + " ",
                    "\n" if line.endswith("\n") else "",
                )

                self._elements.append(
                    {
                        "type": "heading",
                        "level": level,
                        "prefix": heading_match.group(1) + " ",
                        "suffix": "\n" if line.endswith("\n") else "",
                        "unit": unit,
                        "line": i + 1,
                    }
                )
                i += 1
                continue

            # List item (unordered)
            list_match = re.match(r"^(\*+)\s+(.+)$", line)
            if list_match:
                level = len(list_match.group(1))
                content = list_match.group(2).strip()

                unit = self.addsourceunit(content)
                unit.addlocation(f"{self.filename or ''}:{i + 1}")
                unit.set_element_info(
                    "list_item",
                    list_match.group(1) + " ",
                    "\n" if line.endswith("\n") else "",
                )

                self._elements.append(
                    {
                        "type": "list_item",
                        "level": level,
                        "prefix": list_match.group(1) + " ",
                        "suffix": "\n" if line.endswith("\n") else "",
                        "unit": unit,
                        "line": i + 1,
                    }
                )
                i += 1
                continue

            # List item (ordered)
            ordered_list_match = re.match(r"^(\.+)\s+(.+)$", line)
            if ordered_list_match:
                level = len(ordered_list_match.group(1))
                content = ordered_list_match.group(2).strip()

                unit = self.addsourceunit(content)
                unit.addlocation(f"{self.filename or ''}:{i + 1}")
                unit.set_element_info(
                    "list_item",
                    ordered_list_match.group(1) + " ",
                    "\n" if line.endswith("\n") else "",
                )

                self._elements.append(
                    {
                        "type": "list_item",
                        "level": level,
                        "prefix": ordered_list_match.group(1) + " ",
                        "suffix": "\n" if line.endswith("\n") else "",
                        "unit": unit,
                        "line": i + 1,
                    }
                )
                i += 1
                continue

            # Code block or literal block
            if line.strip().startswith("----") or line.strip().startswith("...."):
                delimiter = line.strip()
                block_lines = [line]
                i += 1
                while i < len(lines):
                    block_lines.append(lines[i])
                    if lines[i].strip() == delimiter:
                        i += 1
                        break
                    i += 1

                self._elements.append(
                    {"type": "code_block", "content": "".join(block_lines)}
                )
                continue

            # Comment
            if line.startswith("//"):
                self._elements.append({"type": "comment", "content": line})
                i += 1
                continue

            # Admonitions (NOTE, TIP, IMPORTANT, WARNING, CAUTION)
            admonition_match = re.match(
                r"^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s+(.+)$", line
            )
            if admonition_match:
                admon_type = admonition_match.group(1)
                content = admonition_match.group(2).strip()

                unit = self.addsourceunit(content)
                unit.addlocation(f"{self.filename or ''}:{i + 1}")
                unit.set_element_info(
                    "admonition",
                    f"{admon_type}: ",
                    "\n" if line.endswith("\n") else "",
                )

                self._elements.append(
                    {
                        "type": "admonition",
                        "admon_type": admon_type,
                        "prefix": f"{admon_type}: ",
                        "suffix": "\n" if line.endswith("\n") else "",
                        "unit": unit,
                        "line": i + 1,
                    }
                )
                i += 1
                continue

            # Table detection (simple tables with |)
            if line.strip().startswith("|"):
                table_lines = []
                start_line = i
                # Collect all table lines
                while i < len(lines) and (
                    lines[i].strip().startswith("|") or not lines[i].strip()
                ):
                    table_lines.append(lines[i])
                    i += 1
                    if i < len(lines) and not lines[i].strip():
                        # Check if next non-empty line is still part of table
                        next_i = i
                        while next_i < len(lines) and not lines[next_i].strip():
                            next_i += 1
                        if next_i >= len(lines) or not lines[next_i].strip().startswith(
                            "|"
                        ):
                            break

                # Parse table cells for translation
                for table_line in table_lines:
                    if table_line.strip() and "|" in table_line:
                        # Extract cells (simple approach)
                        cells = [
                            cell.strip()
                            for cell in table_line.split("|")
                            if cell.strip()
                        ]
                        for cell in cells:
                            # Skip cell separator markers and empty cells
                            if cell and not cell.startswith("="):
                                unit = self.addsourceunit(cell)
                                unit.addlocation(
                                    f"{self.filename or ''}:{start_line + 1}"
                                )
                                unit.set_element_info("table_cell", "", "")

                self._elements.append(
                    {
                        "type": "table",
                        "content": "".join(table_lines),
                        "line": start_line + 1,
                    }
                )
                continue

            # Paragraph - collect consecutive non-empty lines
            para_lines = []
            start_line = i
            while i < len(lines) and lines[i].strip():
                # Check if this is a special line that breaks paragraphs
                if (
                    re.match(r"^(={2,6}|\*+|\.+)\s+", lines[i])
                    or lines[i].strip().startswith("----")
                    or lines[i].strip().startswith("....")
                    or lines[i].startswith("//")
                ):
                    break
                para_lines.append(lines[i])
                i += 1

            if para_lines:
                # Join paragraph lines and normalize whitespace
                para_text = " ".join(line.strip() for line in para_lines)

                if para_text:
                    unit = self.addsourceunit(para_text)
                    unit.addlocation(f"{self.filename or ''}:{start_line + 1}")
                    unit.set_element_info("paragraph", "", "\n")

                    self._elements.append(
                        {
                            "type": "paragraph",
                            "unit": unit,
                            "line": start_line + 1,
                            "original_lines": para_lines,
                        }
                    )

    def _reconstruct(self):
        """Reconstruct the AsciiDoc document with translations."""
        result = []

        for element in self._elements:
            elem_type = element["type"]

            if elem_type == "header":
                if element.get("unit") and element["unit"].isheader():
                    result.append(element["content"])
            elif elem_type in {"empty", "code_block", "comment"}:
                result.append(element["content"])
            elif elem_type in {"heading", "list_item", "admonition"}:
                unit = element.get("unit")
                if unit:
                    translated = self.callback(unit.source)
                    result.append(f"{element['prefix']}{translated}{element['suffix']}")
            elif elem_type == "table":
                # For tables, we need to reconstruct with translated cells
                # For now, preserve the original table structure
                # (proper table translation would require more complex parsing)
                result.append(element["content"])
            elif elem_type == "paragraph":
                unit = element.get("unit")
                if unit:
                    translated = self.callback(unit.source)
                    # Try to preserve line structure somewhat
                    result.append(f"{translated}\n")

        self.filesrc = "".join(result)

    @staticmethod
    def _dummy_callback(text: str) -> str:
        return text
