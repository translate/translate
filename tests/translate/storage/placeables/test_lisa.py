#
# Copyright 2006-2007 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.
#

from copy import copy

from lxml import etree
from pytest import mark, raises

from translate.misc.xml_helpers import parse_xml
from translate.storage.placeables import StringElem, lisa
from translate.storage.placeables.xliff import Bx, Entity, Ex, G, UnknownXML, X


def test_xml_to_strelem() -> None:
    source = parse_xml("<source>a</source>")
    elem = lisa.xml_to_strelem(source)
    assert elem == StringElem("a")

    source = parse_xml('<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.sub == [StringElem("a"), X(id="foo[1]/bar[1]/baz[1]")]

    source = parse_xml('<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.sub == [StringElem("a"), X(id="foo[1]/bar[1]/baz[1]"), StringElem("é")]

    source = parse_xml(
        '<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>é</source>'
    )
    elem = lisa.xml_to_strelem(source)
    assert elem.sub == [
        StringElem("a"),
        G(
            id="foo[2]/bar[2]/baz[2]",
            sub=[StringElem("b"), X(id="foo[1]/bar[1]/baz[1]"), StringElem("c")],
        ),
        StringElem("é"),
    ]


def test_xml_space() -> None:
    source = parse_xml(
        '<source xml:space="default"> a <x id="foo[1]/bar[1]/baz[1]"/> </source>'
    )
    elem = lisa.xml_to_strelem(source)
    print(elem.sub)
    assert elem.sub == [StringElem("a "), X(id="foo[1]/bar[1]/baz[1]"), StringElem(" ")]


def test_inherited_xml_space() -> None:
    root = parse_xml(
        '<root xml:space="preserve"><source> a '
        '<x id="foo[1]/bar[1]/baz[1]"/> </source></root>'
    )
    elem = lisa.xml_to_strelem(root[0], xml_space="default")

    assert elem.sub == [
        StringElem(" a "),
        X(id="foo[1]/bar[1]/baz[1]"),
        StringElem(" "),
    ]


@mark.parametrize(
    ("content", "expected"),
    [
        ('<g id="first">Hello</g><g id="second"> world</g>', "Hello world"),
        ('<g id="first">Hello </g>world', "Hello world"),
        (' <g id="first"> world</g>', "world"),
        (
            '<g id="first" xml:space="preserve">Hello<g id="second" xml:space="default">  world  </g></g>',
            "Hello world",
        ),
    ],
)
def test_normalized_inline_whitespace(content: str, expected: str) -> None:
    source = parse_xml(f'<source xml:space="default">{content}</source>')

    assert str(lisa.xml_to_strelem(source)) == expected


@mark.parametrize(
    ("xml_space", "expected_tail"),
    [("default", " world"), ("preserve", " \t world")],
)
@mark.parametrize("nested", [False, True])
def test_xml_to_strelem_comment_tail(
    xml_space: str, expected_tail: str, nested: bool
) -> None:
    content = "Hello<!--note--> \t world"
    if nested:
        content = f'<g id="group">{content}</g>'
    source = parse_xml(f'<source xml:space="{xml_space}">{content}</source>')

    assert str(lisa.xml_to_strelem(source)) == f"Hello{expected_tail}"


@mark.parametrize("markup", ['<?php echo "hello"; ?>', "<?note value?>"])
@mark.parametrize("tag", [None, "g", "unknown"])
@mark.parametrize("xml_space", ["default", "preserve"])
@mark.parametrize("multiple", [False, True])
def test_xml_to_strelem_rejects_processing_instructions(
    markup: str, tag: str | None, xml_space: str, multiple: bool
) -> None:
    content = f"Hello {markup} \t world"
    if multiple:
        content += f" {markup} again"
    if tag is not None:
        content = f'<{tag} id="group">{content}</{tag}>'
    source = parse_xml(f'<source xml:space="{xml_space}">{content}</source>')

    with raises(TypeError):
        lisa.xml_to_strelem(source)
    with raises(TypeError):
        lisa.parse_xliff(etree.tostring(source, encoding="unicode"))


@mark.parametrize("cdata", [False, True])
@mark.parametrize("xml_space", ["default", "preserve"])
def test_literal_php_roundtrip(cdata: bool, xml_space: str) -> None:
    text = 'Hello <?php echo "hello"; ?> world'
    escaped = 'Hello &lt;?php echo "hello"; ?&gt; world'
    content = f"<![CDATA[{text}]]>" if cdata else escaped
    source = parse_xml(f'<source xml:space="{xml_space}">{content}</source>')
    restored = etree.Element("source")

    elem = lisa.xml_to_strelem(source)
    assert str(elem) == text
    lisa.strelem_to_xml(restored, elem)

    assert etree.tostring(restored, encoding="unicode") == f"<source>{escaped}</source>"
    assert str(lisa.parse_xliff(content)) == text


@mark.parametrize("tag", [None, "g", "unknown"])
@mark.parametrize(
    ("xml_space", "expected"),
    [("default", "Hello &word; again"), ("preserve", "Hello  &word; \t again")],
)
def test_xml_entity_roundtrip(xml_space: str, expected: str, tag: str | None) -> None:
    content = "Hello  &word; \t again"
    if tag is not None:
        content = f'<{tag} id="group">{content}</{tag}>'
        expected = f'<{tag} id="group">{expected}</{tag}>'
    source = parse_xml(
        '<!DOCTYPE source [<!ENTITY word "expanded">]>'
        f'<source xml:space="{xml_space}">{content}</source>'
    )

    elem = lisa.xml_to_strelem(source)
    entities = [item for item in elem.flatten() if isinstance(item, Entity)]
    assert len(entities) == 1
    assert str(entities[0]) == "&word;"
    assert not entities[0].iseditable
    assert not entities[0].istranslatable

    restored = etree.Element("source", attrib=dict(source.attrib))
    lisa.strelem_to_xml(restored, elem.copy())

    assert etree.tostring(restored, encoding="unicode") == (
        f'<source xml:space="{xml_space}">{expected}</source>'
    )
    assert len(list(restored.iter(etree.Entity))) == 1


def test_literal_entity_text_roundtrip() -> None:
    source = parse_xml("<source>&amp;word;</source>")
    restored = etree.Element("source")

    lisa.strelem_to_xml(restored, lisa.xml_to_strelem(source))

    assert etree.tostring(restored) == b"<source>&amp;word;</source>"


@mark.parametrize(
    ("xml_space", "expected_text", "expected_xml"),
    [
        ("default", "a &word;", "<source>a &amp;word;</source>"),
        ("preserve", " a  &word; ", "<source> a  &amp;word; </source>"),
    ],
)
def test_cdata_entity_text_roundtrip(
    xml_space: str, expected_text: str, expected_xml: str
) -> None:
    source = parse_xml(
        '<!DOCTYPE source [<!ENTITY word "expanded">]>'
        f'<source xml:space="{xml_space}"><![CDATA[ a  &word; ]]></source>'
    )
    restored = etree.Element("source")

    elem = lisa.xml_to_strelem(source)
    assert str(elem) == expected_text
    assert not any(isinstance(item, Entity) for item in elem.flatten())
    lisa.strelem_to_xml(restored, elem.copy())

    assert etree.tostring(restored, encoding="unicode") == expected_xml
    assert not list(restored.iter(etree.Entity))


def test_chunk_list() -> None:
    left = StringElem(
        [
            "a",
            G(id="foo[2]/bar[2]/baz[2]", sub=["b", X(id="foo[1]/bar[1]/baz[1]"), "c"]),
            "é",
        ]
    )
    right = StringElem(
        [
            "a",
            G(id="foo[2]/bar[2]/baz[2]", sub=["b", X(id="foo[1]/bar[1]/baz[1]"), "c"]),
            "é",
        ]
    )
    assert left == right


def test_set_strelem_to_xml() -> None:
    source = etree.Element("source")
    lisa.strelem_to_xml(source, StringElem("a"))
    assert etree.tostring(source, encoding="UTF-8") == b"<source>a</source>"

    source = etree.Element("source")
    lisa.strelem_to_xml(source, StringElem(["a", "é"]))
    assert etree.tostring(source, encoding="UTF-8") == b"<source>a\xc3\xa9</source>"

    source = etree.Element("source")
    lisa.strelem_to_xml(source, StringElem(X(id="foo[1]/bar[1]/baz[1]")))
    assert (
        etree.tostring(source, encoding="UTF-8")
        == b'<source><x id="foo[1]/bar[1]/baz[1]"/></source>'
    )

    source = etree.Element("source")
    lisa.strelem_to_xml(source, StringElem(["a", X(id="foo[1]/bar[1]/baz[1]")]))
    assert (
        etree.tostring(source, encoding="UTF-8")
        == b'<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>'
    )

    source = etree.Element("source")
    lisa.strelem_to_xml(source, StringElem(["a", X(id="foo[1]/bar[1]/baz[1]"), "é"]))
    assert (
        etree.tostring(source, encoding="UTF-8")
        == b'<source>a<x id="foo[1]/bar[1]/baz[1]"/>\xc3\xa9</source>'
    )

    source = etree.Element("source")
    lisa.strelem_to_xml(
        source,
        StringElem(
            [
                "a",
                G(
                    id="foo[2]/bar[2]/baz[2]",
                    sub=["b", X(id="foo[1]/bar[1]/baz[1]"), "c"],
                ),
                "é",
            ]
        ),
    )
    assert (
        etree.tostring(source, encoding="UTF-8")
        == b'<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>\xc3\xa9</source>'
    )


def test_unknown_xml_placeable() -> None:
    # The XML below is (modified) from the official XLIFF example file Sample_AlmostEverything_1.2_strict.xlf
    source = parse_xml(
        """<source xml:lang="en-us">Text <g id="_1_ski_040">g</g>TEXT<bpt id="_1_ski_139">bpt<sub>sub</sub>
               </bpt>TEXT<ept id="_1_ski_238">ept</ept>TEXT<ph id="_1_ski_337"/>TEXT<it id="_1_ski_436" pos="open">it</it>TEXT<mrk mtype="x-test">mrk</mrk>
               <x id="_1_ski_535"/>TEXT<bx id="_1_ski_634"/>TEXT<ex id="_1_ski_733"/>TEXT.</source>"""
    )
    elem = lisa.xml_to_strelem(source)

    custom = StringElem(
        [
            StringElem("Text "),
            G("g", id="_1_ski_040"),
            StringElem("TEXT"),
            UnknownXML(
                [
                    StringElem("bpt"),
                    UnknownXML("sub", xml_node=copy(source[1][0])),
                    StringElem("\n               "),
                ],
                id="_1_ski_139",
                xml_node=copy(source[3]),
            ),
            StringElem("TEXT"),
            UnknownXML("ept", id="_1_ski_238", xml_node=copy(source[2])),
            StringElem("TEXT"),
            UnknownXML(id="_1_ski_337", xml_node=copy(source[3])),  # ph-tag
            StringElem("TEXT"),
            UnknownXML("it", id="_1_ski_436", xml_node=copy(source[4])),
            StringElem("TEXT"),
            UnknownXML("mrk", xml_node=copy(source[5])),
            StringElem("\n               "),
            X(id="_1_ski_535"),
            StringElem("TEXT"),
            Bx(id="_1_ski_634"),
            StringElem("TEXT"),
            Ex(id="_1_ski_733"),
            StringElem("TEXT."),
        ]
    )
    assert elem == custom

    xml = copy(source)
    for _i in range(len(xml)):
        del xml[0]
    xml.text = None
    xml.tail = None
    lisa.strelem_to_xml(xml, elem)
    assert etree.tostring(xml) == etree.tostring(source)
