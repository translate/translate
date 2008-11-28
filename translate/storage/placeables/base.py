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

"""This module implements basic functionality to support placeables.

A placeable is used to represent things like:
1. substitutions
     for example, in ODF, footnotes appear in the ODF xml
     where they are defined; so if we extract a paragraph with some
     footnotes, the translator will have a lot of additional XML to with;
     so we separate the footnotes out into separate translation units and
     mark their positions in the original text with placeables.
2. hiding of inline formatting data
     the translator doesn't want to have to deal with all the weird
     formatting conventions of wherever the text came from.
3. marking variables
     This is an old issue - translators translate variable names which
     should remain untranslated. We can wrap placeables around variable
     names to avoid this.

The placeables model follows the XLIFF standard's list of placeables.
Please refer to the XLIFF specification to get a better understanding.
"""

__all__ = ['Placeable', 'Bpt', 'Ept', 'X', 'Bx', 'Ex', 'G', 'It', 'Sub', 'Ph']

def as_string(chunk_seq):
    return u''.join([unicode(chunk) for chunk in chunk_seq])
    
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
        if self.has_content:
            return u'<%(tagname)s id=%(id)s>%(content)s</%(tagname)s>' % \
                {'tagname': self.__class__.__name__,
                 'id':      self.id,
                 'content': as_string(self.content)}
        else:
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

