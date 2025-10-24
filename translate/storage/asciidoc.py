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

This implementation uses pyparsing with a full-document grammar approach
for robust and maintainable parsing.
"""

from __future__ import annotations

from typing import Any

from pyparsing import (
    Forward,
    Group,
    LineEnd,
    LineStart,
    Literal,
    OneOrMore,
    Optional,
    ParseResults,
    ParserElement,
    Regex,
    SkipTo,
    StringEnd,
    StringStart,
    Suppress,
    White,
    ZeroOrMore,
    pythonStyleComment,
)

from translate.storage import base

# Enable packrat parsing for better performance
ParserElement.enablePackrat()

# Set default whitespace characters (space and tab only, not newlines)
ParserElement.setDefaultWhitespaceChars(' \t')


class AsciiDocUnit(base.TranslationUnit):
    """A unit of translatable/localisable AsciiDoc content."""

    def __init__(self, source: str | None = None) -> None:
        super().__init__(source)
        self.locations: list[str] = []
        self._element_type: str = "paragraph"
        self._prefix: str = ""
        self._suffix: str = ""

    def addlocation(self, location: str) -> None:
        self.locations.append(location)

    def getlocations(self) -> list[str]:
        return self.locations

    def set_element_info(self, element_type: str, prefix: str = "", suffix: str = "") -> None:
        """Store element type and formatting information."""
        self._element_type = element_type
        self._prefix = prefix
        self._suffix = suffix


class AsciiDocHeaderUnit(AsciiDocUnit):
    @staticmethod
    def isheader() -> bool:
        return True


class AsciiDocFile(base.TranslationStore):
    UnitClass = AsciiDocUnit

    def __init__(self, inputfile=None, callback=None) -> None:
        """
        Construct a new object instance.

        :param inputfile: if specified, the content of this file is read and parsed.
        :param callback: a function which takes a chunk of untranslated content as
          input and returns the corresponding translated content. Defaults to
          a no-op.
        """
        base.TranslationStore.__init__(self)
        self.filename: str | None = getattr(inputfile, "name", None)
        self.callback = callback or self._dummy_callback
        self.filesrc: str = ""
        self._elements: list[dict[str, Any]] = []  # Store parsed elements for reconstruction
        self._grammar = self._create_document_grammar()
        if inputfile is not None:
            adoc_src = inputfile.read()
            inputfile.close()
            self.parse(adoc_src)

    def parse(self, data: bytes) -> None:
        """Process the given source string (binary) using full-document pyparsing."""
        text = data.decode()
        
        try:
            # Parse the entire document at once
            parsed = self._grammar.parseString(text, parseAll=True)
            self._process_parsed_document(parsed, text)
        except Exception as e:
            # Fallback to the safer approach if parsing fails
            raise ValueError(f"Failed to parse AsciiDoc document: {e}") from e
        
        # Reconstruct the document
        self._reconstruct()
    
    def _process_parsed_document(self, parsed: ParseResults, original_text: str) -> None:
        """Process the parsed document and extract translation units."""
        line_number = 1
        
        for element in parsed:
            if not isinstance(element, dict):
                continue
                
            elem_type = element.get("type")
            if not elem_type:
                continue
            
            if elem_type == "header":
                # Document header - not translated
                header_content = element.content
                header = AsciiDocHeaderUnit(header_content)
                self.addunit(header)
                self._elements.append({
                    "type": "header",
                    "content": header_content,
                    "unit": header
                })
                line_number += header_content.count('\n')
                
            elif elem_type == "heading":
                marker = element["marker"]
                title = element["title"].rstrip().rstrip("=").strip()
                suffix = "\n" if element["content"].endswith("\n") else ""
                
                unit = self.addsourceunit(title)
                unit.addlocation(f"{self.filename or ''}:{line_number}")
                unit.set_element_info("heading", marker + " ", suffix)
                
                self._elements.append({
                    "type": "heading",
                    "level": len(marker),
                    "prefix": marker + " ",
                    "suffix": suffix,
                    "unit": unit,
                    "line": line_number,
                })
                line_number += element["content"].count('\n')
                
            elif elem_type == "list_item":
                marker = element["marker"]
                content = element["text"].strip()
                checklist_prefix = ""
                
                if element.get("checklist"):
                    checklist_prefix = element["checklist"] + " "
                
                unit = self.addsourceunit(content)
                unit.addlocation(f"{self.filename or ''}:{line_number}")
                prefix = marker + " " + checklist_prefix
                suffix = "\n" if element["content"].endswith("\n") else ""
                unit.set_element_info("list_item", prefix, suffix)
                
                self._elements.append({
                    "type": "list_item",
                    "level": len(marker),
                    "prefix": prefix,
                    "suffix": suffix,
                    "unit": unit,
                    "line": line_number,
                })
                line_number += element["content"].count('\n')
                
            elif elem_type == "description_list":
                term = element["term"].strip()
                definition = element["definition"].strip()
                suffix = "\n" if element["content"].endswith("\n") else ""
                
                unit = self.addsourceunit(definition)
                unit.addlocation(f"{self.filename or ''}:{line_number}")
                unit.set_element_info("description_list", f"{term}:: ", suffix)
                
                self._elements.append({
                    "type": "description_list",
                    "term": term,
                    "prefix": f"{term}:: ",
                    "suffix": suffix,
                    "unit": unit,
                    "line": line_number,
                })
                line_number += element["content"].count('\n')
                
            elif elem_type == "admonition":
                admon_type = element["admon_type"]
                content = element["text"].strip()
                suffix = "\n" if element["content"].endswith("\n") else ""
                
                unit = self.addsourceunit(content)
                unit.addlocation(f"{self.filename or ''}:{line_number}")
                unit.set_element_info("admonition", f"{admon_type}: ", suffix)
                
                self._elements.append({
                    "type": "admonition",
                    "admon_type": admon_type,
                    "prefix": f"{admon_type}: ",
                    "suffix": suffix,
                    "unit": unit,
                    "line": line_number,
                })
                line_number += element["content"].count('\n')
                
            elif elem_type == "paragraph":
                # Normalize whitespace in paragraphs
                para_text = " ".join(element["content"].strip().split())
                
                if para_text:
                    unit = self.addsourceunit(para_text)
                    unit.addlocation(f"{self.filename or ''}:{line_number}")
                    unit.set_element_info("paragraph", "", "\n")
                    
                    self._elements.append({
                        "type": "paragraph",
                        "unit": unit,
                        "line": line_number,
                        "original_lines": [element["content"]],
                    })
                line_number += element["content"].count('\n')
                
            elif elem_type in ("empty_line", "code_block", "comment", "attribute",
                             "list_continuation", "directive", "anchor", "block_title",
                             "conditional_block", "table"):
                # Non-translatable elements - preserve as-is
                self._elements.append({
                    "type": elem_type,
                    "content": element["content"],
                    "line": line_number,
                })
                line_number += element["content"].count('\n')
        
        # Remove trailing empty lines as they're artifacts of parsing
        while self._elements and self._elements[-1]["type"] == "empty_line":
            self._elements.pop()
    
    def _create_document_grammar(self) -> ParserElement:
        """
        Create a complete pyparsing grammar for AsciiDoc documents.
        
        This grammar parses the entire document structure at once,
        rather than line-by-line processing.
        """
        # Define newline
        newline = LineEnd()
        
        # Empty line
        empty_line = (LineStart() + newline).setResultsName("empty_line", listAllMatches=True)
        empty_line.setParseAction(lambda t: {"type": "empty_line", "content": "\n"})
        
        # Comments (single line starting with //)
        comment_line = (LineStart() + Literal("//") + SkipTo(newline | StringEnd()) + Optional(newline))
        comment_line.setResultsName("comment", listAllMatches=True)
        comment_line.setParseAction(lambda t: {"type": "comment", "content": "".join(t)})
        
        # Conditional directives
        conditional_start = LineStart() + (Literal("ifdef") | Literal("ifndef") | Literal("ifeval")) + Literal("::") + SkipTo(newline) + newline
        conditional_end = LineStart() + Literal("endif::") + SkipTo(newline | StringEnd()) + Optional(newline)
        
        # Conditional block (ifdef/ifndef...endif)
        # Simplified: match everything from start to corresponding end without recursion
        conditional_block = conditional_start + SkipTo(conditional_end, include=False) + conditional_end
        conditional_block.setResultsName("conditional_block", listAllMatches=True)
        conditional_block.setParseAction(lambda t: {"type": "conditional_block", "content": "".join(t)})
        
        # Anchors [[id]]
        anchor = (LineStart() + Literal("[[") + SkipTo("]]") + Literal("]]") + Optional(SkipTo(newline)) + newline)
        anchor.setResultsName("anchor", listAllMatches=True)
        anchor.setParseAction(lambda t: {"type": "anchor", "content": "".join(t)})
        
        # Block title (.Title)
        block_title = (LineStart() + Regex(r"\.[A-Za-z0-9][^\n]*") + newline)
        block_title.setResultsName("block_title", listAllMatches=True)
        block_title.setParseAction(lambda t: {"type": "block_title", "content": "".join(t)})
        
        # Attribute lines [attribute]
        attribute_line = (LineStart() + Literal("[") + SkipTo("]", failOn="\n") + Literal("]") + Optional(White()) + newline)
        attribute_line.setResultsName("attribute", listAllMatches=True)
        attribute_line.setParseAction(lambda t: {"type": "attribute", "content": "".join(t)})
        
        # Block delimiters (----, ...., ====, etc.)
        block_delimiter = Regex(r"[-=.*_+]{4,}")
        code_block = (LineStart() + block_delimiter("delim") + newline + 
                     SkipTo(LineStart() + block_delimiter + newline) + 
                     LineStart() + block_delimiter + newline)
        code_block.setResultsName("code_block", listAllMatches=True)
        code_block.setParseAction(lambda t: {"type": "code_block", "content": "".join(t)})
        
        # List continuation (+)
        list_continuation = (LineStart() + Literal("+") + newline)
        list_continuation.setResultsName("list_continuation", listAllMatches=True)
        list_continuation.setParseAction(lambda t: {"type": "list_continuation", "content": "".join(t)})
        
        # Headings (==, ===, etc.)
        heading_marker = Regex(r"={2,6}")
        heading = (LineStart() + heading_marker("marker") + White() + 
                  Regex(r"[^\n]+")("title") + newline)
        heading.setResultsName("heading", listAllMatches=True)
        heading.setParseAction(lambda t: {
            "type": "heading",
            "marker": t.marker,
            "title": t.title,
            "content": "".join(t)
        })
        
        # Unordered list items (*, **, etc.)
        unordered_marker = Regex(r"\*+")
        checklist = Regex(r"\[[*x ]\]")
        unordered_list_item = (LineStart() + unordered_marker("marker") + White() +
                              Optional(checklist("checklist") + White()) +
                              Regex(r"[^\n]+")("text") + newline)
        
        # Ordered list items (., .., etc.)
        ordered_marker = Regex(r"\.+")
        ordered_list_item = (LineStart() + ordered_marker("marker") + White() +
                            Regex(r"[^\n]+")("text") + newline)
        
        # Combine list items
        list_item = (unordered_list_item | ordered_list_item)
        list_item.setResultsName("list_item", listAllMatches=True)
        list_item.setParseAction(lambda t: {
            "type": "list_item",
            "marker": t.marker,
            "text": t.text,
            "checklist": t.checklist if hasattr(t, 'checklist') else "",
            "content": "".join(t)
        })
        
        # Description lists (term:: definition)
        description_list = (LineStart() + Regex(r"[^:\n]+")("term") + Literal("::") +
                           White() + Regex(r"[^\n]+")("definition") + newline)
        description_list.setResultsName("description_list", listAllMatches=True)
        description_list.setParseAction(lambda t: {
            "type": "description_list",
            "term": t.term,
            "definition": t.definition,
            "content": "".join(t)
        })
        
        # Admonitions (NOTE:, TIP:, etc.)
        admon_type = (Literal("NOTE") | Literal("TIP") | Literal("IMPORTANT") |
                     Literal("WARNING") | Literal("CAUTION"))
        admonition = (LineStart() + admon_type("admon_type") + Literal(":") +
                     White() + Regex(r"[^\n]+")("text") + newline)
        admonition.setResultsName("admonition", listAllMatches=True)
        admonition.setParseAction(lambda t: {
            "type": "admonition",
            "admon_type": t.admon_type,
            "text": t.text,
            "content": "".join(t)
        })
        
        # Table lines (starts with |)
        table_line = LineStart() + Literal("|") + SkipTo(newline) + newline
        table = OneOrMore(table_line | empty_line)
        table.setResultsName("table", listAllMatches=True)
        table.setParseAction(lambda t: {"type": "table", "content": "".join(t)})
        
        # Document header (= Title with attributes)
        header_line = LineStart() + Literal("=") + White() + SkipTo(newline) + newline
        header_attr = LineStart() + Literal(":") + SkipTo(newline) + newline
        header_content = header_line + ZeroOrMore(Regex(r"[^\n]*") + newline | header_attr)
        header = StringStart() + header_content
        header.setResultsName("header", listAllMatches=True)
        header.setParseAction(lambda t: {"type": "header", "content": "".join(t)})
        
        # Paragraph (consecutive non-empty, non-special lines)
        # Must not start with special markers
        para_line = LineStart() + Regex(r"(?![=*.\[:|//])[^\n]+") + newline
        paragraph = OneOrMore(para_line)
        paragraph.setResultsName("paragraph", listAllMatches=True)
        paragraph.setParseAction(lambda t: {"type": "paragraph", "content": "".join(t)})
        
        # Document structure: optional header followed by content elements
        content_element = (
            empty_line |
            conditional_block |
            comment_line |
            anchor |
            block_title |
            attribute_line |
            code_block |
            list_continuation |
            heading |
            list_item |
            description_list |
            admonition |
            table |
            paragraph
        )
        
        document = Optional(header) + ZeroOrMore(content_element) + StringEnd()
        
        return document

    def _reconstruct(self) -> None:
        """Reconstruct the AsciiDoc document with translations."""
        result: list[str] = []

        for element in self._elements:
            elem_type = element["type"]

            if elem_type == "header":
                if element.get("unit") and element["unit"].isheader():
                    result.append(element["content"])
            elif elem_type in {
                "empty_line",
                "code_block",
                "comment",
                "attribute",
                "list_continuation",
                "directive",
                "anchor",
                "block_title",
                "conditional_block",
            }:
                result.append(element["content"])
            elif elem_type in {
                "heading",
                "list_item",
                "admonition",
                "description_list",
            }:
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
