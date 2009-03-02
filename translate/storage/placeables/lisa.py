#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from lxml import etree

from translate.storage.placeables import placeables
from translate.storage.placeables.base import StringElem
from translate.storage.xml_extract import misc


def make_empty_replacement_placeable(klass, node):
    try:
        return klass(id=node.attrib[u'id'])
    except KeyError:
        pass
    retur klass()

def make_g_placeable(klass, node):
    return klass(id=node.attrib[u'id'], subelems=extract_chunks(node).subelems)

def not_yet_implemented(klass, node):
    raise NotImplementedError

_class_dictionary = {
    u'bpt': (placeables.Bpt, not_yet_implemented),
    u'bx' : (placeables.Bx,  make_empty_replacement_placeable),
    u'ept': (placeables.Ept, not_yet_implemented),
    u'ex' : (placeables.Ex,  make_empty_replacement_placeable),
    u'g'  : (placeables.G,   make_g_placeable),
    u'it' : (placeables.It,  not_yet_implemented),
    u'ph' : (placeables.Ph,  not_yet_implemented),
    u'sub': (placeables.Sub, not_yet_implemented),
    u'x'  : (placeables.X,   make_empty_replacement_placeable)
}

def make_placeable(node):
    _namespace, tag = misc.parse_tag(node.tag)
    klass, maker = _class_dictionary[tag]
    return maker(klass, node)

def as_unicode(string):
    if isinstance(string, unicode):
        return string
    else:
        return unicode(string.decode('utf-8'))

def extract_chunks(dom_node):
    result = StringElem()
    if dom_node.text:
        result.subelems.append(as_unicode(dom_node.text))
    for child_dom_node in dom_node:
        result.subelems.append(make_placeable(child_dom_node))
        if child_dom_node.tail:
            result.subelems.append(as_unicode(child_dom_node.tail))
    return result

# ==========================================================

def placeable_as_dom_node(placeable, tagname):
    dom_node = etree.Element(tagname)
    if placeable.id is not None:
        dom_node.attrib['id'] = placeable.id
    if placeable.xid is not None:
        dom_node.attrib['xid'] = placeable.xid
    if placeable.rid is not None:
        dom_node.attrib['rid'] = placeable.rid
    return dom_node

_placeable_dictionary = {
    placeables.Bpt: lambda placeable: placeable_as_dom_node(placeable, 'bpt'),
    placeables.Bx : lambda placeable: placeable_as_dom_node(placeable, 'bx'),
    placeables.Ept: lambda placeable: placeable_as_dom_node(placeable, 'ept'),
    placeables.Ex : lambda placeable: placeable_as_dom_node(placeable, 'ex'),
    placeables.G  : lambda placeable: placeable_as_dom_node(placeable, 'g'),
    placeables.It : lambda placeable: placeable_as_dom_node(placeable, 'it'),
    placeables.Ph : lambda placeable: placeable_as_dom_node(placeable, 'ph'),
    placeables.Sub: lambda placeable: placeable_as_dom_node(placeable, 'sub'),
    placeables.X  : lambda placeable: placeable_as_dom_node(placeable, 'x')
}

class EOF: pass

def end_with_eof(seq):
    for item in seq:
        yield item
    while True:
        yield EOF

def collect_text(text, next, itr):
    text = as_unicode(text)
    if isinstance(next, (unicode, str)):
        return collect_text(text + as_unicode(next), itr.next(), itr)
    else:
        return text, next

def get_placeable(result, next, itr):
    if isinstance(next, StringElem):
        return next, itr.next()
    else:
        return result, next

def process_placeable(placeable, next, chunk_seq):
    """Get all text appearing after """
    text, next          = collect_text(u'', next, chunk_seq)
    child_dom_node      = _placeable_dictionary[placeable.__class__](placeable)
    child_dom_node.tail = text
    if placeable.subelems is not None:
        insert_into_dom(child_dom_node, placeable.subelems)
    return child_dom_node, next

def insert_into_dom(dom_node, chunk_seq):
    """Enumerate the elements of chunk_seq, adding text and placeable
    nodes to dom_node."""

    chunk_seq = end_with_eof(chunk_seq)
    dom_node.text, next = collect_text(u'', chunk_seq.next(), chunk_seq)
    if dom_node.text == u'':
        dom_node.text = None
    while next != EOF:
        placeable, next = get_placeable(None, next, chunk_seq)
        if placeable is not None:
            child_dom_node, next = process_placeable(placeable, next, chunk_seq)
            dom_node.append(child_dom_node)
    return dom_node
