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

"""Tests for the AsciiDoc classes."""

from io import BytesIO
from unittest import TestCase

from translate.storage import asciidoc


class TestAsciiDocTranslationUnitExtractionAndTranslation(TestCase):
    def test_empty_document(self):
        store = self.parse("")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == ""

    def test_plain_text_paragraph(self):
        input = "A single paragraph.\nTwo lines.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["A single paragraph. Two lines."]
        assert store.units[0].getlocations()[0].endswith(":1")
        translated_output = self.get_translated_output(store)
        assert translated_output == "(A single paragraph. Two lines.)\n"

    def test_multiple_paragraphs(self):
        input = "First paragraph.\n\nSecond paragraph.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["First paragraph.", "Second paragraph."]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(First paragraph.)\n\n(Second paragraph.)\n"

    def test_heading_level_2(self):
        input = "== Section Title\n\nSome content.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Section Title", "Some content."]
        translated_output = self.get_translated_output(store)
        assert translated_output == "== (Section Title)\n\n(Some content.)\n"
        assert store.units[0].getlocations()[0].endswith(":1")

    def test_heading_level_3(self):
        input = "=== Subsection\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Subsection"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "=== (Subsection)\n"

    def test_unordered_list(self):
        input = "* First item\n* Second item\n* Third item\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["First item", "Second item", "Third item"])
        translated_output = self.get_translated_output(store)
        assert translated_output == "* (First item)\n* (Second item)\n* (Third item)\n"

    def test_nested_unordered_list(self):
        input = "* First level\n** Second level\n* Back to first\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources, ["First level", "Second level", "Back to first"]
        )
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "* (First level)\n** (Second level)\n* (Back to first)\n"
        )

    def test_ordered_list(self):
        input = ". First item\n. Second item\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["First item", "Second item"])
        translated_output = self.get_translated_output(store)
        assert translated_output == ". (First item)\n. (Second item)\n"

    def test_code_block(self):
        input = (
            "Some text.\n\n----\nCode block content\nMore code\n----\n\nAfter code.\n"
        )
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Code blocks are not extracted for translation
        self.assertCountEqual(unit_sources, ["Some text.", "After code."])
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "(Some text.)\n\n----\nCode block content\nMore code\n----\n\n(After code.)\n"
        )

    def test_literal_block(self):
        input = "Text before.\n\n....\nLiteral block\n....\n\nText after.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["Text before.", "Text after."])

    def test_comment(self):
        input = "// This is a comment\nActual content.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Actual content."]
        translated_output = self.get_translated_output(store)
        assert translated_output == "// This is a comment\n(Actual content.)\n"

    def test_document_title(self):
        input = "= Document Title\nAuthor Name\n\n== First Section\n\nContent here.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Document header is stored as a header unit but also appears in units list
        assert len(unit_sources) == 3
        assert store.units[0].isheader()
        # Check non-header units
        non_header_sources = [tu.source for tu in store.units if not tu.isheader()]
        self.assertCountEqual(non_header_sources, ["First Section", "Content here."])

    def test_paragraph_with_inline_formatting(self):
        # AsciiDoc uses different inline formatting than Markdown
        # *bold*, _italic_, `monospace`
        input = "This has *bold* and _italic_ text.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Inline formatting is preserved in the translation unit
        assert unit_sources == ["This has *bold* and _italic_ text."]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(This has *bold* and _italic_ text.)\n"

    def test_mixed_content(self):
        input = """== Introduction

This is the first paragraph.

This is the second paragraph.

=== Subsection

* Item one
* Item two

Another paragraph here.
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources,
            [
                "Introduction",
                "This is the first paragraph.",
                "This is the second paragraph.",
                "Subsection",
                "Item one",
                "Item two",
                "Another paragraph here.",
            ],
        )

    def test_admonition(self):
        input = "NOTE: This is an important note.\n\nSome text.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources, ["This is an important note.", "Some text."]
        )
        translated_output = self.get_translated_output(store)
        assert (
            translated_output == "NOTE: (This is an important note.)\n\n(Some text.)\n"
        )

    def test_warning_admonition(self):
        input = "WARNING: Be careful here.\n"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Be careful here."]
        translated_output = self.get_translated_output(store)
        assert translated_output == "WARNING: (Be careful here.)\n"

    def test_simple_table(self):
        input = """| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Table cells should be extracted
        self.assertCountEqual(unit_sources, ["Cell 1", "Cell 2", "Cell 3", "Cell 4"])

    def test_example_block(self):
        input = """Some text.

====
This is an example block.
====

More text.
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Example blocks are not extracted
        self.assertCountEqual(unit_sources, ["Some text.", "More text."])

    def test_attribute_line(self):
        input = """[NOTE]
This is a note.

[source,java]
----
code here
----

Regular paragraph.
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Attribute lines should not be extracted
        self.assertCountEqual(unit_sources, ["This is a note.", "Regular paragraph."])

    def test_sidebar_block(self):
        input = """Text before.

****
This is a sidebar.
****

Text after.
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        # Sidebar blocks are not extracted
        self.assertCountEqual(unit_sources, ["Text before.", "Text after."])

    def test_list_continuation(self):
        """Test list continuation markers."""
        input = """* Item one
+
More content for item one.
* Item two
"""
        store = self.parse(input)
        unit_sources = [tu.source for tu in store.units if not tu.isheader()]
        # Should extract list items and continuation content, but not the + marker
        self.assertCountEqual(
            unit_sources, ["Item one", "More content for item one.", "Item two"]
        )

    def test_checklist(self):
        """Test checklist syntax."""
        input = """* [*] Checked item
* [x] Also checked
* [ ] Unchecked item
* Regular item
"""
        store = self.parse(input)
        unit_sources = [tu.source for tu in store.units if not tu.isheader()]
        # Checklist markers should not be included in translatable content
        self.assertCountEqual(
            unit_sources,
            ["Checked item", "Also checked", "Unchecked item", "Regular item"],
        )
        translated_output = self.get_translated_output(store)
        # Checklist markers should be preserved in output
        assert "* [*] (Checked item)" in translated_output
        assert "* [x] (Also checked)" in translated_output
        assert "* [ ] (Unchecked item)" in translated_output

    def test_description_list(self):
        """Test description list."""
        input = """Term 1:: Definition for term 1
Term 2:: Definition for term 2
Another term:: Another definition
"""
        store = self.parse(input)
        unit_sources = [tu.source for tu in store.units if not tu.isheader()]
        # Only definitions should be extracted, not terms
        self.assertCountEqual(
            unit_sources,
            [
                "Definition for term 1",
                "Definition for term 2",
                "Another definition",
            ],
        )
        translated_output = self.get_translated_output(store)
        # Terms should be preserved
        assert "Term 1:: (Definition for term 1)" in translated_output
        assert "Term 2:: (Definition for term 2)" in translated_output

    def test_real_world_neuvector_content(self):
        """Test with actual content from neuvector-product-docs repository."""
        input = """= 5.x Overview
:revdate: 2025-01-10
:page-revdate: {revdate}

== The Full Life-Cycle Container Security Platform

[NOTE]
====
These docs describe the 5.x version.
====

{product-name} provides a powerful platform.

. First item here.
. Second item here.

Other features include more stuff.
"""
        store = self.parse(input)
        # Get only non-header units
        unit_sources = [tu.source for tu in store.units if not tu.isheader()]
        # Should extract heading, paragraph, list items, and final paragraph
        # But NOT the note block content, attributes, or document attributes
        expected = [
            "The Full Life-Cycle Container Security Platform",
            "{product-name} provides a powerful platform.",
            "First item here.",
            "Second item here.",
            "Other features include more stuff.",
        ]
        self.assertCountEqual(unit_sources, expected)

    @staticmethod
    def parse(adoc):
        inputfile = BytesIO(adoc.encode())
        return asciidoc.AsciiDocFile(inputfile=inputfile, callback=lambda x: f"({x})")

    @staticmethod
    def get_translation_unit_sources(store):
        return [tu.source for tu in store.units]

    @staticmethod
    def get_translated_output(store):
        return store.filesrc


class TestAsciiDocRendering:
    def test_preserves_structure(self):
        input = "== Heading\n\nParagraph text.\n"
        inputfile = BytesIO(input.encode())
        store = asciidoc.AsciiDocFile(inputfile=inputfile, callback=lambda x: x.upper())
        assert store.filesrc == "== HEADING\n\nPARAGRAPH TEXT.\n"
