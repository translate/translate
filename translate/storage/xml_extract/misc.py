#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import contextlib
import re


def reduce_tree(f, parent_unit_node, unit_node, get_children, *state):
    """
    Enumerate a tree, applying f to in a pre-order fashion to each node.

    parent_unit_node contains the parent of unit_node. For the root of the tree,
    parent_unit_node == unit_node.

    get_children is a single argument function applied to a unit_node to
    get a list/iterator to its children.

    state is used by f to modify state information relating to whatever f does
    to the tree.
    """

    def as_tuple(x):
        if isinstance(x, tuple):
            return x
        return (x,)

    state = f(parent_unit_node, unit_node, *state)
    for child_unit_node in get_children(unit_node):
        state = reduce_tree(
            f, unit_node, child_unit_node, get_children, *as_tuple(state)
        )
    return state


def compose_mappings(left, right):
    """
    Given two mappings left: A -> B and right: B -> C, create a hash
    result_map: A -> C. Only values in left (i.e. things from B) which have
    corresponding keys in right will have their keys mapped to values in right.
    """
    result_map = {}
    for left_key, left_val in left.items():
        with contextlib.suppress(KeyError):
            result_map[left_key] = right[left_val]
    return result_map


tag_pattern = re.compile(r"({(?P<namespace>(\w|[-:./])*)})?(?P<tag>(\w|[-])*)")


def parse_tag(full_tag):
    """
    Parse a full XML tag name into namespace and tag name.

    >>> parse_tag('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content')
    ('urn:oasis:names:tc:opendocument:xmlns:office:1.0', 'document-content')
    >>> parse_tag('document-content')
    ('', 'document-content').
    """
    match = tag_pattern.match(full_tag)
    if match is not None:
        # Slightly hacky way of supporting 2+3
        ret = []
        for k in ("namespace", "tag"):
            value = match.groupdict()[k] or ""
            if not isinstance(value, str):
                value = str(value, encoding="utf-8")
            ret.append(value)
        return ret[0], ret[1]
    raise ValueError("Passed an invalid tag")
