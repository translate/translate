# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from translate.convert import po2yaml, test_convert
from translate.misc import wStringIO


class TestPO2YAML(object):

    ConverterClass = po2yaml.po2yaml

    def _convert(self, po_input_source, format_template_source=None,
                 include_fuzzy=False, output_threshold=None):
        """Helper that converts PO to format without files."""
        input_file = wStringIO.StringIO(po_input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if format_template_source:
            template_file = wStringIO.StringIO(format_template_source)
        converter = self.ConverterClass(input_file, output_file, template_file,
                                        include_fuzzy, output_threshold)
        assert converter.run() == 1
        return converter.target_store, output_file

    def format2po_file(self, po_input_source, format_template_source=None,
                       include_fuzzy=False, output_threshold=None):
        """Helper that converts PO source to format store without files."""
        return self._convert(po_input_source, format_template_source,
                             include_fuzzy, output_threshold)[0]

    def format2po_text(self, po_input_source, format_template_source=None,
                       include_fuzzy=False, output_threshold=None):
        """Helper that converts PO source to format output without files."""
        return self._convert(po_input_source, format_template_source,
                             include_fuzzy, output_threshold)[1].getvalue()

    def test_convert_empty_PO(self):
        """Check converting empty PO returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO()
        converter = self.ConverterClass(input_file, output_file, template_file)
        assert converter.run() == 1
        assert converter.target_store.isempty()
        assert output_file.getvalue().decode('utf-8') == '{}\n'

    def test_convert_no_templates(self):
        """Check converter doesn't allow to pass no templates."""
        input_file = wStringIO.StringIO()
        output_file = wStringIO.StringIO()
        template_file = None
        with pytest.raises(ValueError):
            self.ConverterClass(input_file, output_file, template_file)

    def test_simple_output(self):
        """Check that a simple single entry PO converts valid YAML output."""
        input_source = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_source = 'key: "Hello, World!"'
        expected_output = '''key: Hello, World!
'''
        assert (expected_output ==
                self.format2po_text(input_source,
                                    template_source).decode('utf-8'))

    def test_simple(self):
        """Check that a simple single entry PO converts to a YAML unit."""
        input_source = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_source = 'key: "Hello, World!"'
        yaml_file = self.format2po_file(input_source, template_source)
        yaml_unit = yaml_file.units[0]
        assert len(yaml_file.units) == 1
        assert yaml_unit.getid() == "key"
        assert yaml_unit.source == "Hello, World!"
        assert yaml_unit.target == "Hello, World!"

    def test_translated(self):
        """Check that a simple translated PO converts to a translated YAML."""
        input_source = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = 'key: "Hello, World!"'
        yaml_file = self.format2po_file(input_source, template_source)
        yaml_unit = yaml_file.units[0]
        assert len(yaml_file.units) == 1
        assert yaml_unit.getid() == "key"
        assert yaml_unit.source == "Ola mundo!"
        assert yaml_unit.target == "Ola mundo!"

    def test_no_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_source = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = 'key: "Hello, World!"'
        yaml_file = self.format2po_file(input_source, template_source)
        yaml_unit = yaml_file.units[0]
        assert len(yaml_file.units) == 1
        assert yaml_unit.getid() == "key"
        assert yaml_unit.source == "Hello, World!"
        assert yaml_unit.target == "Hello, World!"

    def test_allow_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_source = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = 'key: "Hello, World!"'
        yaml_file = self.format2po_file(input_source, template_source,
                                        include_fuzzy=True)
        yaml_unit = yaml_file.units[0]
        assert len(yaml_file.units) == 1
        assert yaml_unit.getid() == "key"
        assert yaml_unit.source == "Ola mundo!"
        assert yaml_unit.target == "Ola mundo!"

    def test_nested(self):
        """Check converting to nested YAML."""
        input_source = """
#: foo->bar
msgid "bar"
msgstr ""

#: foo->baz->boo
msgid "booo"
msgstr ""

#: eggs
msgid "spam"
msgstr ""
"""
        template_source = '''
foo:
    bar: bar
    baz:
        boo: booo
eggs: spam
'''
        yaml_file = self.format2po_file(input_source, template_source)
        assert len(yaml_file.units) == 3
        assert yaml_file.units[0].getlocations() == ['foo->bar']
        assert yaml_file.units[0].source == "bar"
        assert yaml_file.units[0].target == "bar"
        assert yaml_file.units[1].getlocations() == ['foo->baz->boo']
        assert yaml_file.units[1].source == "booo"
        assert yaml_file.units[1].target == "booo"
        assert yaml_file.units[2].getlocations() == ['eggs']
        assert yaml_file.units[2].source == "spam"
        assert yaml_file.units[2].target == "spam"


class TestPO2YAMLCommand(test_convert.TestConvertCommand, TestPO2YAML):
    """Tests running actual po2yaml commands on files"""
    convertmodule = po2yaml
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy")
