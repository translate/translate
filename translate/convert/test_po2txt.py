from io import BytesIO

from translate.convert import po2txt, test_convert


class TestPO2Txt:
    ConverterClass = po2txt.po2txt

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        encoding="utf-8",
        wrap=None,
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
            encoding,
            wrap,
        )
        assert converter.run() == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_basic(self):
        """test basic conversion"""
        input_string = """msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        template_string = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_nonascii(self):
        """test conversion with non-ascii text"""
        input_string = """msgid "Heading"
msgstr "Opskrif"

msgid "File content"
msgstr "Lêerinhoud"
"""
        template_string = """Heading

File content"""
        expected_output = """Opskrif

Lêerinhoud"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_blank_handling(self):
        """check that we discard blank messages"""
        input_string = """msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr ""
"""
        template_string = """Heading

Body text"""
        expected_output = """Opskrif

Body text"""
        assert expected_output == self._convert_to_string(input_string)
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_fuzzy_handling(self):
        """check that we handle fuzzy message correctly"""
        input_string = """#, fuzzy
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        template_string = """Heading

Body text"""
        expected_output = """Heading

Lyfteks"""
        assert expected_output == self._convert_to_string(input_string)
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_obsolete_ignore(self):
        """check that we handle obsolete message by not using it"""
        input_string = """
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"

#~ msgid "Obsolete"
#~ msgstr "Oud"
"""
        template_string = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert expected_output == self._convert_to_string(input_string)
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_header_ignore(self):
        """check that we ignore headers"""
        input_string = """
msgid "Heading"
msgstr "Opskrif"

msgid "Body text"
msgstr "Lyfteks"
"""
        template_string = """Heading

Body text"""
        expected_output = """Opskrif

Lyfteks"""
        assert expected_output == self._convert_to_string(input_string)
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = "Hello, World!"
        expected_output = ""
        # Input completion is 0% so with a 70% threshold it should not output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70, success_expected=False
        )
        assert output == expected_output

    def test_convert_completion_above_threshold(self):
        """Check no conversion if input completion is above threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = "Hello, World!"
        expected_output = "Ola mundo!"
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert output == expected_output


class TestPO2TxtCommand(test_convert.TestConvertCommand, TestPO2Txt):
    """Tests running actual po2txt commands on files"""

    convertmodule = po2txt
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
        "--encoding",
        "-w WRAP, --wrap=WRAP",
    ]
