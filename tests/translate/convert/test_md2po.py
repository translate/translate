import os

from translate.convert import md2po

from . import test_convert


class TestMD2PO(test_convert.TestConvertCommand):
    convertmodule = md2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates=DUPLICATESTYLE",
        "--multifile=MULTIFILESTYLE",
    ]

    def test_markdown_file_with_multifile_single(self):
        self.given_markdown_file()
        self.run_command("file.md", "test.po", multifile="single")
        self.then_po_file_is_written()

    def test_markdown_file_with_multifile_onefile(self):
        self.given_markdown_file()
        self.run_command("file.md", "test.po", multifile="onefile")
        self.then_po_file_is_written()

    def test_markdown_directory_with_multifile_single(self):
        self.given_directory_of_markdown_files()
        self.run_command("mddir", "podir", multifile="single")
        assert os.path.isdir(self.get_testfilename("podir"))
        assert os.path.isfile(self.get_testfilename("podir/file1.po"))
        assert os.path.isfile(self.get_testfilename("podir/file2.po"))
        content = self.read_testfile("podir/file1.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" not in content

    def test_markdown_directory_with_multifile_onefile(self):
        self.given_directory_of_markdown_files()
        self.run_command("mddir", "test.po", multifile="onefile")
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" in content

    def given_markdown_file(self):
        self.create_testfile(
            "file.md", "# Markdown\nYou are only coming through in waves."
        )

    def given_directory_of_markdown_files(self):
        os.makedirs("mddir", exist_ok=True)
        self.create_testfile("mddir/file1.md", "# Heading\nContent of file 1")
        self.create_testfile("mddir/file2.md", "# Heading\nContent of file 2")

    def then_po_file_is_written(self):
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "coming through" in content
