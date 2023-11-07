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
    def test_empty_document(self):
        store = self.parse("")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == ""

    def test_plain_text_paragraph(self):
        input = [
            " A single paragraph. Slightly indented.\n",
            " Two lines.\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["A single paragraph. Slightly indented. Two lines."]
        assert store.units[0].getlocations()[0].endswith("p")
        translated_output = self.get_translated_output(store)
        assert (
            translated_output == "(A single paragraph. Slightly indented. Two lines.)\n"
        )

    def test_paragraph_with_basic_markup(self):
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

    def test_html_character_entities(self):
        input = "f&ouml;&ouml;"
        store = self.parse(input)
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["föö"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(föö)\n"

    def test_hard_line_break(self):
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

    def test_escaped_character(self):
        store = self.parse("\\*escaped, not emphasized\\*\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["\\*escaped, not emphasized\\*"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(\\*escaped, not emphasized\\*)\n"

    def test_html_span(self):
        store = self.parse("now <p>hear ye</p> all\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["now {1}hear ye{2} all"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(now <p>hear ye</p> all)\n"

    def test_code_span(self):
        store = self.parse("inline `code` span\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["inline `code` span"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(inline `code` span)\n"

    def test_plain_image(self):
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
        assert locations[0].endswith("link-title")

    def test_plain_image_no_title(self):
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

    def test_plain_link(self):
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

    def test_autolink(self):
        store = self.parse("what's the <http://autolink> problem?\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["what's the {1} problem?"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(what's the <http://autolink> problem?)\n"

    def test_atx_heading(self):
        store = self.parse("\n##  sweet *potato*  ##\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["sweet *potato*"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "\n## (sweet *potato*) ##\n"
        assert store.units[0].getlocations()[0].endswith("heading")

    def test_empty_atx_heading(self):
        input = [
            "## \n",
            "#\n",
            "### ###\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_setext_heading(self):
        store = self.parse("mm potatoes\n-----------\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["mm potatoes"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(mm potatoes)\n-----------\n"
        assert store.units[0].getlocations()[0].endswith("heading")

    def test_nested_list(self):
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
        assert store.units[0].getlocations()[0].endswith("list-item.list-item.p")

    def test_empty_list_item(self):
        input = [
            "1. foo\n",
            "2.\n",
            "3. bar\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        self.assertCountEqual(unit_sources, ["foo", "bar"])

    def test_code_block(self):
        input = [
            "    a simple\n",
            "      indented code block\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_html_block(self):
        input = [
            '<i class="foo">\n',
            "*bar*\n",
            "</i>\n",
        ]
        store = self.parse("".join(input))
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []

    def test_block_quote(self):
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
        assert locations[0].endswith("quote.p")

    def test_link_reference_definition_and_full_reference_link(self):
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
        assert locations[0].endswith("linkref.link-title")
        # location: link label
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "foo *bar*"
        ]
        assert len(locations) == 2
        assert all(loc.endswith("link-label") for loc in locations)

    def test_link_reference_definition_and_shortcut_reference_link(self):
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

    def test_link_reference_definition_and_collapsed_reference_link(self):
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

    def test_table_with_header(self):
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
        assert locations[0].endswith("table-cell")
        # location: regular table cell
        locations = [
            tu.getlocations()[0] for tu in store.units if tu.source == "Fourth"
        ]
        assert len(locations) == 1
        assert locations[0].endswith("table-cell")

    def test_thematic_break(self):
        store = self.parse("*******\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == "*******\n"

    def test_nested_block_tokens(self):
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

    def test_merging_of_adjacent_placeholders(self):
        store = self.parse("now hear ye</p> <h1> all\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["now hear ye{1} all"]
        translated_output = self.get_translated_output(store)
        assert translated_output == "(now hear ye</p> <h1> all)\n"

    def test_remove_placeholders_from_both_ends_of_translation_units(self):
        store = self.parse("<http://autolink> <h1> yeah </h1> <http://autolink>\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == ["yeah"]
        translated_output = self.get_translated_output(store)
        assert (
            translated_output
            == "<http://autolink> <h1> (yeah) </h1> <http://autolink>\n"
        )

    def test_paragraph_with_only_whitespace_and_placeholders(self):
        store = self.parse("<http://autolink> <p> <p> <p>\n")
        unit_sources = self.get_translation_unit_sources(store)
        assert unit_sources == []
        translated_output = self.get_translated_output(store)
        assert translated_output == "<http://autolink> <p> <p> <p>\n"

    def test_image_embedded_in_link(self):
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

    def test_placeholder_trimming(self):
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

        fragments[0].important = True
        fragments[4].important = True
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
    def test_hard_line_break_in_translation_unit(self):
        input = "yes box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace(" ", "\n")
        )
        assert store.filesrc == "yes\\\nbox\n"

    def test_missing_placeholder(self):
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "??")
        )
        assert store.filesrc == "yes ?? box\n"

    def test_duplicate_placeholder(self):
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "{1}{1}")
        )
        assert store.filesrc == "yes <http://autolink><http://autolink> box\n"

    def test_extraneous_placeholder(self):
        input = "yes <http://autolink> box\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: x.replace("{1}", "{1}{2}")
        )
        assert store.filesrc == "yes <http://autolink>{2} box\n"

    def test_reordered_placeholders(self):
        input = "yes <http://autolink> box <hr> all right\n"
        inputfile = BytesIO(input.encode())
        store = markdown.MarkdownFile(
            inputfile=inputfile, callback=lambda x: "all {2} messed up {1}!"
        )
        assert store.filesrc == "all <hr> messed up <http://autolink>!\n"

    def test_invalid_markdown_in_translation(self):
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
