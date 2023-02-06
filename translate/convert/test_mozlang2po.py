from io import BytesIO

import pytest

from translate.convert import mozlang2po, test_convert


class TestLang2PO:
    ConverterClass = mozlang2po.lang2po

    def _convert(
        self,
        input_string,
        template_string=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
        encoding="utf-8",
        success_expected=True,
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
            blank_msgstr,
            duplicate_style,
            encoding,
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
    def _single_element(po_store):
        """Helper to check store has one non-header unit, and return it."""
        assert len(po_store.units) == 2
        assert po_store.units[0].isheader()
        return po_store.units[1]

    @staticmethod
    def _count_elements(po_store):
        """Helper that counts the number of non-header units."""
        assert po_store.units[0].isheader()
        return len(po_store.units) - 1

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_simple_string(self):
        """Check that a simple lang string converts correctly."""
        input_string = """;One
Een
"""
        expected_output = """
msgid "One"
msgstr "Een"
"""
        assert expected_output in self._convert_to_string(input_string)

    def test_merge(self):
        """Check converter doesn't merge."""
        with pytest.raises(NotImplementedError):
            self._convert_to_store("this", "cannot be", "blank", success_expected=False)

    def test_simple_entry(self):
        """Check that a simple lang entry converts properly to a po entry."""
        input_string = """;One
Een
"""
        target_store = self._convert_to_store(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.source == "One"
        assert target_unit.target == "Een"

    def test_simple_comment(self):
        """Check handling of simple comments."""
        input_string = """# Comment
;One
Een
"""
        target_store = self._convert_to_store(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.source == "One"
        assert target_unit.target == "Een"
        assert target_unit.getnotes() == "Comment"

    def test_meta_tags(self):
        """Check meta tags are not extracted."""
        input_string = """## tag
# Comment
;One
Een
"""
        target_store = self._convert_to_store(input_string)
        target_unit = self._single_element(target_store)
        assert "tag" not in target_unit.getnotes()

    def test_keep_duplicates(self):
        """Check converting keeps duplicates."""
        input_string = """
;One
Un

;One
Dous
"""
        target_store = self._convert_to_store(input_string, duplicate_style="msgctxt")
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].source == "One"
        assert target_store.units[1].target == "Un"
        assert target_store.units[2].source == "One"
        assert target_store.units[2].target == "Dous"

    def test_drop_duplicates(self):
        """Check converting drops duplicates."""
        input_string = """
;One
Un

;One
Dous
"""
        target_store = self._convert_to_store(input_string, duplicate_style="merge")
        assert self._count_elements(target_store) == 1
        assert target_store.units[1].source == "One"
        assert target_store.units[1].target == "Un"


class TestLang2POCommand(test_convert.TestConvertCommand, TestLang2PO):
    """Tests running actual lang2po commands on files"""

    convertmodule = mozlang2po
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-P, --pot",
        "--encoding=ENCODING",
        "--duplicates=DUPLICATESTYLE",
    ]
