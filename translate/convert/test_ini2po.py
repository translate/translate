# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pytest import importorskip

from translate.convert import ini2po, test_convert
from translate.misc import wStringIO


importorskip("iniparse")


class TestIni2PO(object):

    def _convert(self, input_source, template_source=None, blank_msgstr=False,
                 duplicate_style="msgctxt", dialect="default"):
        """Helper that converts format input to PO output without files."""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_source:
            template_file = wStringIO.StringIO(template_source)
        result = ini2po.run_converter(input_file, output_file, template_file,
                                      blank_msgstr, duplicate_style, dialect)
        assert result == 1
        return output_file.getvalue()

    def test_convert_empty_file(self):
        """Check converting empty INI returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = None
        result = ini2po.run_converter(input_file, output_file, template_file)
        assert result == 0
        assert output_file.getvalue() == ''

    def test_convert_simple(self):
        """Check the simplest case of converting a translation."""
        input_source = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr ""
"""
        output = self._convert(input_source)
        assert expected_output in output
        assert "extracted from " in output

    def test_no_duplicates(self):
        """Check converting drops duplicates."""
        input_source = """[section]
key=value
key=different
"""
        expected_output = """#: [section]key
msgid "different"
msgstr ""
"""
        assert expected_output in self._convert(input_source,
                                                duplicate_style="msgctxt")
        assert expected_output in self._convert(input_source,
                                                duplicate_style="merge")

    def test_merge_simple(self):
        """Check the simplest case of merging a translation."""
        input_source = """[section]
key=valor
"""
        template_source = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr "valor"
"""
        output = self._convert(input_source, template_source)
        assert expected_output in output
        assert "extracted from " in output


class TestIni2POCommand(test_convert.TestConvertCommand, TestIni2PO):
    """Tests running actual ini2po commands on files"""
    convertmodule = ini2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--duplicates=DUPLICATESTYLE")
