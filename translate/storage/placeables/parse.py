#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
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

"""
Contains the C{parse} function that parses normal strings into StringElem-
based "rich" string element trees.
"""

from translate.storage.placeables import base, StringElem


def parse(tree, parse_funcs):
    if isinstance(tree, (str, unicode)):
        tree = StringElem([tree])
    if not parse_funcs:
        return tree
    leaves = [elem for elem in tree.depth_first() if elem.isleaf()]
    print leaves
    parse_func = parse_funcs[0]

    for leaf in leaves:
        subleaves = parse_func(unicode(leaf))
        if subleaves is not None:
            leaf.sub = subleaves
        parse(leaf, [f for f in parse_funcs if f is not parse_func])

        if len(leaf.sub) == 1 and \
                leaf.__class__ is StringElem and \
                leaf.sub[0].__class__ is not StringElem and \
                isinstance(leaf.sub[0], StringElem):
            parent = tree.get_parent_elem(leaf)
            if parent is not None:
                leafindex = parent.sub.index(leaf)
                parent.sub[leafindex] = leaf.sub[0]
    return tree
