#
# Copyright 2023 Anders Kaplan
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

"""Tests for the Markdown classes."""

from io import BytesIO
from unittest import TestCase

from translate.storage import markdown


class TestMarkdownTranslationUnitExtractionAndTranslation(TestCase):
    def test_empty_document(self) -> None:
        store = self.parse("")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == ""

    def test_plain_text_paragraph(self) -> None:
        input = [
            " A single paragraph. Slightly indented.\n",
            " Two lines.\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["A single paragraph. Slightly indented. Two lines."]
        assert store.units[0].getlocations()[0].endswith("1")
        translated_output = self.get_translated_output(store)
        assert (
            translated_output == "(A single paragraph. Slightly indented. Two lines.)\n"
        )

    def test_paragraph_with_basic_markup(self) -> None:
        input = [
            " *A* **single** _paragraph_. __Slightly__ ~~indented~~.\n",
            " **With *nested* markup**.\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == [
            "*A* **single** _paragraph_. __Slightly__ ~~indented~~. **With *nested* markup**."
        ]
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "(*A* **single** _paragraph_. __Slightly__ ~~indented~~. **With *nested* markup**.)\n"
        )

    def test_html_character_entities(self) -> None:
        input = "f&ouml;&ouml;"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["föö"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(föö)\n"

    def test_hard_line_break(self) -> None:
        input = [
            "alpha\n",
            "beta\\\n",
            "gamma  \n",
            "delta\n",
            "epsilon\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        # both types of hard line breaks are rendered as a single '\n' in the TU
        assert unit_sources == ["alpha beta\ngamma\ndelta epsilon"]
        translated_output = self.get_translated_output(store)
        # a '\n' in the translation gets rendered as '\\\n' in the markdown
        assert translated_output == "(alpha beta\\\ngamma\\\ndelta epsilon)\n"

    def test_escaped_character(self) -> None:
        store = self.parse("\\*escaped, not emphasized\\*\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["\\*escaped, not emphasized\\*"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(\\*escaped, not emphasized\\*)\n"

    def test_html_span(self) -> None:
        store = self.parse("now <p>hear ye</p> all\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["now {1}hear ye{2} all"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(now <p>hear ye</p> all)\n"

    def test_code_span(self) -> None:
        store = self.parse("inline `code` span\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["inline `code` span"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(inline `code` span)\n"

    def test_plain_image(self) -> None:
        store = self.parse('![foo](/url "title")\n')
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources,
            [
                "![foo]{1}",  # structurally important placeholder may not be removed even if it's at the end of the translation unit
                "title",
            ],
        )
        translated_output = self.get_translated_output(store)
        assert translated_output == '(![foo](/url "(title)"))\n'
        # location: link title
        locations = [tu.getlocations()[0] for tu in store.units if tu.source == "title"]
        assert len(locations) == 1
        assert locations[0].endswith("1")

    def test_plain_image_no_title(self) -> None:
        store = self.parse("![foo](/url)\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert (
            unit_sources
            == [
                "![foo]{1}"  # structurally important placeholder may not be removed even if it's at the end of the translation unit
            ]
        )
        translated_output = self.get_translated_output(store)
        assert translated_output == "(![foo](/url))\n"

    def test_plain_link(self) -> None:
        store = self.parse('[link](/url "title \\"&quot;")\n')
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources,
            [
                "[link]{1}",  # structurally important placeholder may not be removed even if it's at the end of the translation unit
                'title ""',
            ],
        )
        translated_output = self.get_translated_output(store)
        assert translated_output == '([link](/url "(title "")"))\n'

    def test_autolink(self) -> None:
        store = self.parse("what's the <http://autolink> problem?\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["what's the {1} problem?"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(what's the <http://autolink> problem?)\n"

    def test_atx_heading(self) -> None:
        store = self.parse("\n##  sweet *potato*  ##\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["sweet *potato*"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "\n## (sweet *potato*) ##\n"
        assert store.units[0].getlocations()[0].endswith("2")

    def test_empty_atx_heading(self) -> None:
        input = [
            "## \n",
            "#\n",
            "### ###\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_setext_heading(self) -> None:
        store = self.parse("mm potatoes\n-----------\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["mm potatoes"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(mm potatoes)\n-----------\n"
        assert store.units[0].getlocations()[0].endswith("1")

    def test_nested_list(self) -> None:
        input = [
            "* 1. something\n",
            "  2. *or other*\n",
            "* the end.\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["something", "*or other*", "the end."])
        translated_output = self.get_translated_output(store)
        expected = [
            "* 1. (something)\n",
            "  2. (*or other*)\n",
            "* (the end.)\n",
        ]
        assert translated_output == "".join(expected)
        assert store.units[0].getlocations()[0].endswith("1")

    def test_empty_list_item(self) -> None:
        input = [
            "1. foo\n",
            "2.\n",
            "3. bar\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["foo", "bar"])

    def test_code_block(self) -> None:
        input = [
            "    a simple\n",
            "      indented code block\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_html_block(self) -> None:
        input = [
            '<i class="foo">\n',
            "*bar*\n",
            "</i>\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_block_quote(self) -> None:
        input = [
            "> # Foo\n",
            "> bar\n",
            "> baz\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["Foo", "bar baz"])
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "bar baz"
        ]
        assert len(locations) == 1
        assert locations[0].endswith("1")

    def test_link_reference_definition_and_full_reference_link(self) -> None:
        input = [
            '[foo *bar*]: train.jpg "train & tracks"\n',
            "[railroad link][foo *bar*] hello\n",
        ]
        store = self.parse("".join(input))
        self.assertCountEqual(
            self.get_translation_unit_sources(store),
            ["foo *bar*", "train & tracks", "[railroad link]{1} hello", "foo *bar*"],
        )
        expected = [
            '[(foo *bar*)]: train.jpg "(train & tracks)"\n',
            "([railroad link][(foo *bar*)] hello)\n",
        ]
        assert self.get_translated_output(store) == "".join(expected)
        # location: link title
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "train & tracks"
        ]
        assert len(locations) == 1
        assert locations[0].endswith("1")
        # location: link label
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "foo *bar*"
        ]
        assert len(locations) == 2
        assert all(loc.endswith(str(i)) for i, loc in enumerate(locations, start=1))

    def test_link_reference_definition_and_shortcut_reference_link(self) -> None:
        store = self.parse('[foo *bar*]: train.jpg "train & tracks"\n![foo *bar*]\n')
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources, ["foo *bar*", "train & tracks", "![foo *bar*]"]
        )
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == '[(foo *bar*)]: train.jpg "(train & tracks)"\n(![foo *bar*])\n'
        )

    def test_link_reference_definition_and_collapsed_reference_link(self) -> None:
        store = self.parse('[foo *bar*]: train.jpg "train & tracks"\n![foo *bar*][]\n')
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources, ["foo *bar*", "train & tracks", "![foo *bar*][]"]
        )
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == '[(foo *bar*)]: train.jpg "(train & tracks)"\n(![foo *bar*][])\n'
        )

    def test_table_with_header(self) -> None:
        input = [
            "| First cell | Second cell |\n",
            "| ---------- | ----------- |\n",
            "| Third      | Fourth      |\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources, ["First cell", "Second cell", "Third", "Fourth"]
        )
        translated_output = self.get_translated_output(store)
        expected = [
            "| (First cell) | (Second cell) |\n",
            "| ------------ | ------------- |\n",
            "| (Third)      | (Fourth)      |\n",
        ]
        assert translated_output == "".join(expected)
        # location: table header cell
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "First cell"
        ]
        assert len(locations) == 1
        assert locations[0].endswith("1")
        # location: regular table cell
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "Fourth"
        ]
        assert len(locations) == 1
        assert locations[0].endswith("1")

    def test_thematic_break(self) -> None:
        store = self.parse("*******\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == "*******\n"

    def test_nested_block_tokens(self) -> None:
        input = [
            "> text\n",
            "> 1. list item\n",
            ">\n",
            "> more text\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["text", "list item", "more text"])
        translated_output = self.get_translated_output(store)
        expected = [
            "> (text)\n",
            "> 1. (list item)\n",
            "> \n",
            "> (more text)\n",
        ]
        assert translated_output == "".join(expected)

    def test_merging_of_adjacent_placeholders(self) -> None:
        store = self.parse("now hear ye</p> <h1> all\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["now hear ye{1} all"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(now hear ye</p> <h1> all)\n"

    def test_remove_placeholders_from_both_ends_of_translation_units(self) -> None:
        store = self.parse("<http://autolink> <h1> yeah </h1> <http://autolink>\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["yeah"]
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "<http://autolink> <h1> (yeah) </h1> <http://autolink>\n"
        )

    def test_paragraph_with_only_whitespace_and_placeholders(self) -> None:
        store = self.parse("<http://autolink> <p> <p> <p>\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == "<http://autolink> <p> <p> <p>\n"

    def test_image_embedded_in_link(self) -> None:
        store = self.parse(
            "[*embedded image* ![moon](moon.jpg \"the moon y'all\")](/uri 'link title')\n"
        )
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(
            unit_sources,
            [
                "[*embedded image* ![moon]{1}]{2}",
                "the moon y'all",
                "link title",
            ],
        )
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "([*embedded image* ![moon](moon.jpg \"(the moon y'all)\")](/uri '(link title)'))\n"
        )

    def test_placeholder_trimming(self) -> None:
        fragments = [
            markdown.Fragment("a", placeholder_content=[markdown.Fragment("")]),
            markdown.Fragment(" "),
            markdown.Fragment("b"),
            markdown.Fragment(" "),
            markdown.Fragment("c", placeholder_content=[markdown.Fragment("")]),
        ]
        (
            leader,
            content,
            trailer,
        ) = markdown.TranslatingMarkdownRenderer.trim_flanking_placeholders(fragments)
        assert leader == fragments[0:2]
        assert content == fragments[2:3]
        assert trailer == fragments[3:5]

        fragments[0].important = True  # ty:ignore[invalid-assignment]
        fragments[4].important = True  # ty:ignore[invalid-assignment]
        (
            leader,
            content,
            trailer,
        ) = markdown.TranslatingMarkdownRenderer.trim_flanking_placeholders(fragments)
        assert leader == []
        assert content == fragments
        assert trailer == []

    @staticmethod
    def parse(md):
        inputfile = BytesIO(md.encode())
        return markdown.MarkdownFile(inputfile=inputfile, callback=lambda x: f"({x})")

    @staticmethod
    def get_translation_unit_sources(store):
        return [tu.source for tu in store.units]

    @staticmethod
    def get_translated_output(store):
        return store.filesrc


class TestMarkdownRendering:
    def test_hard_line_break_in_translation_unit(self) -> None:
        input = "yes box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace(" ", "\n")
        )
        assert store.filesrc == "yes\\\nbox\n"

    def test_missing_placeholder(self) -> None:
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "??")
        )
        assert store.filesrc == "yes ?? box\n"

    def test_duplicate_placeholder(self) -> None:
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "{1}{1}")
        )
        assert store.filesrc == "yes <http://autolink><http://autolink> box\n"

    def test_extraneous_placeholder(self) -> None:
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "{1}{2}")
        )
        assert store.filesrc == "yes <http://autolink>{2} box\n"

    def test_reordered_placeholders(self) -> None:
        input = "yes <http://autolink> box <hr> all right\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: "all {2} messed up {1}!"
        )
        assert store.filesrc == "all <hr> messed up <http://autolink>!\n"

    def test_invalid_markdown_in_translation(self) -> None:
        # The translated text is processed by removing leading and trailing
        # whitespace, converting line breaks to hard line breaks, and replacing
        # placeholders. Nothing else. Therefore it's quite possible to produce
        # invalid markdown, or rather, unexpected markdown this way.
        # This is by design.
        input = "whatever\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile,
            callback=lambda x: "\t1.  ---  \n|  yeah  |\n|  whatever |  ",
        )
        assert store.filesrc == "1.  ---  \\\n|  yeah  |\\\n|  whatever |\n"


class TestMarkdownTranslationIgnore:
    def test_ignore_section_basic(self) -> None:
        """Test that content between translate:off and translate:on is not extracted."""
        input = """Translate this

<!-- translate:off -->

Don't translate this

<!-- translate:on -->

Translate this too
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Translate this", "Translate this too"]
        translated_output = self.get_translated_output(store)
        expected = """(Translate this)

<!-- translate:off -->

Don't translate this

<!-- translate:on -->

(Translate this too)
"""
        assert translated_output == expected

    def test_ignore_section_with_markup(self) -> None:
        """Test that ignored content preserves its markup."""
        input = """Before

<!-- translate:off -->

**Bold** and *italic* text with [links](http://example.com)

<!-- translate:on -->

After
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Before", "After"]
        translated_output = self.get_translated_output(store)
        expected = """(Before)

<!-- translate:off -->

**Bold** and *italic* text with [links](http://example.com)

<!-- translate:on -->

(After)
"""
        assert translated_output == expected

    def test_ignore_section_with_code_block(self) -> None:
        """Test ignoring sections with code blocks."""
        input = """Text before

<!-- translate:off -->

```python
def hello():
    print("world")
```

<!-- translate:on -->

Text after
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Text before", "Text after"]

    def test_multiple_ignore_sections(self) -> None:
        """Test multiple ignore sections in the same document."""
        input = """First

<!-- translate:off -->

Ignore A

<!-- translate:on -->

Second

<!-- translate:off -->

Ignore B

<!-- translate:on -->

Third
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["First", "Second", "Third"]

    def test_ignore_at_start(self) -> None:
        """Test that ignore section at start of document works."""
        input = """<!-- translate:off -->

Ignored

<!-- translate:on -->

Translated
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Translated"]

    def test_ignore_at_end(self) -> None:
        """Test that ignore section at end of document works."""
        input = """Translated

<!-- translate:off -->

Ignored
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Translated"]

    def test_nested_structures_in_ignore(self) -> None:
        """Test that nested structures like lists and quotes are ignored."""
        input = """Before

<!-- translate:off -->

> Block quote
> - List item 1
> - List item 2

<!-- translate:on -->

After
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Before", "After"]

    def test_link_references_in_ignore(self) -> None:
        """Test that link reference definitions in ignored sections are not extracted."""
        input = """Text

<!-- translate:off -->

[Reference 1]: http://example.com "Title 1"
[Reference 2]: http://example.org

<!-- translate:on -->

More text
"""
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["Text", "More text"]
        # Verify the link references are preserved in output
        assert "[Reference 1]: http://example.com" in store.filesrc
        assert "[Reference 2]: http://example.org" in store.filesrc

    def test_docpath_heading_hierarchy(self) -> None:
        """Test logical document path with heading hierarchy."""
        input = "# Chapter 1\n\nFirst paragraph.\n\nSecond paragraph.\n\n## Section 1.1\n\nThird paragraph.\n\n# Chapter 2\n\nFourth paragraph.\n"
        store = self.parse(input)
        docpaths = [tu.getdocpath() for tu in store.units]
        assert docpaths == [
            "h1[1]",
            "h1[1]/p[1]",
            "h1[1]/p[2]",
            "h1[1]/h2[1]",
            "h1[1]/h2[1]/p[1]",
            "h1[2]",
            "h1[2]/p[1]",
        ]

    def test_docpath_no_initial_heading(self) -> None:
        """Test docpath for content before any heading."""
        input = "Introduction.\n\n# Title\n\nContent.\n"
        store = self.parse(input)
        assert store.units[0].getdocpath() == "p[1]"
        assert store.units[1].getdocpath() == "h1[1]"
        assert store.units[2].getdocpath() == "h1[1]/p[1]"

    def test_docpath_list_items(self) -> None:
        """Test docpath for list items."""
        input = "# Title\n\n- Item 1\n- Item 2\n- Item 3\n"
        store = self.parse(input)
        docpaths = [tu.getdocpath() for tu in store.units]
        assert docpaths == [
            "h1[1]",
            "h1[1]/li[1]/p[1]",
            "h1[1]/li[2]/p[1]",
            "h1[1]/li[3]/p[1]",
        ]

    def test_docpath_blockquote(self) -> None:
        """Test docpath for blockquotes."""
        input = "# Title\n\n> A quote\n\nParagraph.\n"
        store = self.parse(input)
        docpaths = [tu.getdocpath() for tu in store.units]
        assert docpaths == [
            "h1[1]",
            "h1[1]/blockquote[1]/p[1]",
            "h1[1]/p[1]",
        ]

    def test_docpath_table(self) -> None:
        """Test docpath for tables."""
        input = "# Title\n\nParagraph.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"
        store = self.parse(input)
        assert store.units[0].getdocpath() == "h1[1]"
        assert store.units[1].getdocpath() == "h1[1]/p[1]"
        # All table cells share the same table docpath
        for unit in store.units[2:]:
            assert unit.getdocpath() == "h1[1]/table[1]"

    def test_docpath_setext_headings(self) -> None:
        """Test docpath with setext-style headings."""
        input = "Chapter 1\n=========\n\nContent.\n\nSection 1.1\n-----------\n\nMore content.\n"
        store = self.parse(input)
        docpaths = [tu.getdocpath() for tu in store.units]
        assert docpaths == [
            "h1[1]",
            "h1[1]/p[1]",
            "h1[1]/h2[1]",
            "h1[1]/h2[1]/p[1]",
        ]

    @staticmethod
    def parse(md):
        inputfile = BytesIO(md.encode())
        return markdown.MarkdownFile(inputfile=inputfile, callback=lambda x: f"({x})")

    @staticmethod
    def get_translation_unit_sources(store):
        return [tu.source for tu in store.units]

    @staticmethod
    def get_translated_output(store):
        return store.filesrc
