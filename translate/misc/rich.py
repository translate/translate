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

__all__ = ['only_strings', 'map_rich']

from translate.storage.placeables import StringElem

def map_content(f, chunk):
    """If chunk is a StringElem and it has content, we need
    to modify the content as well.

    Note that this is NOT a pure function. For that, we would
    need to copy the placeables themselves."""
    if isinstance(chunk, StringElem):
        if chunk.subelems is not None:
            chunk.subelems = map_entry(f, chunk.subelems)
    return chunk

def map_entry(f, chunk_seq):
    """Transform every chunk in chunk_seq with the function f,
    including the inner content of any placeables."""
    return [f(map_content(f, chunk)) for chunk in chunk_seq]

def only_strings(f):
    """A decorator to ensure that f is only applied to strings
    and not Placeables. It's used to decorate the function
    passed to map_rich."""
    def decorated_f(arg):
        if not isinstance(arg, StringElem):
            return f(arg)
        else:
            return arg
    return decorated_f

def map_rich(f, rich_string):
    """Return a new list of chunk sequences, where each chunk
    sequence has f applied to it."""
    return [map_entry(f, entry) for entry in rich_string]
