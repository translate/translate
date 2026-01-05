from __future__ import annotations

import os

from translate.convert import md2po
from translate.storage.po import pofile

from . import test_convert


class TestMD2PO(test_convert.TestConvertCommand):
    convertmodule = md2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates=DUPLICATESTYLE",
        "--multifile=MULTIFILESTYLE",
    ]

    def test_markdown_file_with_multifile_single(self) -> None:
        self.given_markdown_file()
        self.run_command("file.md", "test.po", multifile="single")
        self.then_po_file_is_written()

    def test_markdown_file_with_multifile_onefile(self) -> None:
        self.given_markdown_file()
        self.run_command("file.md", "test.po", multifile="onefile")
        self.then_po_file_is_written()

    def test_markdown_directory_with_multifile_single(self) -> None:
        self.given_directory_of_markdown_files()
        self.run_command("mddir", "podir", multifile="single")
        assert os.path.isdir(self.get_testfilename("podir"))
        assert os.path.isfile(self.get_testfilename("podir/file1.po"))
        assert os.path.isfile(self.get_testfilename("podir/file2.po"))
        content = self.read_testfile("podir/file1.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" not in content

    def test_markdown_directory_with_multifile_onefile(self) -> None:
        self.given_directory_of_markdown_files()
        self.run_command("mddir", "test.po", multifile="onefile")
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "Content of file 1" in content
        assert "Content of file 2" in content

    def given_markdown_file(self, content: str | None = None) -> None:
        if content is None:
            content = "# Markdown\nYou are only coming through in waves."
        self.create_testfile("file.md", content)

    def test_markdown_frontmatter(self) -> None:
        self.given_markdown_file(
            content="""---
date: 2024-02-02T04:14:54-08:00
draft: false
params:
  author: John Smith
title: Example
weight: 10
---

# Markdown
You are only coming through in waves.
"""
        )
        self.run_command("file.md", "test.po")
        self.then_po_file_is_written()
        output = pofile()
        with open(self.get_testfilename("test.po")) as handle:
            print(handle.read())
        with open(self.get_testfilename("test.po"), "rb") as handle:
            output.parse(handle)
        assert len(output.units) == 3

    def given_directory_of_markdown_files(self) -> None:
        os.makedirs("mddir", exist_ok=True)
        self.create_testfile("mddir/file1.md", "# Heading\nContent of file 1")
        self.create_testfile("mddir/file2.md", "# Heading\nContent of file 2")

    def then_po_file_is_written(self) -> str:
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        assert "coming through" in content
        return content

    def test_markdown_translation_ignore_sections(self) -> None:
        """Test that content between translate:off and translate:on is not extracted."""
        self.given_markdown_file(
            content="""# Welcome

This text will be translated.

<!-- translate:off -->

```python
def example():
    return "This code won't be extracted"
```

[link-ref]: https://example.com "Link Title"

<!-- translate:on -->

This text will also be translated.
"""
        )
        self.run_command("file.md", "test.po")
        assert os.path.isfile(self.get_testfilename("test.po"))
        content = self.read_testfile("test.po").decode()
        # Verify that translatable content is extracted
        assert "Welcome" in content
        assert "This text will be translated." in content
        assert "This text will also be translated." in content
        # Verify that ignored content is NOT extracted
        assert "This code won't be extracted" not in content
        assert "link-ref" not in content
        assert "Link Title" not in content
