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

from lxml import etree

from translate.storage.placeables import base
import translate.storage.placeables.misc as placeables_misc
from translate.storage.xml_extract import misc

def make_empty_replacement_placeable(klass, node):
    return klass(node.attrib[u'id'])

def make_g_placeable(klass, node):
    return klass(node.attrib[u'id'], extract_chunks(node))

def not_yet_implemented(klass, node):
    raise NotImplementedError

_class_dictionary = { u'bpt': (base.Bpt, not_yet_implemented), 
                      u'bx' : (base.Bx,  make_empty_replacement_placeable), 
                      u'ept': (base.Ept, not_yet_implemented),
                      u'ex' : (base.Ex,  make_empty_replacement_placeable),
                      u'g'  : (base.G,   make_g_placeable), 
                      u'it' : (base.It,  not_yet_implemented),
                      u'ph' : (base.Ph,  not_yet_implemented), 
                      u'sub': (base.Sub, not_yet_implemented),
                      u'x'  : (base.X,   make_empty_replacement_placeable) }

def make_placeable(node):
    _namespace, tag = misc.parse_tag(node.tag)
    klass, maker = _class_dictionary[tag]
    return maker(klass, node)

def extract_chunks(dom_node):
    result = []
    if dom_node.text:
        result.append(placeables_misc.as_unicode(dom_node.text))
    for child_dom_node in dom_node:
        result.append(make_placeable(child_dom_node))
        if child_dom_node.tail:
            result.append(placeables_misc.as_unicode(child_dom_node.tail))
    return result

# ==========================================================

def placeable_as_dom_node(placeable, tagname):
    dom_node = etree.Element(tagname)
    dom_node.attrib['id'] = placeable.id
    if placeable.xid is not None:
        dom_node.attrib['xid'] = placeable.xid
    if placeable.rid is not None:
        dom_node.attrib['rid'] = placeable.rid
    return dom_node

_placeable_dictionary = { base.Bpt: lambda placeable: placeable_as_dom_node(placeable, 'bpt'), 
                          base.Bx : lambda placeable: placeable_as_dom_node(placeable, 'bx'), 
                          base.Ept: lambda placeable: placeable_as_dom_node(placeable, 'ept'),
                          base.Ex : lambda placeable: placeable_as_dom_node(placeable, 'ex'),
                          base.G  : lambda placeable: placeable_as_dom_node(placeable, 'g'), 
                          base.It : lambda placeable: placeable_as_dom_node(placeable, 'it'),
                          base.Ph : lambda placeable: placeable_as_dom_node(placeable, 'ph'), 
                          base.Sub: lambda placeable: placeable_as_dom_node(placeable, 'sub'),
                          base.X  : lambda placeable: placeable_as_dom_node(placeable, 'x') }

class EOF: pass

def end_with_eof(seq):
    for item in seq:
        yield item
    while True:
        yield EOF

def collect_text(text, next, itr):
    text = placeables_misc.as_unicode(text)
    if isinstance(next, (unicode, str)):
        return collect_text(text + placeables_misc.as_unicode(next), itr.next(), itr)
    else:
        return text, next
    
def get_placeable(result, next, itr):
    if isinstance(next, base.Placeable):
        return next, itr.next()
    else:
        return result, next

def process_placeable(placeable, next, chunk_seq):
    """Get all text appearing after """
    text, next          = collect_text(u'', next, chunk_seq)
    child_dom_node      = _placeable_dictionary[placeable.__class__](placeable)
    child_dom_node.tail = text
    if placeable.content is not None:
        insert_into_dom(child_dom_node, placeable.content)
    return child_dom_node, next

def insert_into_dom(dom_node, chunk_seq):
    """Enumerate the elements of chunk_seq, adding text and placeable
    nodes to dom_node."""
    
    chunk_seq = end_with_eof(chunk_seq)
    dom_node.text, next = collect_text(u'', chunk_seq.next(), chunk_seq)
    while next != EOF:
        placeable, next = get_placeable(None, next, chunk_seq)
        if placeable is not None:
            child_dom_node, next = process_placeable(placeable, next, chunk_seq)
            dom_node.append(child_dom_node)
    return dom_node
