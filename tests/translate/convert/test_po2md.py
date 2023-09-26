import os

from translate.convert import po2md

from . import test_convert


class TestPO2MD(test_convert.TestConvertCommand):
    convertmodule = po2md
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
        "-m MAXLENGTH, --maxlinelength=MAXLENGTH",
    ]

    def test_single_markdown_file_with_single_po(self):
        self.given_markdown_file()
        self.given_translation_file()
        self.run_command("translation.po", "out.md", template="file.md")
        self.then_translated_markdown_file_is_written()

    def test_directory_of_markdown_files_with_single_po(self):
        self.given_directory_of_markdown_files()
        self.given_translation_file()
        self.run_command("translation.po", "testout", template="mddir")
        self.then_directory_of_translated_markdown_files_is_written()

    def test_directory_of_markdown_files_and_directory_of_po_files(self):
        self.given_directory_of_markdown_files()
        self.given_directory_of_po_files()
        self.run_command("podir", "testout", template="mddir")
        self.then_directory_of_translated_markdown_files_is_written()

    def given_markdown_file(self):
        self.create_testfile(
            "file.md", "# Markdown\nYou are only coming through in waves."
        )

    def given_directory_of_markdown_files(self):
        os.makedirs("mddir", exist_ok=True)
        self.create_testfile("mddir/file1.md", "# Heading\nContent of file 1")
        self.create_testfile("mddir/file2.md", "# Heading\nContent of file 2")

    def given_translation_file(self, filename="translation.po"):
        lines = [
            "#: 'ref'",
            'msgid "You are only coming through in waves."',
            'msgstr "Översatt innehåll"',
            "",
            "#: 'ref'",
            'msgid "Content of file 1"',
            'msgstr "Innehåll i fil 1"',
            "",
            "#: 'ref'",
            'msgid "Content of file 2"',
            'msgstr "Innehåll i fil 2"',
        ]
        self.create_testfile(filename, "\n".join(lines))

    def given_directory_of_po_files(self):
        os.makedirs("podir", exist_ok=True)
        for filename in ["podir/file1.po", "podir/file2.po"]:
            self.given_translation_file(filename=filename)

    def then_translated_markdown_file_is_written(self):
        assert os.path.isfile(self.get_testfilename("out.md"))
        content = self.read_testfile("out.md").decode()
        assert "Översatt innehåll" in content

    def then_directory_of_translated_markdown_files_is_written(self):
        assert os.path.isdir(self.get_testfilename("testout"))
        assert os.path.isfile(self.get_testfilename("testout/file1.md"))
        assert os.path.isfile(self.get_testfilename("testout/file2.md"))
        content = self.read_testfile("testout/file1.md").decode()
        assert "Innehåll i fil 1" in content
        assert "Innehåll i fil 2" not in content
