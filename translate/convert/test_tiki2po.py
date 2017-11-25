# -*- coding: utf-8 -*-

# tiki2po unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01

from io import BytesIO

from translate.convert import test_convert, tiki2po


class TestTiki2Po(object):

    def _convert(self, format_input_source, format_template_source=None,
                 include_unused=False):
        """Helper that converts format to target format without files."""
        input_file = BytesIO(format_input_source)
        output_file = BytesIO()
        template_file = None
        if format_template_source:
            template_file = BytesIO(format_template_source)
        result = tiki2po.converttiki(input_file, output_file, template_file,
                                     include_unused)
        assert result == 1
        return output_file.getvalue().decode('utf-8')

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        input_file = BytesIO()
        output_file = BytesIO()
        result = tiki2po.converttiki(input_file, output_file)
        assert result == 0
        assert output_file.getvalue().decode('utf-8') == ''

    def test_converttiki_defaults(self):
        input_source = """
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
"""
        output = self._convert(input_source)
        assert '#: translated' in output
        assert 'msgid "zero_source"' in output
        assert "one_source" not in output

    def test_converttiki_includeunused(self):
        input_source = """
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
"""
        output = self._convert(input_source, include_unused=True)
        assert '#: translated' in output
        assert 'msgid "zero_source"' in output
        assert '#: unused' in output
        assert 'msgid "one_source"' in output


class TestTiki2PoCommand(test_convert.TestConvertCommand, TestTiki2Po):
    """Tests running actual tiki2po commands on files"""
    convertmodule = tiki2po
    defaultoptions = {}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "--include-unused")
