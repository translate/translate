#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006-2007 Zuza Software Foundation
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

from lxml import etree
from translate.storage.placeables import lisa
from translate.storage.placeables.base import X, Bx, Ex, G, Bpt, Ept, Ph, It, Sub

def test_extract_chunks():
    source = etree.fromstring(u'<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>')
    chunks = lisa.extract_chunks(source)
    assert chunks == ['a', X('foo[1]/bar[1]/baz[1]')]

    source = etree.fromstring(u'<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>')
    chunks = lisa.extract_chunks(source)
    assert chunks == ['a', X('foo[1]/bar[1]/baz[1]'), 'é']

    source = etree.fromstring(u'<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>é</source>')
    chunks = lisa.extract_chunks(source)
    assert chunks == ['a', G('foo[2]/bar[2]/baz[2]', ['b', X(id = 'foo[1]/bar[1]/baz[1]'), 'c']), 'é']

def test_chunk_list():
    left  = ['a', G('foo[2]/bar[2]/baz[2]', ['b', X(id = 'foo[1]/bar[1]/baz[1]'), 'c']), 'é']
    right = ['a', G('foo[2]/bar[2]/baz[2]', ['b', X(id = 'foo[1]/bar[1]/baz[1]'), 'c']), 'é']
    assert left == right

def test_set_insert_into_dom():
    source = etree.Element(u'source')
    lisa.insert_into_dom(source, ['a'])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source>a</source>'

    source = etree.Element(u'source')
    lisa.insert_into_dom(source, ['a', 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source>aé</source>'

    source = etree.Element(u'source')
    lisa.insert_into_dom(source, [X('foo[1]/bar[1]/baz[1]')])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source><x id="foo[1]/bar[1]/baz[1]"/></source>'

    source = etree.Element(u'source')
    lisa.insert_into_dom(source, ['a', X('foo[1]/bar[1]/baz[1]')])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>'
    
    source = etree.Element(u'source')
    lisa.insert_into_dom(source, ['a', X('foo[1]/bar[1]/baz[1]'), 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>'

    source = etree.Element(u'source')
    lisa.insert_into_dom(source, ['a', G('foo[2]/bar[2]/baz[2]', ['b', X(id = 'foo[1]/bar[1]/baz[1]'), 'c']), 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == u'<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>é</source>'

if __name__ == '__main__':
    test_chunk_list()
    test_extract_chunks()
    test_set_insert_into_dom()
    