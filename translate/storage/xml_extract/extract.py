#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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

from translate.storage import base
from translate.misc.typecheck import accepts, Self, IsCallable, IsOneOf, Any
from translate.misc.typecheck.typeclasses import Number
from translate.misc.contextlib import contextmanager, nested
from translate.misc.context import with_
from translate.storage.xml_extract import xpath_breadcrumb
from translate.storage.xml_extract import misc

class Translatable(object):
    """A node corresponds to a translatable element. A node may
       have children, which correspond to placeables."""
    @accepts(Self(), Number, unicode)
    def __init__(self, placeable_id, placeable_name): 
        self.placeable_name = placeable_name
        self.placeable_id = placeable_id
        self.placeable_tag_id = 1
        self.source = []
        self.xpath = ""
        self.is_inline = False
        self.dom_node = None

    def _get_placeables(self):
        return [placeable for placeable in self.source if isinstance(placeable, Translatable)]

    placeables = property(_get_placeables)

class ParseState(object):
    """Maintain constants and variables used during the walking of a
    DOM tree (via the function apply)."""
    def __init__(self, no_translate_content_elements, inline_elements = {}):
        self.no_translate_content_elements = no_translate_content_elements
        self.inline_elements = inline_elements
        self.placeable_id = 0
        self.level = 0
        self.is_inline = False
        self.xpath_breadcrumb = xpath_breadcrumb.XPathBreadcrumb()
        self.placeable_name = u"<top-level>"

@accepts(ParseState, unicode)
def make_translatable(state, placeable_name, dom_node, source):
    """Make a Translatable object. If we are in a placeable (this
    is true if state.level > 0, then increase state.placeable by 1
    and return a Translatable with that placeable ID.
    
    Otherwise we are processing a top-level element, and we give
    it a placeable_id of -1."""
    if state.level > 0:
        state.placeable_id += 1
        translatable = Translatable(state.placeable_id, placeable_name)
    else:
        translatable = Translatable(-1, placeable_name)
    translatable.xpath = state.xpath_breadcrumb.xpath
    translatable.dom_node = dom_node
    translatable.source = source
    return translatable

@accepts(etree._Element, ParseState)
def _process_placeable(dom_node, state):
    """Run find_translatable_dom_nodes on the current dom_node"""
    placeable = find_translatable_dom_nodes(dom_node, state)
    # This happens if there were no recognized child tags and thus
    # no translatable is returned. Make a placeable with the name
    # "placeable"
    if len(placeable) == 0:
        return make_translatable(state, u"placeable", dom_node, [])
    # The ideal situation: we got exactly one translateable back
    # when processing this tree.
    elif len(placeable) == 1:
        return placeable[0]
    else:
        raise Exception("BUG: find_translatable_dom_nodes should never return more than a single translatable")

@accepts(etree._Element, ParseState)
def _process_placeables(dom_node, state):
    """Return a list of placeables and list with
    alternating string-placeable objects. The former is
    useful for directly working with placeables and the latter
    is what will be used to build the final translatable string."""

    @contextmanager
    def set_level():
        state.level += 1
        yield state.level
        state.level -= 1
    
    def with_block(level):
        source = []
        for child in dom_node:
            source.extend([_process_placeable(child, state), unicode(child.tail or u"")])
        return source
    # Do the work within a context to ensure that the level is
    # reset, come what may.
    return with_(set_level(), with_block)

@accepts(etree._Element, ParseState)
def _process_translatable(dom_node, state):
    source = [unicode(dom_node.text or u"")] + _process_placeables(dom_node, state)
    translatable = make_translatable(state, state.placeable_name[-1], dom_node, source)
    translatable.is_inline = state.is_inline
    return [translatable]

@accepts(etree._Element, ParseState)
def _process_children(dom_node, state):
    _namespace, tag = misc.parse_tag(dom_node.tag)
    children = [find_translatable_dom_nodes(child, state) for child in dom_node]
    # Flatten a list of lists into a list of elements
    children = [child for child_list in children for child in child_list]
    if len(children) > 1:
        intermediate_translatable = make_translatable(state, tag, dom_node, children)
        return [intermediate_translatable]
    else:
        return children

@accepts(etree._Element, ParseState)
def find_translatable_dom_nodes(dom_node, state):
    namespace, tag = misc.parse_tag(dom_node.tag)

    @contextmanager
    def xpath_set():
        state.xpath_breadcrumb.start_tag(dom_node.tag)
        yield state.xpath_breadcrumb
        state.xpath_breadcrumb.end_tag()
        
    @contextmanager
    def placeable_set():
        old_placeable_name = state.placeable_name
        state.placeable_name = tag
        yield state.placeable_name
        state.placeable_name = old_placeable_name
            
    @contextmanager
    def inline_set():
        old_inline = state.is_inline
        if (namespace, tag) in state.inline_elements:
            state.is_inline = True
        yield state.is_inline
        state.is_inline = old_inline
      
    def with_block(xpath_breadcrumb, placeable_name, is_inline):
        if (namespace, tag) not in state.no_translate_content_elements:
            return _process_translatable(dom_node, state)
        else:
            return _process_children(dom_node, state)            
    return with_(nested(xpath_set(), placeable_set(), inline_set()), with_block)

@accepts(base.TranslationUnit, Translatable)
def _add_location_and_ref_info(unit, translatable):
    """Add location information to 'unit' which is used to disambiguate
    different units and to find the position of the source text in the
    original XML document"""
    unit.addlocation(translatable.xpath)
    if translatable.placeable_id > -1:
        unit.addnote("References: %d" % translatable.placeable_id)
    return unit

@accepts(Translatable)
def _to_string(translatable):
    """Convert a Translatable to an XLIFF string representation."""
    result = []
    for chunk in translatable.source:
        if isinstance(chunk, unicode):
            result.append(chunk)
        else:
            if chunk.is_inline:
                result.extend([u'<g id="%s">' % chunk.placeable_id, _to_string(chunk), u'</g>'])
            else:
                result.append(u'<x id="%s"/>' % chunk.placeable_id)
    return u''.join(result)

@accepts(base.TranslationStore, Translatable)
def _add_translatable_to_store(store, translatable):
    """Construct a new translation unit, set its source and location
    information and add it to 'store'.
    """
    unit = store.UnitClass(_to_string(translatable))
    unit = _add_location_and_ref_info(unit, translatable)
    store.addunit(unit)

@accepts(Translatable)
def _contains_translatable_text(translatable):
    """Checks whether translatable contains any chunks of text which contain
    more than whitespace.
    
    If not, then there's nothing to translate."""
    for chunk in translatable.source:
        if isinstance(chunk, unicode):
            if chunk.strip() != u"":
                return True
    return False

@accepts(base.TranslationStore)
def _make_store_adder(store):
    """Return a function which, when called with a Translatable will add
    a unit to 'store'. The placeables will represented as strings according
    to 'placeable_quoter'."""    
    def add_to_store(translatable):
        if _contains_translatable_text(translatable) and not translatable.is_inline:
            _add_translatable_to_store(store, translatable)
    
    return add_to_store

@accepts([Translatable], IsCallable())
def _walk_translatable_tree(translatables, f):
    """"""
    for translatable in translatables:
        f(translatable)
        _walk_translatable_tree(translatable.placeables, f)

@accepts(lambda obj: hasattr(obj, "read"), base.TranslationStore, IsOneOf(IsCallable(), type(None)))
def build_store(odf_file, store, parse_state, store_adder = None):
    """Utility function for loading xml_filename"""    
    store_adder = store_adder or _make_store_adder(store)
    tree = etree.parse(odf_file)
    root = tree.getroot()
    translatables = find_translatable_dom_nodes(root, parse_state)
    _walk_translatable_tree(translatables, store_adder)
    return tree
