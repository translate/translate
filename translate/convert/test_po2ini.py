from io import BytesIO

from pytest import importorskip, raises

from translate.convert import po2ini, test_convert


importorskip("iniparse")


class TestPO2Ini:
    ConverterClass = po2ini.po2ini

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        dialect="default",
        success_expected=True,
    ):
        """Helper that converts to target format without using files."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(
            input_file,
            output_file,
            template_file,
            include_fuzzy,
            output_threshold,
            dialect,
        )
        assert converter.run() == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_no_templates(self):
        """Check converter doesn't allow to pass no templates."""
        with raises(ValueError):
            self._convert_to_string("")

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        input_string = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        template_string = """[section]
prop=value
"""
        expected_output = """[section]
prop=waarde
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_space_preservation(self):
        """check that we preserve any spacing in ini files when merging"""
        input_string = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        template_string = """[section]
prop  =  value
"""
        expected_output = """[section]
prop  =  waarde
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        input_string = r"""#: [section]accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""
"""
        template_string = """[section]
accesskey-accept=
"""
        expected_output = """[section]
accesskey-accept=
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        input_string = """#: [section]prop
#, fuzzy
msgid "value"
msgstr "waarde"
"""
        template_string = """[section]
prop=value
"""
        expected_output = """[section]
prop=value
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no ini values that we copy the template"""
        input_string = ""
        template_string = """# A comment
"""
        expected_output = template_string
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_empty_value(self):
        """test that we handle an value in translation that is missing in the template"""
        input_string = """#: [section]key
msgctxt "key"
msgid ""
msgstr "translated"
"""
        template_string = """[section]
key =
"""
        expected_output = """[section]
key =translated
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_dialects_inno(self):
        """test that we output correctly for Inno files."""
        input_string = r"""#: [section]prop
msgid "value\tvalue2\n"
msgstr "ṽḁḽṻḝ\tṽḁḽṻḝ2\n"
"""
        template_string = """[section]
prop  =  value%tvalue%n
"""
        expected_output = """[section]
prop  =  ṽḁḽṻḝ%tṽḁḽṻḝ2%n
"""
        assert expected_output == self._convert_to_string(
            input_string, template_string, dialect="inno"
        )

    def test_misaligned_files(self):
        """Check misaligned files conversions uses the template version."""
        input_string = """#: [section]key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = """[section]
different=Other string
"""
        expected_output = """[section]
different=Other string
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """#: [section]prop
msgid "value"
msgstr ""
"""
        template_string = """[section]
prop=value
"""
        expected_output = ""
        # Input completion is 0% so with a 70% threshold it should not output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70, success_expected=False
        )
        assert output == expected_output

    def test_convert_completion_above_threshold(self):
        """Check no conversion if input completion is above threshold."""
        input_string = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        template_string = """[section]
prop=value
"""
        expected_output = """[section]
prop=waarde
"""
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert output == expected_output

    def test_no_fuzzy(self):
        """Check that a simple fuzzy PO converts to a untranslated target."""
        input_string = """#: [section]prop
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = """[section]
prop=Hello, World!
"""
        expected_output = """[section]
prop=Hello, World!
"""
        assert expected_output == self._convert_to_string(
            input_string, template_string, include_fuzzy=False
        )

    def test_allow_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated target."""
        input_string = """#: [section]prop
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = """[section]
prop=Hello, World!
"""
        expected_output = """[section]
prop=Ola mundo!
"""
        assert expected_output == self._convert_to_string(
            input_string, template_string, include_fuzzy=True
        )

    def test_merging_missing_source(self):
        """Check merging when template locations are missing in source."""
        input_string = """#: [section]missing
msgid "value"
msgstr "valor"
"""
        template_string = """[section]
key=other
"""
        expected_output = template_string
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_merging_repeated_locations(self):
        """Check merging when files have repeated locations."""
        input_string = """#: [section]key
msgid "first"
msgstr "primeiro"

#: [section]key
msgid "second"
msgstr "segundo"
"""
        template_string = """[section]
key=first
key=second
"""
        expected_output = """[section]
key=first
key=primeiro
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

        template_string = """[section]
key=first

[section]
key=second
"""
        expected_output = """[section]
key=first

[section]
key=primeiro
"""
        assert expected_output == self._convert_to_string(input_string, template_string)


class TestPO2IniCommand(test_convert.TestConvertCommand, TestPO2Ini):
    """Tests running actual po2ini commands on files"""

    convertmodule = po2ini
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]
