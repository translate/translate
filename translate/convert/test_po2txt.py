# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from translate.convert import po2txt, test_convert
from translate.misc import wStringIO


class TestPO2Txt(object):

    ConverterClass = po2txt.po2txt

    def _convert(self, input_string, template_string=None, include_fuzzy=False,
                 output_threshold=None, encoding='utf-8', wrap=None,
                 success_expected=True):
        """Helper that converts to target format without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(input_file, output_file, template_file,
                                        include_fuzzy, output_threshold,
                                        encoding, wrap)
        assert converter.run() == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode('utf-8')

    def test_basic(self):
        """test basic conversion"""
        posource = """msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        txttemplate = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert self._convert_to_string(posource, txttemplate) == expected_output

    def test_nonascii(self):
        """test conversion with non-ascii text"""
        posource = """msgid "Heading"
msgstr "Opskrif"

msgid "File content"
msgstr "Lêerinhoud"
"""
        txttemplate = """Heading

File content"""
        expected_output = """Opskrif

Lêerinhoud"""
        assert self._convert_to_string(posource, txttemplate) == expected_output

    def test_blank_handling(self):
        """check that we discard blank messages"""
        posource = """msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr ""
"""
        txttemplate = """Heading

Body text"""
        expected_output = """Opskrif

Body text"""
        assert self._convert_to_string(posource) == expected_output
        assert self._convert_to_string(posource, txttemplate) == expected_output

    def test_fuzzy_handling(self):
        """check that we handle fuzzy message correctly"""
        posource = """#, fuzzy
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        txttemplate = """Heading

Body text"""
        expected_output = """Heading

Lyfteks"""
        assert self._convert_to_string(posource) == expected_output
        assert self._convert_to_string(posource, txttemplate) == expected_output

    def test_obsolete_ignore(self):
        """check that we handle obsolete message by not using it"""
        posource = """
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"

#~ msgid "Obsolete"
#~ msgstr "Oud"
"""
        txttemplate = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert self._convert_to_string(posource) == expected_output
        assert self._convert_to_string(posource, txttemplate) == expected_output

    def test_header_ignore(self):
        """check that we ignore headers"""
        posource = """
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        txttemplate = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert self._convert_to_string(posource) == expected_output
        assert self._convert_to_string(posource, txttemplate) == expected_output

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
