#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

__all__ = ['Placeable', 'Bpt', 'Ept', 'X', 'Bx', 'Ex', 'G', 'It', 'Sub', 'Ph']

def as_string(chunk_seq):
    return u''.join([repr(chunk) for chunk in chunk_seq])
    
class PlaceableId(object):
    def __init__(self, id=None, content=None, xid=None, rid=None):
        self.id      = id
        self.xid     = xid
        self.rid     = rid

class Placeable(PlaceableId):
    has_content = True
    
    def __init__(self, id, content=None, xid=None, rid=None):
        super(Placeable, self).__init__(id, xid, rid)
        self.content = content

    def __unicode__(self):
        if self.has_content:
            return as_string(self.content)
        else:
            return u'\ufffc'
        
    def __repr__(self):
        return u'<%(tagname)s id=%(id)s />' % {'tagname': self.__class__.__name__, 
                                               'id': self.id }
        
    def __eq__(self, other):
        return self.id        == other.id        and \
               self.content   == other.content   and \
               self.xid       == other.xid       and \
               self.rid       == other.rid       and \
               self.__class__ == other.__class__

class Delimiter(object):
    pass

class PairedDelimiter(object):
    pass

class MaskingPlaceable(Placeable):
    def __init__(self, id, content, masked_code):
        raise NotImplementedError

class Bpt(MaskingPlaceable, PairedDelimiter):
    pass

class Ept(MaskingPlaceable, PairedDelimiter):
    pass

class Ph(MaskingPlaceable):
    pass

class It(MaskingPlaceable, Delimiter):
    pass
        
class ReplacementPlaceable(Placeable):
    pass

class G(ReplacementPlaceable):
    pass

class Bx(ReplacementPlaceable, PairedDelimiter):
    has_content = False

    def __init__(self, id, xid = None):
        ReplacementPlaceable.__init__(self, id, content = None, xid = xid)

class Ex(ReplacementPlaceable, PairedDelimiter):
    has_content = False

    def __init__(self, id, xid = None):
        ReplacementPlaceable.__init__(self, id, content = None, xid = xid)

class X(ReplacementPlaceable, Delimiter):
    has_content = False

    def __init__(self, id, xid = None):
        ReplacementPlaceable.__init__(self, id, content = None, xid = xid)

class SubflowPlaceable(Placeable):
    pass

class Sub(SubflowPlaceable):
    pass

