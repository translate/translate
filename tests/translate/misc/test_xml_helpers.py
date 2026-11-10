from xml.parsers.expat import ExpatError

from lxml import etree
from pytest import mark, raises

from translate.misc.xml_helpers import (
    XMLTextParser,
    extract_xml_prolog,
    getText,
    getXMLspace,
    getXMLspaceInherited,
    normalize_xml_space,
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


@mark.parametrize(
    ("source", "expected"),
    [
        (
            "<root><b>Hello</b><i> world</i></root>",
            "<root><b>Hello</b><i> world</i></root>",
        ),
        (
            "<root><b>Hello</b><empty/><i> world</i></root>",
            "<root><b>Hello</b><empty/><i> world</i></root>",
        ),
        (
            "<root><b>Hello </b>world</root>",
            "<root><b>Hello </b>world</root>",
        ),
        (
            "<root><b>Hello </b> world</root>",
            "<root><b>Hello </b>world</root>",
        ),
        (
            "<root> <b> world</b></root>",
            "<root><b>world</b></root>",
        ),
        (
            "<root> <outer> <inner> world</inner></outer></root>",
            "<root><outer><inner>world</inner></outer></root>",
        ),
        (
            '<root xml:space="preserve">Hello<child xml:space="default">  world  </child></root>',
            '<root xml:space="preserve">Hello<child xml:space="default"> world</child></root>',
        ),
        (
            "<root>Hello<child> world</child></root>",
            "<root>Hello<child> world</child></root>",
        ),
        (
            "<root><child>Hello<grandchild> world</grandchild></child></root>",
            "<root><child>Hello<grandchild> world</grandchild></child></root>",
        ),
        (
            "<root> first <child> second </child></root>",
            "<root>first <child>second</child></root>",
        ),
        (
            "<root><child><grandchild> \ttext\n </grandchild></child></root>",
            "<root><child><grandchild>text</grandchild></child></root>",
        ),
        (
            '<root> first <child xml:space="preserve">  second  </child></root>',
            '<root>first <child xml:space="preserve">  second  </child></root>',
        ),
    ],
)
def test_normalize_xml_space_children(source: str, expected: str) -> None:
    root = parse_xml(source)

    normalize_xml_space(root, "default", remove_start=True)

    assert etree.tostring(root, encoding="unicode") == expected


def test_normalize_xml_space_subtree_with_tail() -> None:
    root = parse_xml("<root><child> text </child>\n  </root>")

    normalize_xml_space(root[0], "default", remove_start=True)

    assert root[0].text == "text"
    assert root[0].tail == " "


@mark.parametrize(
    ("parent_space", "child_space", "expected_tail"),
    [
        ("preserve", "default", " \t after "),
        ("default", "preserve", " after "),
    ],
)
def test_normalize_xml_space_tail_uses_parent_space(
    parent_space: str, child_space: str, expected_tail: str
) -> None:
    root = parse_xml(
        f'<root xml:space="{parent_space}"><parent>'
        f'<child xml:space="{child_space}"> text </child> \t after </parent></root>'
    )
    child = root[0][0]

    normalize_xml_space(child, "default", remove_start=True)

    assert child.text == (" text " if child_space == "preserve" else "text")
    assert child.tail == expected_tail


@mark.parametrize(
    "content",
    [
        "Hello &word; again",
        "&word; &word;",
        "<child>Hello </child>&word;",
        "Hello &word;<child> again</child>",
    ],
)
def test_normalize_xml_space_preserves_entity_boundaries(content: str) -> None:
    root = parse_xml(
        f'<!DOCTYPE root [<!ENTITY word "expanded">]><root>{content}</root>'
    )

    normalize_xml_space(root, "default", remove_start=True)

    assert etree.tostring(root, encoding="unicode") == f"<root>{content}</root>"


@mark.parametrize("remove_start", [False, True])
@mark.parametrize(
    "source",
    [
        "<root>  <first> </first><second> text </second></root>",
        "<root>Hello <empty/> <child> world </child> again </root>",
        '<root xml:space="preserve"> \t<child xml:space="default">  word </child> text </root>',
        '<!DOCTYPE root [<!ENTITY word "expanded">]><root> &word; <child> again </child></root>',
        "<root> Hello<!--note--> \t<?note value?> world </root>",
    ],
)
def test_normalize_xml_space_is_idempotent(source: str, remove_start: bool) -> None:
    root = parse_xml(source)
    normalize_xml_space(root, "default", remove_start=remove_start)
    normalized = etree.tostring(root)

    normalize_xml_space(root, "default", remove_start=remove_start)

    assert etree.tostring(root) == normalized


@mark.parametrize(
    ("source", "expected"),
    [
        (
            "<root> \tHello<child> world </child></root>",
            "<root> Hello<child> world</child></root>",
        ),
        (
            "<root><child> \tHello</child></root>",
            "<root><child> Hello</child></root>",
        ),
    ],
)
def test_normalize_xml_space_retains_leading_space(source: str, expected: str) -> None:
    root = parse_xml(source)

    normalize_xml_space(root, "default", remove_start=False)

    assert etree.tostring(root, encoding="unicode") == expected


@mark.parametrize("space", ["\u00a0", "\u202f"])
@mark.parametrize("remove_start", [False, True])
def test_normalize_xml_space_preserves_nonbreaking_spaces(
    space: str, remove_start: bool
) -> None:
    root = parse_xml(f"<root>{space}Hello<child> {space}world{space} </child></root>")

    normalize_xml_space(root, "default", remove_start=remove_start)

    assert etree.tostring(root, encoding="unicode") == (
        f"<root>{space}Hello<child> {space}world{space}</child></root>"
    )


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
