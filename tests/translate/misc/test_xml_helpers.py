from lxml import etree

from translate.misc.xml_helpers import (
    XMLTextParser,
    getText,
    getXMLspace,
    getXMLspaceInherited,
    parse_xml,
    reindent,
)


class UppercaseXMLTextParser(XMLTextParser):
    def process_string(self, content: str) -> tuple[str, bool, bool]:
        return content.upper(), False, False


def test_xml_text_parser_preserves_markup() -> None:
    source = (
        "<root>plain<é title='Bob&apos;s'>inner</é>"
        "<![CDATA[Don't]]><!-- Don't --><?test Don't?>&brand;</root>"
    )

    assert UppercaseXMLTextParser(source).parse() == (
        "PLAIN<é title='Bob&apos;s'>INNER</é>"
        "<![CDATA[Don't]]><!-- Don't --><?test Don't?>&brand;"
    )


def test_xml_space_inheritance() -> None:
    root = parse_xml(
        '<root xml:space="preserve"><parent xml:space="default">'
        '<child/><sibling xml:space="preserve"/>'
        "</parent></root>"
    )
    child = root[0][0]
    sibling = root[0][1]

    assert getXMLspace(child) is None
    assert getXMLspaceInherited(child) == "default"
    assert getXMLspaceInherited(sibling) == "preserve"
    assert getXMLspaceInherited(etree.Element("detached"), "fallback") == "fallback"


def test_gettext_uses_inherited_xml_space() -> None:
    root = parse_xml(
        '<root xml:space="preserve"><preserved> File  1 </preserved>'
        '<normalized xml:space="default"> File  2 </normalized></root>'
    )

    assert getText(root[0], "default") == " File  1 "
    assert getText(root[1], "preserve") == "File 2"


class TestReindent:
    @staticmethod
    def _xmlfromstring(xmlstring):
        return parse_xml(xmlstring)

    @staticmethod
    def _xmltostring(xml):
        return etree.tostring(
            xml, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )

    def test_indent_four_spaces(self) -> None:
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

    def test_indent_tab(self) -> None:
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
