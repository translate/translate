# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from translate.convert import yaml2po, test_convert
from translate.misc import wStringIO


class TestYAML2PO(object):

    ConverterClass = yaml2po.yaml2po

    def _convert(self, input_string, template_string=None, blank_msgstr=False,
                 duplicate_style="msgctxt", success_expected=True):
        """Helper that converts to target format without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(input_file, output_file, template_file,
                                        blank_msgstr, duplicate_style)
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode('utf-8')

    def _single_element(self, po_file):
        """Helper to check PO file has one non-header unit, and return it."""
        assert len(po_file.units) == 2
        assert po_file.units[0].isheader()
        return po_file.units[1]

    def _count_elements(self, po_file):
        """Helper that counts the number of non-header units."""
        assert po_file.units[0].isheader()
        return len(po_file.units) - 1

    def test_convert_empty_YAML(self):
        """Check converting empty YAML returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = None
        converter = self.ConverterClass(input_file, output_file, template_file)
        assert converter.run() == 0
        assert converter.target_store.isempty()
        assert output_file.getvalue().decode('utf-8') == ''

    def test_simple_output(self):
        """Check that a simple single entry YAML converts valid PO output."""
        input_source = 'key: "Hello, World!"'
        expected_unit_output = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        assert expected_unit_output in self._convert_to_string(input_source)

    def test_simple(self):
        """Check that a simple single entry YAML converts to a PO unit."""
        input_source = 'key: "Hello, World!"'
        po_file = self._convert_to_store(input_source)
        po_unit = self._single_element(po_file)
        assert po_unit.getlocations() == ["key"]
        assert po_unit.source == "Hello, World!"
        assert po_unit.target == ""

    def test_nested(self):
        """Check converting nested YAML."""
        input_source = '''
foo:
    bar: bar
    baz:
        boo: booo


eggs: spam
'''
        po_file = self._convert_to_store(input_source)
        assert self._count_elements(po_file) == 3
        assert po_file.units[1].getlocations() == ['foo->bar']
        assert po_file.units[1].source == "bar"
        assert po_file.units[1].target == ""
        assert po_file.units[2].getlocations() == ['foo->baz->boo']
        assert po_file.units[2].source == "booo"
        assert po_file.units[2].target == ""
        assert po_file.units[3].getlocations() == ['eggs']
        assert po_file.units[3].source == "spam"
        assert po_file.units[3].target == ""

    def test_no_duplicates(self):
        """Check converting drops duplicates."""
        input_source = '''
foo: bar
foo: baz
'''
        po_file = self._convert_to_store(input_source)
        assert self._count_elements(po_file) == 1
        assert po_file.units[1].getlocations() == ['foo']
        assert po_file.units[1].source == "baz"
        assert po_file.units[1].target == ""

    def test_convert_with_template(self):
        """Check converting a simple single-string YAML with newer template."""
        input_source = 'key: "Ola mundo!"'
        template_source = '''key: "Hello, World!"
foo: What's up?
'''
        po_file = self._convert_to_store(input_source, template_source)
        assert self._count_elements(po_file) == 2
        assert po_file.units[1].getlocations() == ['key']
        assert po_file.units[1].source == "Hello, World!"
        assert po_file.units[1].target == "Ola mundo!"
        assert po_file.units[2].getlocations() == ['foo']
        assert po_file.units[2].source == "What's up?"
        assert po_file.units[2].target == ""


class TestYAML2POCommand(test_convert.TestConvertCommand, TestYAML2PO):
    """Tests running actual yaml2po commands on files"""
    convertmodule = yaml2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
