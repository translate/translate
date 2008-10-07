# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
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

from translate.convert import accesskey

from py import test

def test_get_label_and_accesskey():
    """test that we can extract the label and accesskey components from an accesskey+label 
    string"""
    assert accesskey.get_label_and_accesskey(u"&File") == (u"File", u"F")
    assert accesskey.get_label_and_accesskey(u"~File", u"~") == (u"File", u"F")
    assert accesskey.get_label_and_accesskey(u"~File", u"~") == (u"File", u"F")

def test_ignore_entities():
    """test that we don't get confused with entities and a & access key marker"""
    assert accesskey.get_label_and_accesskey(u"Set &browserName; as &Default") != (u"Set &browserName; as &Default", u"b")
    assert accesskey.get_label_and_accesskey(u"Set &browserName; as &Default") == (u"Set &browserName; as Default", u"D")
 
def test_alternate_accesskey_marker():
    """check that we can identify the accesskey if the marker is different"""
    assert accesskey.get_label_and_accesskey(u"~File", u"~") == (u"File", u"F")
    assert accesskey.get_label_and_accesskey(u"&File", u"~") == (u"&File", u"")

def test_unicode():
    """test that we can do the same with unicode strings"""
    assert accesskey.get_label_and_accesskey(u"Eḓiṱ") == (u"Eḓiṱ", u"")
    assert accesskey.get_label_and_accesskey(u"E&ḓiṱ") == (u"Eḓiṱ", u"ḓ")
    assert accesskey.get_label_and_accesskey(u"E_ḓiṱ", u"_") == (u"Eḓiṱ", u"ḓ")
    label, akey = accesskey.get_label_and_accesskey(u"E&ḓiṱ")
    assert label, akey == (u"Eḓiṱ", u"ḓ")
    assert isinstance(label, unicode) and isinstance(akey, unicode)

def test_empty_string():
    """test that we can handle and empty label+accesskey string"""
    assert accesskey.get_label_and_accesskey(u"") == (u"", u"")
    assert accesskey.get_label_and_accesskey(u"", u"~") == (u"", u"")
