# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pytest import importorskip, raises

from translate.convert import po2ini, test_convert
from translate.misc import wStringIO
from translate.storage import po


importorskip("iniparse")


class TestPO2Ini(object):

    def _convert(self, po_input_source, format_template_source=None,
                 include_fuzzy=False, dialect="default"):
        """Helper that converts PO to format without files."""
        input_file = wStringIO.StringIO(po_input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if format_template_source:
            template_file = wStringIO.StringIO(format_template_source)
        result = po2ini.run_converter(input_file, output_file, template_file,
                                      includefuzzy=include_fuzzy,
                                      dialect=dialect)
        assert result == 1
        return output_file.getvalue()

    def test_convert_no_templates(self):
        """Check converter doesn't allow to pass no templates."""
        input_file = None
        template_file = None
        with raises(ValueError):
            self._convert(input_file, template_file)

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop=value
"""
        iniexpected = """[section]
prop=waarde
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_space_preservation(self):
        """check that we preserve any spacing in ini files when merging"""
        posource = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop  =  value
"""
        iniexpected = """[section]
prop  =  waarde
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r"""#: [section]accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""
"""
        initemplate = """[section]
accesskey-accept=
"""
        iniexpected = """[section]
accesskey-accept=
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = """#: [section]prop
#, fuzzy
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop=value
"""
        iniexpected = """[section]
prop=value
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no ini values that we copy the template"""
        posource = ""
        initemplate = """# A comment
"""
        iniexpected = initemplate
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_empty_value(self):
        """test that we handle an value in translation that is missing in the template"""
        posource = """#: [section]key
msgctxt "key"
msgid ""
msgstr "translated"
"""
        initemplate = """[section]
key =
"""
        iniexpected = """[section]
key =translated
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_dialects_inno(self):
        """test that we output correctly for Inno files."""
        posource = r"""#: [section]prop
msgid "value\tvalue2\n"
msgstr "ṽḁḽṻḝ\tṽḁḽṻḝ2\n"
"""
        initemplate = """[section]
prop  =  value%tvalue%n
"""
        iniexpected = """[section]
prop  =  ṽḁḽṻḝ%tṽḁḽṻḝ2%n
"""
        inifile = self._convert(posource, initemplate, dialect="inno")
        assert inifile.decode('utf-8') == iniexpected

    def test_misaligned_files(self):
        """Check misaligned files conversions uses the template version."""
        input_source = """#: [section]key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = """[section]
different=Other string
"""
        expected_output = """[section]
different=Other string
"""
        output = self._convert(input_source, template_source)
        assert output == expected_output

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_source = """#: [section]prop
msgid "value"
msgstr ""
"""
        template_source = """[section]
prop=value
"""
        expected_output = ""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO(template_source)
        # Input completion is 0% so with a 70% threshold it should not output.
        result = po2ini.run_converter(input_file, output_file, template_file,
                                      outputthreshold=70)
        assert result == 0
        assert output_file.getvalue() == expected_output

    def test_convert_completion_above_threshold(self):
        """Check no conversion if input completion is above threshold."""
        input_source = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        template_source = """[section]
prop=value
"""
        expected_output = """[section]
prop=waarde
"""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO(template_source)
        # Input completion is 100% so with a 70% threshold it should output.
        result = po2ini.run_converter(input_file, output_file, template_file,
                                      outputthreshold=70)
        assert result == 1
        assert output_file.getvalue() == expected_output

    def test_no_fuzzy(self):
        """Check that a simple fuzzy PO converts to a untranslated target."""
        input_source = """#: [section]prop
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = """[section]
prop=Hello, World!
"""
        expected_output = """[section]
prop=Hello, World!
"""
        output = self._convert(input_source, template_source,
                               include_fuzzy=False)
        assert output == expected_output

    def test_allow_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated target."""
        input_source = """#: [section]prop
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_source = """[section]
prop=Hello, World!
"""
        expected_output = """[section]
prop=Ola mundo!
"""
        output = self._convert(input_source, template_source,
                               include_fuzzy=True)
        assert output == expected_output

    def test_merging_repeated_locations(self):
        """Check merging when files have repeated locations."""
        input_source = """#: [section]key
msgid "first"
msgstr "primeiro"

#: [section]key
msgid "second"
msgstr "segundo"
"""
        template_source = """[section]
key=first
key=second
"""
        expected_output = """[section]
key=first
key=primeiro
"""
        output = self._convert(input_source, template_source)
        assert output == expected_output

        template_source = """[section]
key=first

[section]
key=second
"""
        expected_output = """[section]
key=first

[section]
key=primeiro
"""
        output = self._convert(input_source, template_source)
        assert output == expected_output


class TestPO2IniCommand(test_convert.TestConvertCommand, TestPO2Ini):
    """Tests running actual po2ini commands on files"""
    convertmodule = po2ini
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)
