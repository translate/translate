# -*- coding: utf-8 -*-

# po2tiki unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2008-12-01

from io import BytesIO

from translate.convert import po2tiki, test_convert


class TestPo2Tiki(object):

    def test_convertpo(self):
        inputfile = b"""
#: translated
msgid "zero_source"
msgstr "zero_target"

#: unused
msgid "one_source"
msgstr "one_target"
        """
        outputfile = BytesIO()
        po2tiki.convertpo(inputfile, outputfile)

        output = outputfile.getvalue().decode('utf-8')

        assert '"one_source" => "one_target",' in output
        assert '"zero_source" => "zero_target",' in output


class TestPo2TikiCommand(test_convert.TestConvertCommand, TestPo2Tiki):
    """Tests running actual po2tiki commands on files"""
    convertmodule = po2tiki
    defaultoptions = {}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
