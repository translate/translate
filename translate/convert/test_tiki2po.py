# -*- coding: utf-8 -*-

# tiki2po unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01

from io import BytesIO

from translate.convert import test_convert, tiki2po


class TestTiki2Po(object):

    def test_converttiki_defaults(self):
        inputfile = b"""
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
        """
        outputfile = BytesIO()
        tiki2po.converttiki(inputfile, outputfile)

        output = outputfile.getvalue().decode('utf-8')

        assert '#: translated' in output
        assert 'msgid "zero_source"' in output
        assert "one_source" not in output

    def test_converttiki_includeunused(self):
        inputfile = b"""
"zero_source" => "zero_target",
// ### Start of unused words
"one_source" => "one_target",
// ### end of unused words
        """
        outputfile = BytesIO()
        tiki2po.converttiki(inputfile, outputfile, includeunused=True)

        output = outputfile.getvalue().decode('utf-8')

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
