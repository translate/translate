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

from translate.storage.placeables import base, xliff, StringElem
from translate.storage.xml_extract import misc

__all__ = ['extract_chunks', 'insert_into_dom']
# Use the above functions as entry points into this module. The rest are used by these functions.


def make_empty_replacement_placeable(klass, node):
    try:
        return klass(id=node.attrib[u'id'])
    except KeyError:
        pass
    return klass()

def make_g_placeable(klass, node):
    return klass(id=node.attrib[u'id'], subelems=extract_chunks(node).subelems)

def not_yet_implemented(klass, node):
    raise NotImplementedError

_class_dictionary = {
    u'bpt': (xliff.Bpt, not_yet_implemented),
    u'bx' : (xliff.Bx,  make_empty_replacement_placeable),
    u'ept': (xliff.Ept, not_yet_implemented),
    u'ex' : (xliff.Ex,  make_empty_replacement_placeable),
    u'g'  : (xliff.G,   make_g_placeable),
    u'it' : (xliff.It,  not_yet_implemented),
    u'ph' : (xliff.Ph,  not_yet_implemented),
    u'sub': (xliff.Sub, not_yet_implemented),
    u'x'  : (xliff.X,   make_empty_replacement_placeable)
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
    if isinstance(dom_node, basestring):
        dom_node = etree.fromstring(dom_node)
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
    xliff.Bpt: lambda placeable: placeable_as_dom_node(placeable, 'bpt'),
    xliff.Bx : lambda placeable: placeable_as_dom_node(placeable, 'bx'),
    xliff.Ept: lambda placeable: placeable_as_dom_node(placeable, 'ept'),
    xliff.Ex : lambda placeable: placeable_as_dom_node(placeable, 'ex'),
    xliff.G  : lambda placeable: placeable_as_dom_node(placeable, 'g'),
    xliff.It : lambda placeable: placeable_as_dom_node(placeable, 'it'),
    xliff.Ph : lambda placeable: placeable_as_dom_node(placeable, 'ph'),
    xliff.Sub: lambda placeable: placeable_as_dom_node(placeable, 'sub'),
    xliff.X  : lambda placeable: placeable_as_dom_node(placeable, 'x'),
    base.Bpt:  lambda placeable: placeable_as_dom_node(placeable, 'bpt'),
    base.Bx :  lambda placeable: placeable_as_dom_node(placeable, 'bx'),
    base.Ept:  lambda placeable: placeable_as_dom_node(placeable, 'ept'),
    base.Ex :  lambda placeable: placeable_as_dom_node(placeable, 'ex'),
    base.G  :  lambda placeable: placeable_as_dom_node(placeable, 'g'),
    base.It :  lambda placeable: placeable_as_dom_node(placeable, 'it'),
    base.Ph :  lambda placeable: placeable_as_dom_node(placeable, 'ph'),
    base.Sub:  lambda placeable: placeable_as_dom_node(placeable, 'sub'),
    base.X  :  lambda placeable: placeable_as_dom_node(placeable, 'x')
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
