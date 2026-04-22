#
# Copyright 2002-2006 Zuza Software Foundation
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

from io import BytesIO
from operator import itemgetter

from lxml import etree

from translate.storage.xml_extract import extract, misc

# reduce_tree

test_tree_1 = (
    "a",
    [("b", []), ("c", [("d", []), ("e", [])]), ("f", [("g", [("h", [])])])],
)

test_tree_2 = (1, [(2, []), (3, [(4, []), (5, [])]), (6, [(7, [(8, [])])])])


def test_reduce_tree() -> None:
    def concatenate(parent_node, node, string):
        return string + node[0]

    assert (
        misc.reduce_tree(concatenate, test_tree_1, test_tree_1, itemgetter(1), "")
        == "abcdefgh"
    )

    def get_even_and_total(parent_node, node, even_lst, total):
        num = node[0]
        if num % 2 == 0:
            even_lst.append(num)
        return even_lst, total + num

    assert misc.reduce_tree(
        get_even_and_total, test_tree_2, test_tree_2, itemgetter(1), [], 0
    ) == ([2, 4, 6, 8], 36)


# compose_mappings
left_mapping = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
right_mapping = {"a": -1, "b": -2, "d": -4, "e": -5, "f": -6}

composed_mapping = {1: -1, 2: -2, 4: -4, 5: -5}


def test_compose_mappings() -> None:
    assert composed_mapping == misc.compose_mappings(left_mapping, right_mapping)


# parse_tag


def test_parse_tag() -> None:
    assert misc.parse_tag("{some-urn}some-tag") == ("some-urn", "some-tag")

    assert misc.parse_tag(
        "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content"
    ) == (
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "document-content",
    )


def test_safe_parser_rejects_entity_expansion() -> None:
    xml = BytesIO(
        b"""<!DOCTYPE root [
<!ENTITY a0 "ha">
<!ENTITY a1 "&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;">
<!ENTITY a2 "&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;">
]>
<root>&a2;</root>"""
    )

    # libxml2 may either preserve the unresolved entity node or reject the
    # nested entity definitions as a loop, depending on the build/version.
    # Both outcomes are acceptable here because neither expands the entity.
    try:
        tree = extract.parse_xml_file(xml)
    except etree.XMLSyntaxError:
        return
    root = tree.getroot()

    assert root.text is None
    assert len(root) == 1
    assert root[0].tag is extract.etree.Entity
