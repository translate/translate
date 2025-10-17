from __future__ import annotations

import os

from translate.convert import po2asciidoc

from . import test_convert


class TestPO2AsciiDoc(test_convert.TestConvertCommand):
    convertmodule = po2asciidoc
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]

    def test_convert_simple_asciidoc(self):
        """Test basic conversion from PO to AsciiDoc."""
        adoc_source = "== Heading\n\nThis is a paragraph.\n"
        self.create_testfile("template.adoc", adoc_source)

        po_source = """
#: :1
msgid "Heading"
msgstr "Titre"

#: :3
msgid "This is a paragraph."
msgstr "C'est un paragraphe."
"""
        self.create_testfile("translations.po", po_source)

        self.run_command("translations.po", "output.adoc", template="template.adoc")

        assert os.path.isfile(self.get_testfilename("output.adoc"))
        output = self.read_testfile("output.adoc").decode()
        assert "== Titre" in output
        assert "C'est un paragraphe." in output

    def test_convert_with_list(self):
        """Test conversion with list items."""
        adoc_source = "* Item one\n* Item two\n"
        self.create_testfile("template.adoc", adoc_source)

        po_source = """
#: :1
msgid "Item one"
msgstr "Premier élément"

#: :2
msgid "Item two"
msgstr "Deuxième élément"
"""
        self.create_testfile("translations.po", po_source)

        self.run_command("translations.po", "output.adoc", template="template.adoc")

        output = self.read_testfile("output.adoc").decode()
        assert "* Premier élément" in output
        assert "* Deuxième élément" in output
