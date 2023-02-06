from io import BytesIO

from translate.convert import po2mozlang, test_convert


class TestPO2Lang:
    ConverterClass = po2mozlang.po2lang

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        mark_active=True,
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
            mark_active,
        )
        assert converter.run() == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_simple(self):
        """Check the simplest conversion case."""
        input_string = """#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Target


"""
        assert expected_output == self._convert_to_string(
            input_string, mark_active=False
        )

    def test_comment(self):
        """Simple # comments"""
        input_string = """#. Comment
#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """# Comment
;Source
Target


"""
        assert expected_output == self._convert_to_string(
            input_string, mark_active=False
        )

    def test_ok_marker(self):
        """The {ok} marker"""
        input_string = """#: prop
msgid "Same"
msgstr "Same"
"""
        expected_output = """;Same
Same {ok}


"""
        assert expected_output == self._convert_to_string(
            input_string, mark_active=False
        )

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """#: prop
msgid "Source"
msgstr ""
"""
        expected_output = ""
        # Input completion is 0% so with a 70% threshold it should not output.
        output = self._convert_to_string(
            input_string, output_threshold=70, mark_active=False, success_expected=False
        )
        assert output == expected_output

    def test_convert_completion_above_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Target


"""
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, output_threshold=70, mark_active=False, success_expected=True
        )
        assert output == expected_output

    def test_convert_skip_non_translatable_input(self):
        """Check no conversion skips non-translatable units in input."""
        input_string = """
msgid ""
msgstr ""

#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Target


"""
        assert expected_output == self._convert_to_string(
            input_string, mark_active=False
        )

    def test_no_fuzzy(self):
        """Check fuzzy units are not converted."""
        input_string = """
#: prop
#, fuzzy
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Source


"""
        assert expected_output == self._convert_to_string(
            input_string, include_fuzzy=False, mark_active=False
        )

    def test_allow_fuzzy(self):
        """Check fuzzy units are converted."""
        input_string = """
#: prop
#, fuzzy
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Target


"""
        assert expected_output == self._convert_to_string(
            input_string, include_fuzzy=True, mark_active=False
        )

    def test_mark_active(self):
        """Check output is marked as active."""
        input_string = """
#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """## active ##
;Source
Target


"""
        assert expected_output == self._convert_to_string(
            input_string, mark_active=True
        )


class TestPO2LangCommand(test_convert.TestConvertCommand, TestPO2Lang):
    """Tests running actual po2prop commands on files"""

    convertmodule = po2mozlang
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--mark-active",
        "--nofuzzy",
    ]
