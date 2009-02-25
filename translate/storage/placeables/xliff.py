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


class Bpt(interfaces.Bpt, XLIFFPlaceable):
    pass


class Ept(interfaces.Ept, XLIFFPlaceable):
    pass


class Ph(interfaces.Ph, XLIFFPlaceable):
    pass


class It(interfaces.It, XLIFFPlaceable):
    pass


class G(interfaces.G, XLIFFPlaceable):
    pass


class Bx(interfaces.Bx, XLIFFPlaceable):
    pass


class Ex(interfaces.Ex, XLIFFPlaceable):
    pass


class X(interfaces.X, XLIFFPlaceable):
    pass


class Sub(interfaces.Sub, XLIFFPlaceable):
    pass
