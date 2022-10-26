"""Tests converting flat XML files to Gettext PO localization files"""

from io import BytesIO

from translate.convert import flatxml2po, test_convert


class TestFlatXML2PO:
    @staticmethod
    def _convert(xmlstring, templatestring=None, **kwargs):
        """Helper that converts xml source to po target without requiring files"""
        inputfile = BytesIO(xmlstring.encode())
        templatefile = None
        if templatestring:
            templatefile = BytesIO(templatestring.encode())
        outputfile = BytesIO()
        converter = flatxml2po.flatxml2po(inputfile, outputfile, templatefile, **kwargs)
        converter.run()
        return converter.target_store, outputfile

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    @staticmethod
    def _do_assert_store(actual):
        """Asserts whether the passed actual store contains two assumed units:
        'one' => 'One'
        'two' => 'Two'
        (plus a header present by default)
        """
        assert actual.units[0].isheader()
        assert len(actual.units) == 3
        one = actual.findid("one")
        assert one
        assert one.target == "One"
        two = actual.findid("two")
        assert two
        assert two.target == "Two"

    def test_defaults(self):
        """Test a conversion with default values."""
        xmlstring = """<root>
            <str key="one">One</str>
            <str key="two">Two</str>
        </root>
        """
        actual = self._convert_to_store(xmlstring)
        self._do_assert_store(actual)

    def test_root_name(self):
        """Test a conversion with different root name."""
        xmlstring = """<strings>
            <str key="one">One</str>
            <str key="two">Two</str>
        </strings>
        """
        actual = self._convert_to_store(xmlstring, root="strings")
        self._do_assert_store(actual)

    def test_value_name(self):
        """Test a conversion with different value name."""
        xmlstring = """<root>
            <entry key="one">One</entry>
            <entry key="two">Two</entry>
        </root>
        """
        actual = self._convert_to_store(xmlstring, value="entry")
        self._do_assert_store(actual)

    def test_key(self):
        """Test a conversion with different key name."""
        xmlstring = """<root>
            <str name="one">One</str>
            <str name="two">Two</str>
        </root>
        """
        actual = self._convert_to_store(xmlstring, key="name")
        self._do_assert_store(actual)

    def test_default_namespace(self):
        """Test a conversion with a default namespace."""
        xmlstring = """<root xmlns="urn:tt:test">
            <str key="one">One</str>
            <str key="two">Two</str>
        </root>
        """
        actual = self._convert_to_store(xmlstring, ns="urn:tt:test")
        self._do_assert_store(actual)

    def test_namespace_prefix(self):
        """Test a conversion with a namespace prefix."""
        xmlstring = """<t:root xmlns:t="urn:tt:test">
            <t:str key="one">One</t:str>
            <t:str key="two">Two</t:str>
        </t:root>
        """
        actual = self._convert_to_store(xmlstring, ns="urn:tt:test")
        self._do_assert_store(actual)

    def test_all_parameters(self):
        """Test a conversion with all parameters."""
        xmlstring = """<fancy xmlns="urn:tt:test">
            <stuff dude="one">One</stuff>
            <stuff dude="two">Two</stuff>
        </fancy>
        """
        actual = self._convert_to_store(
            xmlstring, root="fancy", value="stuff", key="dude", ns="urn:tt:test"
        )
        self._do_assert_store(actual)

    def test_empty_file_is_empty_store(self):
        """Test a conversion that starts with an empty file.

        This must not trigger the element name validation
        or cause other issues. An empty store is expected.
        """
        xmlstring = "<root/>"
        actual = self._convert_to_store(xmlstring)
        assert actual
        assert actual.units[0].isheader()
        assert len(actual.units) == 1


class TestFlatXML2POCommand(test_convert.TestConvertCommand):
    """Tests running actual flatxml2po commands on files"""

    convertmodule = flatxml2po

    expected_options = [
        "-r ROOT, --root=ROOT",
        "-v VALUE, --value=VALUE",
        "-k KEY, --key=KEY",
        "-n NS, --namespace=NS",
    ]
