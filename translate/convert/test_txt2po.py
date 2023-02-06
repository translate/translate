from io import BytesIO

import pytest

from translate.convert import test_convert, txt2po


class BaseTxt2POTester:
    ConverterClass = txt2po.txt2po
    Flavour = None

    def _convert(
        self,
        input_string,
        template_string=None,
        duplicate_style="msgctxt",
        encoding="utf-8",
        success_expected=True,
        no_segmentation=False,
    ):
        """Helper that converts to target format without using files."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(
            input_file,
            output_file,
            template_file,
            duplicate_style,
            encoding,
            self.Flavour,
            no_segmentation,
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    @staticmethod
    def _count_elements(po_store):
        """Helper that counts the number of non-header units."""
        assert po_store.units[0].isheader()
        return len(po_store.units) - 1


class TestTxt2PO(BaseTxt2POTester):
    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_keep_duplicates(self):
        """Check converting keeps duplicates."""
        input_string = """
Simple

Simple
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "Simple"
        assert target_store.units[1].target == ""
        assert target_store.units[2].source == "Simple"
        assert target_store.units[2].target == ""

    def test_drop_duplicates(self):
        """Check converting drops duplicates."""
        input_string = """
Simple

Simple
"""
        target_store = self._convert_to_store(input_string, duplicate_style="merge")
        assert self._count_elements(target_store) == 1
        assert target_store.units[1].source == "Simple"
        assert target_store.units[1].target == ""

    def test_simple(self):
        """Test the most basic conversion."""
        input_string = "A simple string"
        expected_output = """#: :1
msgid "A simple string"
msgstr ""
"""
        target_store = self._convert_to_store(input_string)
        assert str(target_store.units[1]) == expected_output
        assert "extracted from " in str(target_store.header())

    def test_multiple_units(self):
        """Test that we can handle txt with multiple units."""
        input_string = """First unit
Still part of first unit

Second unit is a heading
------------------------

Third unit with blank after but no more units.

"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 3

    def test_carriage_return(self):
        """Remove carriage returns from files in dos format."""
        input_string = """The rapid expansion of telecommunications infrastructure in recent years has\r
helped to bridge the digital divide to a limited extent.\r
"""
        expected_output = """The rapid expansion of telecommunications infrastructure in recent years has
helped to bridge the digital divide to a limited extent."""

        target_store = self._convert_to_store(input_string)
        assert str(target_store.units[1].source) == expected_output

    def test_merge(self):
        """Test converter doesn't merge."""
        with pytest.raises(NotImplementedError):
            self._convert_to_store("this", "cannot be", "blank", success_expected=False)

    def test_no_segmentation(self):
        """Check multiple paragraphs are extracted as a single unit."""
        input_string = """
First paragraph

Second paragraph
"""
        expected_output = input_string
        target_store = self._convert_to_store(input_string, no_segmentation=True)
        assert self._count_elements(target_store) == 1
        assert target_store.units[1].source == expected_output
        assert target_store.units[1].target == ""


class TestDoku2po(BaseTxt2POTester):
    Flavour = "dokuwiki"

    def test_convert_empty(self):
        """Test converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_keep_duplicates(self):
        """Check converting keeps duplicates."""
        input_string = """
Simple

Simple
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "Simple"
        assert target_store.units[1].target == ""
        assert target_store.units[2].source == "Simple"
        assert target_store.units[2].target == ""

    def test_drop_duplicates(self):
        """Test converting drops duplicates."""
        input_string = """
Simple

Simple
"""
        target_store = self._convert_to_store(input_string, duplicate_style="merge")
        assert self._count_elements(target_store) == 1
        assert target_store.units[1].source == "Simple"
        assert target_store.units[1].target == ""

    def test_basic(self):
        """Test basic Dokuwiki conversion."""
        input_string = """=====Heading=====

This is a wiki page.
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "Heading"
        assert target_store.units[2].source == "This is a wiki page."

    def test_bullet_list(self):
        """Test Dokuwiki bullet list conversion."""
        input_string = """  * This is a fact.
  * This is a fact.
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "This is a fact."
        assert target_store.units[1].getlocations() == [":1"]
        assert target_store.units[2].source == "This is a fact."
        assert target_store.units[2].getlocations() == [":2"]

    def test_numbered_list(self):
        """Test Dokuwiki numbered list conversion."""
        input_string = """  - This is an item.
  - This is an item.
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "This is an item."
        assert target_store.units[1].getlocations() == [":1"]
        assert target_store.units[2].source == "This is an item."
        assert target_store.units[2].getlocations() == [":2"]

    def test_spacing(self):
        """Test Dokuwiki list nesting conversion."""
        input_string = """ =====         Heading  =====
  * This is an item.
    * This is a subitem.
        * This is a tabbed item.
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 4
        assert target_store.units[1].source == "Heading"
        assert target_store.units[2].source == "This is an item."
        assert target_store.units[3].source == "This is a subitem."
        assert target_store.units[4].source == "This is a tabbed item."

    def test_merge(self):
        """Test converter doesn't merge."""
        with pytest.raises(NotImplementedError):
            self._convert_to_store("this", "cannot be", "blank", success_expected=False)


class TestTxt2POCommand(test_convert.TestConvertCommand, TestTxt2PO):
    """Tests running actual txt2po commands on files"""

    convertmodule = txt2po
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-P, --pot",
        "--duplicates",
        "--encoding",
        "--flavour",
        "--no-segmentation",
    ]
