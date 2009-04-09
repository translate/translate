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

"""Contains XLIFF-specific placeables."""

from translate.storage.placeables import base
from translate.storage.placeables.strelem import StringElem

__all__ = ['Bpt', 'Ept', 'X', 'Bx', 'Ex', 'G', 'It', 'Sub', 'Ph', 'parsers', 'to_xliff_placeables']


class Bpt(base.Bpt):
    pass


class Ept(base.Ept):
    pass


class Ph(base.Ph):
    pass


class It(base.It):
    pass


class G(base.G):
    pass


class Bx(base.Bx):
    pass


class Ex(base.Ex):
    pass


class X(base.X):
    pass


class Sub(base.Sub):
    pass


def to_xliff_placeables(tree):
    if not isinstance(tree, StringElem):
        return tree

    newtree = None

    classmap = {
        base.Bpt: Bpt,
        base.Ept: Ept,
        base.Ph:  Ph,
        base.It:  It,
        base.G:   G,
        base.Bx:  Bx,
        base.Ex:  Ex,
        base.X:   X,
        base.Sub: Sub
    }
    for baseclass, xliffclass in classmap.items():
        if isinstance(tree, baseclass):
            newtree = xliffclass()

    if newtree is None:
        newtree = tree.__class__()

    newtree.id = tree.id
    newtree.rid = tree.rid
    newtree.xid = tree.xid
    newtree.sub = []

    for subtree in tree.sub:
        newtree.sub.append(to_xliff_placeables(subtree))

    return newtree


parsers = []
