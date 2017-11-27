# -*- coding: utf-8 -*-

from translate.convert import po2l20n, test_convert
from translate.misc import wStringIO


class TestPO2L20n(object):

    def merge2l20n(self, po_source, l20n_source):
        """Helper that converts to target format string without using files."""
        inputfile = wStringIO.StringIO(po_source)
        templatefile = wStringIO.StringIO(l20n_source)
        convertor = po2l20n.po2l20n(inputfile, None, templatefile)
        outputfile = wStringIO.StringIO()
        convertor.convert_store().serialize(outputfile)
        output_l20n = outputfile.getvalue()
        return output_l20n.decode('utf8')

    def test_merging_simple(self):
        """Check the simplest case of merging a translation."""
        input_string = """#: l20n
msgid "value"
msgstr "waarde"
"""
        template_string = """l20n = value
"""
        expected_output = """l20n = waarde
"""
        assert expected_output == self.merge2l20n(input_string,
                                                  template_string)

    def test_merging_untranslated(self):
        """check the simplest case of merging an untranslated unit"""
        input_string = """#: l20n
msgid "value"
msgstr ""
"""
        template_string = """l20n = value
"""
        expected_output = template_string
        assert expected_output == self.merge2l20n(input_string,
                                                  template_string)


class TestPO2L20nCommand(test_convert.TestConvertCommand, TestPO2L20n):
    """Tests running actual po2prop commands on files"""
    convertmodule = po2l20n
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--nofuzzy", last=True)
