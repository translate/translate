from io import BytesIO

import pytest

from translate.convert import po2yaml, test_convert


class TestPO2YAML:
    ConverterClass = po2yaml.po2yaml

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
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
            input_file, output_file, template_file, include_fuzzy, output_threshold
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty_PO(self):
        """Check converting empty PO returns no output."""
        assert self._convert_to_string("", "{}") == "{}\n"

    def test_convert_no_templates(self):
        """Check converter doesn't allow to pass no templates."""
        with pytest.raises(ValueError):
            self._convert_to_store("")

    def test_simple_output(self):
        """Check that a simple single entry PO converts valid YAML output."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
        expected_output = """key: Hello, World!
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_simple(self):
        """Check that a simple single entry PO converts to a YAML unit."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Hello, World!"
        assert target_unit.target == "Hello, World!"

    def test_translated(self):
        """Check that a simple translated PO converts to a translated YAML."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Ola mundo!"
        assert target_unit.target == "Ola mundo!"

    def test_no_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_string = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Hello, World!"
        assert target_unit.target == "Hello, World!"

    def test_allow_fuzzy(self):
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_string = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(
            input_string, template_string, include_fuzzy=True
        )
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Ola mundo!"
        assert target_unit.target == "Ola mundo!"

    def test_nested(self):
        """Check converting to nested YAML."""
        input_string = """
#: foo->bar
msgid "bar"
msgstr ""

#: foo->baz->boo
msgid "booo"
msgstr ""

#: foo->
msgid "bar2"
msgstr ""

#: eggs
msgid "spam"
msgstr ""
"""
        template_string = """
foo:
    bar: bar
    '': bar2
    baz:
        boo: booo
eggs: spam
"""
        target_store = self._convert_to_store(input_string, template_string)
        assert len(target_store.units) == 4
        assert target_store.units[0].getlocations() == ["foo->bar"]
        assert target_store.units[0].source == "bar"
        assert target_store.units[0].target == "bar"
        assert target_store.units[1].getlocations() == ["foo->"]
        assert target_store.units[1].source == "bar2"
        assert target_store.units[1].target == "bar2"
        assert target_store.units[2].getlocations() == ["foo->baz->boo"]
        assert target_store.units[2].source == "booo"
        assert target_store.units[2].target == "booo"
        assert target_store.units[3].getlocations() == ["eggs"]
        assert target_store.units[3].source == "spam"
        assert target_store.units[3].target == "spam"

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
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
        template_string = 'key: "Hello, World!"'
        expected_output = """key: Ola mundo!
"""
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert output == expected_output


class TestPO2YAMLCommand(test_convert.TestConvertCommand, TestPO2YAML):
    """Tests running actual po2yaml commands on files"""

    convertmodule = po2yaml
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]
