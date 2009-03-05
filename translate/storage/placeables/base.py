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
Contains base placeable classes with names based on XLIFF placeables. See the
XLIFF standard for more information about what the names mean.
"""

from strelem import StringElem
from interfaces import *


__all__ = ['Bpt', 'Ept', 'Ph', 'It', 'G', 'Bx', 'Ex', 'X', 'Sub', 'to_base_placeables']


# Basic placeable types.
class Bpt(MaskingPlaceable, PairedDelimiter):
    pass


class Ept(MaskingPlaceable, PairedDelimiter):
    pass


class Ph(MaskingPlaceable):
    pass


class It(MaskingPlaceable, Delimiter):
    pass


class G(ReplacementPlaceable):
    pass


class Bx(ReplacementPlaceable, PairedDelimiter):
    has_content = False

    def __init__(self, id=None, xid=None):
        ReplacementPlaceable.__init__(self, id=id, xid=xid)


class Ex(ReplacementPlaceable, PairedDelimiter):
    has_content = False

    def __init__(self, id=None, xid=None):
        ReplacementPlaceable.__init__(self, id=id, xid=xid)


class X(ReplacementPlaceable, Delimiter):
    has_content = False

    def __init__(self, id=None, xid=None):
        ReplacementPlaceable.__init__(self, id=id, xid=xid)


class Sub(SubflowPlaceable):
    pass


def to_base_placeables(tree):
    if not isinstance(tree, StringElem):
        return tree

    base_class = [klass for klass in tree.__class__.__bases__ \
                  if klass in [Bpt, Ept, Ph, It, G, Bx, Ex, X, Sub]]

    if not base_class:
        base_class = tree.__class__
    else:
        base_class = base_class[0]

    newtree = base_class()
    newtree.id = tree.id
    newtree.rid = tree.rid
    newtree.xid = tree.xid
    newtree.subelems = []

    for subtree in tree.subelems:
        newtree.subelems.append(to_base_placeables(subtree))

    return newtree
