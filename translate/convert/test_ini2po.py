from io import BytesIO

from pytest import importorskip

from translate.convert import ini2po, test_convert


importorskip("iniparse")


class TestIni2PO:
    ConverterClass = ini2po.ini2po

    def _convert(
        self,
        input_string,
        template_string=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
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
            blank_msgstr,
            duplicate_style,
            dialect,
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty_file(self):
        """Check converting empty INI returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_convert_no_translation(self):
        """Check converting INI with no translatable text returns no output."""
        output = self._convert_to_string("[section]", success_expected=False)
        assert output == ""

    def test_convert_simple(self):
        """Check the simplest case of converting a translation."""
        input_string = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_no_duplicates(self):
        """Check converting drops duplicates."""
        input_string = """[section]
key=value
key=different
"""
        expected_output = """#: [section]key
msgid "different"
msgstr ""
"""
        output = self._convert_to_string(input_string, duplicate_style="msgctxt")
        assert expected_output in output
        output = self._convert_to_string(input_string, duplicate_style="merge")
        assert expected_output in output

    def test_merge_simple(self):
        """Check the simplest case of merging a translation."""
        input_string = """[section]
key=valor
"""
        template_string = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr "valor"
"""
        output = self._convert_to_string(input_string, template_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_merge_misaligned_files(self):
        """Check merging two files that are not aligned."""
        input_string = """[section]
other=missing
"""
        template_string = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr ""
"""
        assert expected_output in self._convert_to_string(input_string, template_string)

    def test_merge_blank_msgstr(self):
        """Check merging two files returns output without translations."""
        input_string = """[section]
key=valor
"""
        template_string = """[section]
key=value
"""
        expected_output = """#: [section]key
msgid "value"
msgstr ""
"""
        assert expected_output in self._convert_to_string(
            input_string, template_string, blank_msgstr=True
        )

    def test_dialects_inno(self):
        """Check that we output correctly for Inno files."""
        input_string = """[section]
prop  =  ṽḁḽṻḝ%tṽḁḽṻḝ2%n
"""
        template_string = """[section]
prop  =  value%tvalue2%n
"""
        expected_output = r"""#: [section]prop
msgid "value\tvalue2\n"
msgstr "ṽḁḽṻḝ\tṽḁḽṻḝ2\n"
"""
        output = self._convert_to_string(input_string, template_string, dialect="inno")
        assert expected_output in output


class TestIni2POCommand(test_convert.TestConvertCommand, TestIni2PO):
    """Tests running actual ini2po commands on files"""

    convertmodule = ini2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-P, --pot",
        "--duplicates=DUPLICATESTYLE",
    ]
