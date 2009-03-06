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


def xliff__unicode__(self):
    if hasattr(self, 'has_content') and self.has_content:
        return u'<%(tag)s%(id)s%(rid)s%(xid)s>%(subelems)s</%(tag)s>' % {
            'tag': self.__class__.__name__.lower(),
            'id':  self.id  and ' id="%s"'  % (self.id)  or '',
            'rid': self.rid and ' rid="%s"' % (self.rid) or '',
            'xid': self.xid and ' xid="%s"' % (self.xid) or '',
            'subelems': u''.join([unicode(s) for s in self.subelems])
        }
    return u'<%(tag)s%(id)s%(rid)s%(xid)s/>' % {
        'tag': self.__class__.__name__.lower(),
        'id':  self.id  and ' id="%s"'  % (self.id)  or '',
        'rid': self.rid and ' rid="%s"' % (self.rid) or '',
        'xid': self.xid and ' xid="%s"' % (self.xid) or ''
    }


class Bpt(base.Bpt):
    __unicode__ = xliff__unicode__


class Ept(base.Ept):
    __unicode__ = xliff__unicode__


class Ph(base.Ph):
    __unicode__ = xliff__unicode__


class It(base.It):
    __unicode__ = xliff__unicode__


class G(base.G):
    __unicode__ = xliff__unicode__


class Bx(base.Bx):
    __unicode__ = xliff__unicode__


class Ex(base.Ex):
    __unicode__ = xliff__unicode__


class X(base.X):
    __unicode__ = xliff__unicode__


class Sub(base.Sub):
    __unicode__ = xliff__unicode__


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
    newtree.subelems = []

    for subtree in tree.subelems:
        newtree.subelems.append(to_xliff_placeables(subtree))

    return newtree


parsers = []
