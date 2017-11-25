# -*- coding: utf-8 -*-

# po2tiki unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01

from translate.convert import po2tiki, test_convert
from translate.misc import wStringIO


class TestPo2Tiki(object):

    def _convert(self, format_input_source, format_template_source=None):
        """Helper that converts format to target format without files."""
        input_file = wStringIO.StringIO(format_input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if format_template_source:
            template_file = wStringIO.StringIO(format_template_source)
        result = po2tiki.run_converter(input_file, output_file, template_file)
        assert result == 1
        return output_file.getvalue().decode('utf-8')

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        input_file = wStringIO.StringIO()
        output_file = wStringIO.StringIO()
        result = po2tiki.run_converter(input_file, output_file)
        assert result == 0
        assert output_file.getvalue().decode('utf-8') == ''

    def test_convert(self):
        """Check converting simple file."""
        input_source = """
#: translated
msgid "zero_source"
msgstr "zero_target"

#: unused
msgid "one_source"
msgstr "one_target"
"""
        output = self._convert(input_source)
        assert '"one_source" => "one_target",' in output
        assert '"zero_source" => "zero_target",' in output

    def test_convert_marked_untranslated(self):
        """Check convert marked as untranslated keeps translation."""
        input_source = """
#: untranslated
msgid "Do not translate"
msgstr "It is translated"
"""
        output = self._convert(input_source)
        assert '"Do not translate" => "It is translated",' in output


class TestPo2TikiCommand(test_convert.TestConvertCommand, TestPo2Tiki):
    """Tests running actual po2tiki commands on files"""
    convertmodule = po2tiki
    defaultoptions = {}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
