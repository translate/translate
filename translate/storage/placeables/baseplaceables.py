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

"""Base classes for inline elements representation."""

#----------------------------------------------------------------------

MASK, REPLACEMENT, DELIMITER = 0, 1, 2

class Placeable(object):
    """Base class for placeables hierarchy.
    
    Our concept of I{placeable} is mainly based on the inline elements
    definition from different LISA standards (XLIFF, TMX, TBX). For detailed
    information, see the specifications:
      - XLIFF: U{http://docs.oasis-open.org/xliff/xliff-core/xliff-core.html}
      - TMX: U{http://www.lisa.org/fileadmin/standards/tmx2/tmx.html}
      - TBX: U{http://www.lisa.org/fileadmin/standards/tbxISO_final.html}
    
    Method and variable names derive (freely) from the LISA terminology.

    A placeable consists of the following:
      - A I{content} string. This is a string representating the actual 
        native code in the original data.
      - A I{markedcontent} list. This is a structured representation of the 
        actual native code in the original data, mainly used when there are
        nested placeable objects in the content. 
        The list elements are (native_code_string, placeable_object) where the
        placeable_object is the representation of the native_code_string 
        or B{None}.
      - A I{ctype} string. This attribute specifies the type of code or data
        that is represented by the placeable (e.g. bolding code, page break).
      - A I{equiv_text} string. This is the equivalent string text of the 
        placeable. Mainly used for lexical purposes (e.g. string comparison).

    The I{emptycontent} class attribute indicates if instances of this
    placeable class cannot have content.

    The I{type} class attribute specifies the type of the placeable. Placeables
    can either 1. mask, 2. replace DOM sub-trees, 3. replace delimiters
    according to the XLIFF specification. This value can assume one of
    MASK, REPLACEMENT or DELIMITER.
    
    @group content: *content*
    @group ctype: *ctype*
    @group equiv_text: *equiv_text*
    """
    emptycontent = False
    type = REPLACEMENT

    def __init__(self, content, ctype=None, equiv_text=None):
        self.content = content
        self.ctype = ctype
        self.equiv_text = equiv_text
        super(Placeable, self).__init__()
        
    def __eq__(self, other):
        """Compares two Placeable objects.
        
        @type other: L{Placeable}
        @param other: Another L{Placeable}
        @rtype: Boolean
        @return: Returns True if the supplied Placeable equals this one.       
        """
        if not isinstance(other, Placeable):
            return False
        return self.content == other.content and self.ctype == other.ctype and \
               self.equiv_text == other.equiv_text
    
    def __str__(self):
        return "<%s [ctype='%s', equiv-text='%s'] content='%s'>" % \
          (self.__class__.__name__, str(self.ctype), str(self.equiv_text), str(self.content)) 

    def getmarkedcontent(self):
        return self.content 
    
    markedcontent = property(getmarkedcontent)
    
    def buildfromplaceable(cls, placeable):
        """Build a native placeable from a foreign one, preserving as much information as possible."""
        if type(placeable) == cls and hasattr(placeable, "copy") and \
           callable(placeable.copy):
            return placeable.copy()
        new_placeable = cls(placeable.content, placeable.ctype, placeable.equiv_text)
        return new_placeable
    
    buildfromplaceable = classmethod(buildfromplaceable)    
    