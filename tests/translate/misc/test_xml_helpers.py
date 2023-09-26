from lxml import etree

from translate.misc.xml_helpers import reindent


class TestReindent:
    @staticmethod
    def _xmlfromstring(xmlstring):
        return etree.fromstring(xmlstring)

    @staticmethod
    def _xmltostring(xml):
        return etree.tostring(
            xml, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )

    def test_indent_four_spaces(self):
        """Test that using 4 spaces for indent yields a consistent result."""
        xmlsource = self._xmlfromstring('<root><str key="test">Test</str></root>')
        reindent(xmlsource, indent="    ")
        actual = self._xmltostring(xmlsource)
        expected = b"""<?xml version='1.0' encoding='utf-8'?>
<root>
    <str key="test">Test</str>
</root>
"""
        assert actual == expected

    def test_indent_tab(self):
        """Test that using a tab for indent yields a consistent result."""
        xmlsource = self._xmlfromstring('<root><str key="test">Test</str></root>')
        reindent(xmlsource, indent="\t")
        actual = self._xmltostring(xmlsource)
        expected = b"""<?xml version='1.0' encoding='utf-8'?>
<root>
\t<str key="test">Test</str>
</root>
"""
        assert actual == expected
