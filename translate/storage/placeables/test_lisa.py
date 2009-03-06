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
from translate.storage.placeables import lisa, StringElem
from translate.storage.placeables.xliff import X, G

def test_xml_to_strelem():
    source = etree.fromstring(u'<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.subelems == [u'a', X(id=u'foo[1]/bar[1]/baz[1]')]

    source = etree.fromstring(u'<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.subelems == [u'a', X(id=u'foo[1]/bar[1]/baz[1]'), u'é']

    source = etree.fromstring(u'<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>é</source>')
    elem = lisa.xml_to_strelem(source)
    assert elem.subelems == [u'a', G(id=u'foo[2]/bar[2]/baz[2]', subelems=[u'b', X(id=u'foo[1]/bar[1]/baz[1]'), u'c']), u'é']

def test_chunk_list():
    left  = StringElem(['a', G(id='foo[2]/bar[2]/baz[2]', subelems=['b', X(id='foo[1]/bar[1]/baz[1]'), 'c']), 'é'])
    right = StringElem(['a', G(id='foo[2]/bar[2]/baz[2]', subelems=['b', X(id='foo[1]/bar[1]/baz[1]'), 'c']), 'é'])
    assert left == right

def test_set_strelem_to_xml():
    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, ['a'])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source>a</source>'

    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, ['a', 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source>aé</source>'

    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, [X(id='foo[1]/bar[1]/baz[1]')])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source><x id="foo[1]/bar[1]/baz[1]"/></source>'

    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, ['a', X(id='foo[1]/bar[1]/baz[1]')])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source>a<x id="foo[1]/bar[1]/baz[1]"/></source>'

    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, ['a', X(id='foo[1]/bar[1]/baz[1]'), 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source>a<x id="foo[1]/bar[1]/baz[1]"/>é</source>'

    source = etree.Element(u'source')
    lisa.strelem_to_xml(source, ['a', G(id='foo[2]/bar[2]/baz[2]', subelems=['b', X(id='foo[1]/bar[1]/baz[1]'), 'c']), 'é'])
    assert etree.tostring(source, encoding = 'UTF-8') == '<source>a<g id="foo[2]/bar[2]/baz[2]">b<x id="foo[1]/bar[1]/baz[1]"/>c</g>é</source>'

if __name__ == '__main__':
    test_chunk_list()
    test_xml_to_strelem()
    test_set_strelem_to_xml()
