# -*- coding: utf-8 -*-

from translate.convert import po2txt, test_convert
from translate.misc import wStringIO


class TestPO2Txt(object):

    def po2txt(self, posource, txttemplate=None):
        """helper that converts po source to txt source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        print(inputfile.getvalue())
        outputfile = wStringIO.StringIO()
        if txttemplate:
            templatefile = wStringIO.StringIO(txttemplate)
        else:
            templatefile = None
        assert po2txt.run_converter(inputfile, outputfile, templatefile)
        print(outputfile.getvalue())
        return outputfile.getvalue().decode('utf-8')

    def test_basic(self):
        """test basic conversion"""
        txttemplate = "Heading\n\nBody text"
        posource = 'msgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "Body text"\nmsgstr "Lyfteks"\n'
        assert self.po2txt(posource, txttemplate) == "Opskrif\n\nLyfteks"

    def test_nonascii(self):
        """test conversion with non-ascii text"""
        txttemplate = "Heading\n\nFile content"
        posource = u'msgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "File content"\nmsgstr "Lêerinhoud"\n'
        assert self.po2txt(posource, txttemplate) == u"Opskrif\n\nLêerinhoud"

    def test_blank_handling(self):
        """check that we discard blank messages"""
        txttemplate = "Heading\n\nBody text"
        posource = 'msgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "Body text"\nmsgstr ""\n'
        assert self.po2txt(posource) == "Opskrif\n\nBody text"
        assert self.po2txt(posource, txttemplate) == "Opskrif\n\nBody text"

    def test_fuzzy_handling(self):
        """check that we handle fuzzy message correctly"""
        txttemplate = "Heading\n\nBody text"
        posource = '#, fuzzy\nmsgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "Body text"\nmsgstr "Lyfteks"\n'
        assert self.po2txt(posource) == "Heading\n\nLyfteks"
        assert self.po2txt(posource, txttemplate) == "Heading\n\nLyfteks"

    def test_obsolete_ignore(self):
        """check that we handle obsolete message by not using it"""
        txttemplate = """Heading

Body text"""
        posource = """
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"

#~ msgid "Obsolete"
#~ msgstr "Oud"
"""
        expected_output = """Opskrif

Lyfteks"""
        assert self.po2txt(posource) == expected_output
        assert self.po2txt(posource, txttemplate) == expected_output

    def test_header_ignore(self):
        """check that we ignore headers"""
        txttemplate = """Heading

Body text"""
        posource = """
msgid ""
msgstr "POT-Creation-Date: 2006-11-11 11:11+0000\n"

msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        expected_output = """Opskrif

Lyfteks"""
        assert self.po2txt(posource) == expected_output
        assert self.po2txt(posource, txttemplate) == expected_output

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_source = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_source = "Hello, World!"
        expected_output = ""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO(template_source)
        # Input completion is 0% so with a 70% threshold it should not output.
        result = po2txt.po2txt(input_file, output_file, template_file,
                               output_threshold=70).run()
        assert result == 0
        assert output_file.getvalue().decode('utf-8') == expected_output

    def test_convert_completion_above_threshold(self):
        """Check no conversion if input completion is above threshold."""
        input_source = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = "Hello, World!"
        expected_output = "Ola mundo!"
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO(template_source)
        # Input completion is 100% so with a 70% threshold it should output.
        result = po2txt.po2txt(input_file, output_file, template_file,
                               output_threshold=70).run()
        assert result == 1
        assert output_file.getvalue().decode('utf-8') == expected_output


class TestPO2TxtCommand(test_convert.TestConvertCommand, TestPO2Txt):
    """Tests running actual po2txt commands on files"""
    convertmodule = po2txt
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy")
        options = self.help_check(options, "--encoding")
        options = self.help_check(options, "-w WRAP, --wrap=WRAP", last=True)
