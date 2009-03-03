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

from translate.storage.placeables import interfaces

__all__ = ['Bpt', 'Ept', 'X', 'Bx', 'Ex', 'G', 'It', 'Sub', 'Ph']


class XLIFFPlaceable(object):
    """A class with some XLIFF-specific functionality."""

    def __unicode__(self):
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


class Bpt(XLIFFPlaceable, interfaces.Bpt):
    pass


class Ept(XLIFFPlaceable, interfaces.Ept):
    pass


class Ph(XLIFFPlaceable, interfaces.Ph):
    pass


class It(XLIFFPlaceable, interfaces.It):
    pass


class G(XLIFFPlaceable, interfaces.G):
    pass


class Bx(XLIFFPlaceable, interfaces.Bx):
    pass


class Ex(XLIFFPlaceable, interfaces.Ex):
    pass


class X(XLIFFPlaceable, interfaces.X):
    pass


class Sub(XLIFFPlaceable, interfaces.Sub):
    pass
