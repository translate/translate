from io import BytesIO

import pytest

from translate.convert import test_convert, yaml2po


class TestYAML2PO:
    ConverterClass = yaml2po.yaml2po

    def _convert(
        self,
        input_string,
        template_string=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
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
            input_file, output_file, template_file, blank_msgstr, duplicate_style
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    @staticmethod
    def _single_element(po_store):
        """Helper to check PO file has one non-header unit, and return it."""
        assert len(po_store.units) == 2
        assert po_store.units[0].isheader()
        return po_store.units[1]

    @staticmethod
    def _count_elements(po_store):
        """Helper that counts the number of non-header units."""
        assert po_store.units[0].isheader()
        return len(po_store.units) - 1

    def test_convert_empty_YAML(self):
        """Check converting empty YAML returns no output."""
        assert self._convert_to_string("", success_expected=False) == ""

    def test_simple_output(self):
        """Check that a simple single entry YAML converts valid PO output."""
        input_string = 'key: "Hello, World!"'
        expected_output = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        assert expected_output in self._convert_to_string(input_string)

    def test_simple(self):
        """Check that a simple single entry YAML converts to a PO unit."""
        input_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.getlocations() == ["key"]
        assert target_unit.source == "Hello, World!"
        assert target_unit.target == ""

    def test_nested(self):
        """Check converting nested YAML."""
        input_string = """
foo:
    bar: bar
    '': bar2
    baz:
        boo: booo


eggs: spam
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 4
        assert target_store.units[1].getlocations() == ["foo->bar"]
        assert target_store.units[1].source == "bar"
        assert target_store.units[1].target == ""
        assert target_store.units[2].getlocations() == ["foo->"]
        assert target_store.units[2].source == "bar2"
        assert target_store.units[2].target == ""
        assert target_store.units[3].getlocations() == ["foo->baz->boo"]
        assert target_store.units[3].source == "booo"
        assert target_store.units[3].target == ""
        assert target_store.units[4].getlocations() == ["eggs"]
        assert target_store.units[4].source == "spam"
        assert target_store.units[4].target == ""

    @pytest.mark.xfail(reason="This is invalid YAML document")
    def test_no_duplicates(self):
        """Check converting drops duplicates."""
        input_string = """
foo: bar
foo: baz
"""
        target_store = self._convert_to_store(input_string)
        assert self._count_elements(target_store) == 1
        assert target_store.units[1].getlocations() == ["foo"]
        assert target_store.units[1].source == "baz"
        assert target_store.units[1].target == ""

    def test_convert_with_template(self):
        """Check converting a simple single-string YAML with newer template."""
        input_string = 'key: "Ola mundo!"'
        template_string = """key: "Hello, World!"
foo: What's up?
"""
        target_store = self._convert_to_store(input_string, template_string)
        assert self._count_elements(target_store) == 2
        assert target_store.units[1].getlocations() == ["key"]
        assert target_store.units[1].source == "Hello, World!"
        assert target_store.units[1].target == "Ola mundo!"
        assert target_store.units[2].getlocations() == ["foo"]
        assert target_store.units[2].source == "What's up?"
        assert target_store.units[2].target == ""


class TestYAML2POCommand(test_convert.TestConvertCommand, TestYAML2PO):
    """Tests running actual yaml2po commands on files"""

    convertmodule = yaml2po
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
        "--duplicates=DUPLICATESTYLE",
    ]
