from __future__ import annotations

import os

from translate.convert import asciidoc2po
from translate.storage.po import pofile

from . import test_convert


class TestAsciiDoc2PO(test_convert.TestConvertCommand):
    convertmodule = asciidoc2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates=DUPLICATESTYLE",
        "--multifile=MULTIFILESTYLE",
    ]

    def test_asciidoc_file_with_multifile_single(self):
        self.given_asciidoc_file()
        self.run_command("file.adoc", "test.po", multifile="single")
        self.then_po_file_is_written()

    def test_asciidoc_file_with_multifile_onefile(self):
        self.given_asciidoc_file()
        self.run_command("file.adoc", "test.po", multifile="onefile")
        self.then_po_file_is_written()

    def test_asciidoc_directory_with_multifile_single(self):
        self.given_directory_of_asciidoc_files()
        self.run_command("adocdir", "podir", multifile="single")
        assert os.path.isdir(self.get_testfilename("podir"))
        assert os.path.isfile(self.get_testfilename("podir/file1.po"))
        assert os.path.isfile(self.get_testfilename("podir/file2.po"))
        content = self.read_testfile("podir/file1.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" not in content

    def test_asciidoc_directory_with_multifile_onefile(self):
        self.given_directory_of_asciidoc_files()
        self.run_command("adocdir", "test.po", multifile="onefile")
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" in content

    def given_asciidoc_file(self, content: str | None = None):
        if content is None:
            content = "== AsciiDoc\nYou are only coming through in waves."
        self.create_testfile("file.adoc", content)

    def test_asciidoc_with_document_header(self):
        self.given_asciidoc_file(
            content="""= Example Document
Author Name
:description: Example document

== First Section
You are only coming through in waves.
"""
        )
        self.run_command("file.adoc", "test.po")
        self.then_po_file_is_written()
        output = pofile()
        with open(self.get_testfilename("test.po"), "rb") as handle:
            output.parse(handle)
        assert len(output.units) == 3  # header + 2 units

    def given_directory_of_asciidoc_files(self):
        os.makedirs("adocdir", exist_ok=True)
        self.create_testfile("adocdir/file1.adoc", "== Heading\nContent of file 1")
        self.create_testfile("adocdir/file2.adoc", "== Heading\nContent of file 2")

    def then_po_file_is_written(self) -> str:
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "coming through" in content
        return content

    def test_comprehensive_extraction_and_translation(self):
        """Test that all translatable content is extracted and used in translation."""
        # Create a comprehensive AsciiDoc file
        adoc_content = """== Introduction

This is a paragraph with some content.

Another paragraph here.

=== Subsection

* List item one
* List item two

. Numbered item one
. Numbered item two
"""
        self.create_testfile("comprehensive.adoc", adoc_content)

        # Convert to PO
        self.run_command("comprehensive.adoc", "comprehensive.po")

        # Parse the PO file and verify all content is present
        output = pofile()
        with open(self.get_testfilename("comprehensive.po"), "rb") as handle:
            output.parse(handle)

        # Extract all msgid values (excluding header)
        msgids = [unit.source for unit in output.units if not unit.isheader()]

        # Verify all expected translatable content is present
        expected_content = [
            "Introduction",
            "This is a paragraph with some content.",
            "Another paragraph here.",
            "Subsection",
            "List item one",
            "List item two",
            "Numbered item one",
            "Numbered item two",
        ]

        for expected in expected_content:
            assert expected in msgids, (
                f"Expected content '{expected}' not found in PO file"
            )

        # Verify we have the right number of units
        assert len(msgids) == len(expected_content), (
            f"Expected {len(expected_content)} units, got {len(msgids)}"
        )
