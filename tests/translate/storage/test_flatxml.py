from io import BytesIO

from pytest import raises

from translate.storage import flatxml, test_monolingual


class TestFlatXMLUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = flatxml.FlatXMLUnit


class TestFlatXMLFile(test_monolingual.TestMonolingualStore):
    StoreClass = flatxml.FlatXMLFile

    @staticmethod
    def _store_to_string(store):
        outputfile = BytesIO()
        store.serialize(outputfile)
        return outputfile.getvalue().decode("utf-8")

    @staticmethod
    def _encoded_file(string, encoding="utf-8"):
        xmldecl = '<?xml version="1.0" encoding="%s"?>' % encoding
        stringfile = BytesIO((xmldecl + string).encode())
        return stringfile

    def test_root_config_detect(self):
        """Test that parser fails on inconsistent root name configuration"""
        xmlsource = '<root><str key="test">Test</str></root>'

        with raises(AssertionError):
            self.StoreClass(xmlsource, root_name="different")

    def test_value_config_detect(self):
        """Test that parser fails on inconsistent value name configuration"""
        xmlsource = '<root><str key="test">Test</str></root>'

        with raises(AssertionError):
            self.StoreClass(xmlsource, value_name="different")

    def test_key_config_detect(self):
        """Test that parser fails on inconsistent key name configuration"""
        xmlsource = '<root><str key="test">Test</str></root>'

        with raises(AssertionError):
            self.StoreClass(xmlsource, key_name="different")

    def test_value_config_mixed_ok(self):
        """Test that parser leaves non-value entries alone"""
        xmlsource = """<root>
            <str key="test">Test</str>
            <not-a-value key="ignored">this entry does not matter</not-a-value>
        </root>"""

        store = self.StoreClass(xmlsource)
        assert store.findid("ignored") is None
        assert store.findid("test")
        assert len(list(store.root.iterchildren("not-a-value"))) == 1

    def test_namespace_config_detect(self):
        """Test that parser fails on inconsistent root namespace configuration.

        This test triggers at root level, and yields a similar message as
        the test against the root element name.
        """
        xmlsource = '<root><str key="test">Test</str></root>'

        with raises(AssertionError):
            self.StoreClass(xmlsource, namespace="different")

    def test_indent_four_spaces(self):
        """Test that using 4 spaces for indent yields a consistent result."""
        xmlsource = self._encoded_file('<root><str key="test">Test</str></root>')
        store = self.StoreClass(xmlsource, indent_chars="    ")
        actual = self._store_to_string(store)
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
    <str key="test">Test</str>
</root>
"""
        assert actual == expected

    def test_indent_tab(self):
        """Test that using a tab for indent yields a consistent result."""
        xmlsource = self._encoded_file('<root><str key="test">Test</str></root>')
        store = self.StoreClass(xmlsource, indent_chars="\t")
        actual = self._store_to_string(store)
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root>
\t<str key="test">Test</str>
</root>
"""
        assert actual == expected

    def test_indent_none_linearizes(self):
        """Test that using None as indent yields a linearized result."""
        xmlsource = self._encoded_file('<root>\n<str key="test">Test</str>\n</root>')
        store = self.StoreClass(xmlsource, indent_chars=None)
        actual = self._store_to_string(store)
        # no newlines or indent for the elements...
        # ...but trailing EOL to satisfy VCS
        expected = """<?xml version='1.0' encoding='UTF-8'?>
<root><str key="test">Test</str></root>
"""
        assert actual == expected
