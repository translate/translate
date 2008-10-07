#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2008 Zuza Software Foundation
#
# This file is part of The Translate Toolkit.
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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""functions used to manipulate access keys in strings"""

DEFAULT_ACCESSKEY_MARKER = u"&"

def getlabel(unquotedstr, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """retrieve the label from a mixed label+accesskey entity"""
    label, accesskey = get_label_and_accesskey(unquotedstr, accesskey_marker)
    return label

def getaccesskey(unquotedstr, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """retrieve the access key from a mixed label+accesskey entity"""
    label, accesskey = get_label_and_accesskey(unquotedstr, accesskey_marker)
    return accesskey

def get_label_and_accesskey(string, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """Extract the label and accesskey form a label+accesskey string

    The function will also try to ignore &entities; which would obviously not
    contain accesskeys.

    @type string: Unicode
    @param string: A string that might contain a label with accesskey marker
    @type accesskey_marker: Char
    @param accesskey_marker: The character that is used to prefix an access key
    """
    assert isinstance(string, unicode)
    assert isinstance(accesskey_marker, unicode)
    assert len(accesskey_marker) == 1
    if string == u"":
        return u"", u""
    accesskey = u""
    label = string
    marker_pos = 0
    while marker_pos >= 0:
        marker_pos = string.find(accesskey_marker, marker_pos)
        if marker_pos != -1:
            marker_pos += 1
            semicolon_pos = string.find(";", marker_pos)
            if semicolon_pos != -1:
                if string[marker_pos:semicolon_pos].isalnum():
                    continue
            label = string[:marker_pos-1] + string[marker_pos:]
            accesskey = string[marker_pos]
            break
    return label, accesskey
