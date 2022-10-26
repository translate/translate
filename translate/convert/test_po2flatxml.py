"""Tests converting Gettext PO localization files to flat XML files"""

from io import BytesIO

from translate.convert import po2flatxml, test_convert


class TestPO2FlatXML:
    postring = """msgid "one"
msgstr "One"

msgid "two"
msgstr "Two"
"""

    @staticmethod
    def _convert(postring, templatestring=None, **kwargs):
        """Helper that converts po source to xml target without requiring files"""
        inputfile = BytesIO(postring.encode())
        templatefile = None
        if templatestring:
            templatefile = BytesIO(templatestring.encode())
        outputfile = BytesIO()
        converter = po2flatxml.po2flatxml(inputfile, outputfile, templatefile, **kwargs)
        converter.run()
        return converter.target_store, outputfile

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_defaults(self):
        """Test a conversion with default values."""
        actual = self._convert_to_string(self.postring)
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
  <str key="one">One</str>
  <str key="two">Two</str>
</root>
"""
        assert actual == expected

    def test_root_name(self):
        """Test a conversion with different root name."""
        actual = self._convert_to_string(self.postring, root="strings")
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<strings>
  <str key="one">One</str>
  <str key="two">Two</str>
</strings>
"""
        assert actual == expected

    def test_value_name(self):
        """Test a conversion with different value name."""
        actual = self._convert_to_string(self.postring, value="entry")
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
  <entry key="one">One</entry>
  <entry key="two">Two</entry>
</root>
"""
        assert actual == expected

    def test_key(self):
        """Test a conversion with different key name."""
        actual = self._convert_to_string(self.postring, key="name")
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
  <str name="one">One</str>
  <str name="two">Two</str>
</root>
"""
        assert actual == expected

    def test_default_namespace(self):
        """Test a conversion with a default namespace.

        This conversion requires a template that specifies the namespace
        as default namespace; otherwise it will be generated.
        """
        templatestring = """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="urn:tt:test"/>"""
        actual = self._convert_to_string(
            self.postring, templatestring=templatestring, ns="urn:tt:test"
        )
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root xmlns="urn:tt:test">
  <str key="one">One</str>
  <str key="two">Two</str>
</root>
"""
        assert actual == expected

    def test_namespace_prefix(self):
        """Test a conversion with a namespace prefix."""
        actual = self._convert_to_string(self.postring, ns="urn:tt:test")
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:root xmlns:ns0="urn:tt:test">
  <ns0:str key="one">One</ns0:str>
  <ns0:str key="two">Two</ns0:str>
</ns0:root>
"""
        assert actual == expected

    def test_indent_eight(self):
        """Test a conversion with an indent width of 8."""
        actual = self._convert_to_string(self.postring, indent=8)
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
        <str key="one">One</str>
        <str key="two">Two</str>
</root>
"""
        assert actual == expected

    def test_noindent(self):
        """Test a conversion with an indent width 0."""
        actual = self._convert_to_string(self.postring, indent=0)
        # no indent here...
        # ...except for a trailing EOL for VCS
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root><str key="one">One</str><str key="two">Two</str></root>
"""
        assert actual == expected


class TestPO2FlatXMLCommand(test_convert.TestConvertCommand):
    """Tests running actual po2flatxml commands on files"""

    convertmodule = po2flatxml
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-r ROOT, --root=ROOT",
        "-v VALUE, --value=VALUE",
        "-k KEY, --key=KEY",
        "-n NS, --namespace=NS",
        "-w INDENT, --indent=INDENT",
    ]
