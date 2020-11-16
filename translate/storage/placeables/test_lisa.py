#
# Copyright 2006-2007 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

from lxml import etree

from translate.storage.placeables import StringElem, lisa
from translate.storage.placeables.xliff import Bx, Ex, G, UnknownXML, X


def test_xml_to_strelem():
    source = etree.fromstring("<source>a</source>")
    elem = lisa.xml_to_strelem(source)
    assert elem == StringElem("a")

    source = etree.fromstring('<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.sub == [StringElem("a"), X(id="foo[1]/bar[1]/baz[1]")]

    source = etree.fromstring('<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.sub == [StringElem("a"), X(id="foo[1]/bar[1]/baz[1]"), StringElem("é")]

    source = etree.fromstring(
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


def test_xml_space():
    source = etree.fromstring(
        '<source xml:space="default"> a <x id="foo[1]/bar[1]/baz[1]"/> </source>'
    )
    elem = lisa.xml_to_strelem(source)
    print(elem.sub)
    assert elem.sub == [StringElem("a "), X(id="foo[1]/bar[1]/baz[1]"), StringElem(" ")]


def test_chunk_list():
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


def test_set_strelem_to_xml():
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


def test_unknown_xml_placeable():
    # The XML below is (modified) from the official XLIFF example file Sample_AlmostEverything_1.2_strict.xlf
    source = etree.fromstring(
        """<source xml:lang="en-us">Text <g id="_1_ski_040">g</g>TEXT<bpt id="_1_ski_139">bpt<sub>sub</sub>
               </bpt>TEXT<ept id="_1_ski_238">ept</ept>TEXT<ph id="_1_ski_337"/>TEXT<it id="_1_ski_436" pos="open">it</it>TEXT<mrk mtype="x-test">mrk</mrk>
               <x id="_1_ski_535"/>TEXT<bx id="_1_ski_634"/>TEXT<ex id="_1_ski_733"/>TEXT.</source>"""
    )
    elem = lisa.xml_to_strelem(source)

    from copy import copy

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
    for i in range(len(xml)):
        del xml[0]
    xml.text = None
    xml.tail = None
    lisa.strelem_to_xml(xml, elem)
    assert etree.tostring(xml) == etree.tostring(source)
