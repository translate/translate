# tiki2po unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01

from io import BytesIO

from translate.convert import test_convert, tiki2po


class TestTiki2Po:
    ConverterClass = tiki2po.tiki2po

    def _convert(
        self,
        input_string,
        template_string=None,
        include_unused=False,
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
            input_file, output_file, template_file, include_unused
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_converttiki_defaults(self):
        input_string = """
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
"""
        output = self._convert_to_string(input_string)
        assert "#: translated" in output
        assert 'msgid "zero_source"' in output
        assert "one_source" not in output

    def test_converttiki_includeunused(self):
        input_string = """
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
"""
        output = self._convert_to_string(input_string, include_unused=True)
        assert "#: translated" in output
        assert 'msgid "zero_source"' in output
        assert "#: unused" in output
        assert 'msgid "one_source"' in output


class TestTiki2PoCommand(test_convert.TestConvertCommand, TestTiki2Po):
    """Tests running actual tiki2po commands on files"""

    convertmodule = tiki2po
    defaultoptions = {}
    expected_options = [
        "--include-unused",
    ]
