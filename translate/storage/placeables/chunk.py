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

from translate.storage.placeables import baseplaceables
from UserList import UserList

def as_chunk(obj):
    if isinstance(obj, (unicode, str)):
        return Chunk(unicode(obj))
    elif isinstance(obj, baseplaceables.Placeable):
        return Chunk(obj)
    else:
        assert isinstance(obj, Chunk)
        return obj

class ChunkList(UserList):
    def __init__(self, a_seq):
        self.data = []
        self.extend(a_seq)
    
    def append(self, a_chunk):
        UserList.append(self, as_chunk(a_chunk))

    def extend(self, a_chunk_seq):
        UserList.extend(self, [as_chunk(a_chunk) for a_chunk in a_chunk_seq])

    def _get_text(self):
        return u''.join([chunk.text for chunk in self])
    text = property(_get_text)

class Chunk(object):
    def __init__(self, data):
        self._data = data
    
    def _get_text(self):
        if isinstance(self._data, baseplaceables.Placeable):
            return u'\ufffc'
        else:
            return self._data        
    text = property(_get_text)
