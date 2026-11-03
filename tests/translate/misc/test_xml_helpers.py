from xml.parsers.expat import ExpatError

from lxml import etree
from pytest import mark, raises

from translate.misc.xml_helpers import (
    XMLTextParser,
    extract_xml_prolog,
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


@mark.parametrize(
    "prolog",
    [
        b"",
        b"\xef\xbb\xbf",
        b'<?xml version="1.1" encoding="UTF-8"?>\r\n\r\n',
        b"<!-- <root/> -->\n<?test <root/>?>\n",
        b'<!DOCTYPE root SYSTEM "file:///nonexistent-external.dtd">\n',
        b'<!DOCTYPE root [<!ENTITY example "<root/>">]>\n',
        "<!-- é -->\n".encode(),
    ],
)
def test_extract_xml_prolog(prolog) -> None:
    assert extract_xml_prolog(prolog + b"<root>content</root>") == prolog


def test_extract_xml_prolog_stops_at_root() -> None:
    # Document validation belongs to the caller, not the prolog extractor.
    assert (
        extract_xml_prolog(b"<!-- header -->\n<root>invalid &") == b"<!-- header -->\n"
    )


def test_extract_xml_prolog_invalid() -> None:
    with raises(ExpatError):
        extract_xml_prolog(b"<!-- unfinished comment")
