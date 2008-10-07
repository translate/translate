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

DEFAULT_ACCESSKEY_MARKER = "&"

def getlabel(unquotedstr, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """retrieve the label from a mixed label+accesskey entity"""
    if isinstance(unquotedstr, str):
        unquotedstr = unquotedstr.decode("UTF-8")
    # mixed labels just need the & taken out
    # except that &entity; needs to be avoided...
    amppos = 0
    while amppos >= 0:
        amppos = unquotedstr.find(accesskey_marker, amppos)
        if amppos != -1:
            amppos += 1
            semipos = unquotedstr.find(";", amppos)
            if semipos != -1:
                if unquotedstr[amppos:semipos].isalnum():
                    continue
            # otherwise, cut it out... only the first one need be changed
            # (see below to see how the accesskey is done)
            unquotedstr = unquotedstr[:amppos-1] + unquotedstr[amppos:]
            break
    return unquotedstr.encode("UTF-8")

def getaccesskey(unquotedstr, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """retrieve the access key from a mixed label+accesskey entity"""
    if isinstance(unquotedstr, str):
        unquotedstr = unquotedstr.decode("UTF-8")
    # mixed access keys need the key extracted from after the &
    # but we must avoid proper entities i.e. &gt; etc...
    amppos = 0
    while amppos >= 0:
        amppos = unquotedstr.find(accesskey_marker, amppos)
        if amppos != -1:
            amppos += 1
            semipos = unquotedstr.find(";", amppos)
            if semipos != -1:
                if unquotedstr[amppos:semipos].isalnum():
                    # what we have found is an entity, not a shortcut key...
                    continue
            # otherwise, we found the shortcut key
            return unquotedstr[amppos].encode("UTF-8")
    # if we didn't find the shortcut key, return an empty string rather than the original string
    # this will come out as "don't have a translation for this" because the string is not changed...
    # so the string from the original dtd will be used instead
    return ""

def get_label_and_accesskey(string, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """Extract the label and accesskey form a label+accesskey string

    The function will also try to ignore &entities; which would obviously not
    contain accesskeys.

    @type string: Unicode
    @param string: A string that might contain a label with accesskey marker
    @type accesskey_marker: Char
    @param accesskey_marker: The character that is used to prefix an access key
    """
    return getlabel(string, accesskey_marker), getaccesskey(string, accesskey_marker)
