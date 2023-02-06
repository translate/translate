# po2tiki unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01
from io import BytesIO

from translate.convert import po2tiki, test_convert


class TestPo2Tiki:
    ConverterClass = po2tiki.po2tiki

    def _convert(self, input_string, template_string=None, success_expected=True):
        """Helper that converts to target format without using files."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(input_file, output_file, template_file)
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_convert(self):
        """Check converting simple file."""
        input_string = """
#: translated
msgid "zero_source"
msgstr "zero_target"

#: unused
msgid "one_source"
msgstr "one_target"
"""
        output = self._convert_to_string(input_string)
        assert '"one_source" => "one_target",' in output
        assert '"zero_source" => "zero_target",' in output

    def test_convert_marked_untranslated(self):
        """Check convert marked as untranslated keeps translation."""
        input_string = """
#: untranslated
msgid "Do not translate"
msgstr "It is translated"
"""
        output = self._convert_to_string(input_string)
        assert '"Do not translate" => "It is translated",' in output


class TestPo2TikiCommand(test_convert.TestConvertCommand, TestPo2Tiki):
    """Tests running actual po2tiki commands on files"""

    convertmodule = po2tiki
    defaultoptions = {}
