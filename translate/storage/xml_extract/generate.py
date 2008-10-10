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

import lxml.etree as etree

from translate.storage import base

from translate.misc.typecheck import accepts, IsCallable, Any
from translate.storage.xml_extract import misc
from translate.storage.xml_extract import extract
from translate.storage.xml_extract import unit_tree

@accepts(etree._Element)
def _get_tag_arrays(dom_node):
    """Return a dictionary indexed by child tag names, where each tag is associated with an array
    of all the child nodes with matching the tag name, in the order in which they appear as children
    of dom_node.
    
    >>> xml = '<a><b></b><c></c><b></b><d/></a>'
    >>> element = etree.fromstring(xml)
    >>> get_tag_arrays(element)
    {'b': [<Element a at 84df144>, <Element a at 84df148>], 'c': [<Element a at 84df120>], 'd': [<Element a at 84df152>]}
    """
    child_dict = {}
    for child in dom_node:
        if child.tag not in child_dict:
            child_dict[child.tag] = []
        child_dict[child.tag].append(child)
    return child_dict

@accepts(etree._Element, unit_tree.XPathTree, extract.Translatable, IsCallable())
def apply_translations(dom_node, unit_node, do_translate):
    tag_array = _get_tag_arrays(dom_node)
    for unit_child_index, unit_child in unit_node.children.iteritems():
        tag, index = unit_child_index
        try:
            dom_child = tag_array[tag][index]
            apply_translations(dom_child, unit_child, do_translate)
        # Raised if tag is not in tag_array. We might want to complain to the
        # user in the future.
        except KeyError:
            pass
        # Raised if index is not in tag_array[tag]. We might want to complain to
        # the user in the future
        except IndexError:
            pass
    # If there is a translation unit associated with this unit_node...
    if unit_node.unit != None:
        # The invoke do_translate on the dom_node and the unit; do_translate
        # should replace the text in dom_node with the text in unit_node.
        do_translate(dom_node, unit_node.unit)

@accepts(IsCallable(), extract.Translatable, vargs=[Any()])
def reduce_unit_tree(f, unit_node, *state):
    return misc.reduce_tree(f, unit_node, unit_node, lambda unit_node: unit_node.placeables, *state)

@accepts(IsCallable(), etree._Element, vargs=[Any()])
def reduce_dom_tree(f, dom_node, *state):
    return misc.reduce_tree(f, dom_node, dom_node, lambda dom_node: dom_node, *state)

@accepts(etree._Element, etree._Element)
def find_dom_root(parent_dom_node, dom_node):
    """@see find_placeable_dom_tree_roots"""
    if dom_node is None or parent_dom_node is None:
        return None
    if dom_node.getparent() == parent_dom_node:
        return dom_node
    elif dom_node.getparent() is None:
        return None
    else:
        return find_dom_root(parent_dom_node, dom_node.getparent())    

@accepts(extract.Translatable)
def find_placeable_dom_tree_roots(unit_node):
    """For an inline placeable, find the root DOM node for the placeable in its
    parent.
    
    Consider the diagram. In this pseudo-ODF example, there is an inline span
    element. However, the span is contained in other tags (which we never process).
    When splicing the template DOM tree (that is, the DOM which comes from 
    the XML document we're using to generate a translated XML document), we'll
    need to move DOM sub-trees around and we need the roots of these sub-trees.
    
    <p> This is text \/                <- Paragraph containing an inline placeable
                     <blah>            <- Inline placeable's root (which we want to find)
                     ...               <- Any number of intermediate DOM nodes
                     <span> bold text  <- The inline placeable's Translatable 
                                          holds a reference to this DOM node    
    """

    def set_dom_root_for_unit_node(parent_unit_node, unit_node, dom_tree_roots):
            dom_tree_roots[unit_node] = find_dom_root(parent_unit_node.dom_node, unit_node.dom_node)
            return dom_tree_roots
    return reduce_unit_tree(set_dom_root_for_unit_node, unit_node, {})
      
@accepts(extract.Translatable, etree._Element)
def _map_source_dom_to_doc_dom(unit_node, source_dom_node):
    """Creating a mapping from the DOM nodes in source_dom_node which correspond to
    placeables, with DOM nodes in the XML document template (this information is obtained
    from unit_node). We are interested in DOM nodes in the XML document template which
    are the roots of placeables. @see the diagram below, as well as 
    find_placeable_dom_tree_roots.
    
    XLIFF Source (below)
    <source>This is text <g> bold text</g> and a footnote<x/></source> 
                         /                                 \________
                        /                                           \
    <p>This is text<blah>...<span> bold text</span>...</blah> and <note>...</note></p>
    Input XML document used as a template (above)
    
    In the above diagram, the XLIFF source DOM node <g> is associated with the XML 
    document DOM node <blah>, whereas the XLIFF source DOM node <x> is associated with
    the XML document DOM node <note>.
    """
    dom_tree_roots = find_placeable_dom_tree_roots(unit_node)
    source_dom_to_doc_dom = {}
  
    def loop(unit_node, source_dom_node):
        for child_unit_node, child_source_dom in zip(unit_node.placeables, source_dom_node):
            source_dom_to_doc_dom[child_source_dom] = dom_tree_roots[child_unit_node]
            loop(child_unit_node, child_source_dom)
    
    loop(unit_node, source_dom_node)
    return source_dom_to_doc_dom

@accepts(etree._Element, etree._Element)
def _map_target_dom_to_source_dom(source_dom_node, target_dom_node):
    def map_id_to_dom_node(parent_node, node, id_to_dom_node):
        if u'id' in node.attrib:
            id_to_dom_node[node.attrib[u'id']] = node
        return id_to_dom_node
    
    id_to_dom_node = reduce_dom_tree(map_id_to_dom_node, target_dom_node, {})
    
    def map_target_dom_to_source_dom_aux(parent_node, node, target_dom_to_source_dom):
        if u'id' in node.attrib and node.attrib[u'id'] in id_to_dom_node:
            target_dom_to_source_dom[id_to_dom_node[node.attrib[u'id']]] = node
        return target_dom_to_source_dom
    
    return reduce_dom_tree(map_target_dom_to_source_dom_aux, source_dom_node, {})

def _build_target_dom_to_doc_dom(unit_node, source_dom, target_dom):
    source_dom_to_doc_dom    = _map_source_dom_to_doc_dom(unit_node, source_dom)
    target_dom_to_source_dom = _map_target_dom_to_source_dom(source_dom, target_dom)
    return misc.compose_mappings(target_dom_to_source_dom, source_dom_to_doc_dom)

@accepts(etree._Element, {etree._Element: etree._Element})
def _get_translated_node(target_node, target_dom_to_doc_dom):
    dom_node = target_dom_to_doc_dom[target_node]
    dom_node.tail = target_node.tail
    return dom_node

@accepts(etree._Element, etree._Element, {etree._Element: etree._Element})
def _build_translated_dom(dom_node, target_node, target_dom_to_doc_dom):
    """
    
    """
    dom_node.text = target_node.text
    dom_node.extend(_get_translated_node(child, target_dom_to_doc_dom) for child in target_node 
                    if target_dom_to_doc_dom[child] is not None)
    for dom_child, target_child in zip(dom_node, target_node):
        _build_translated_dom(dom_child, target_child, target_dom_to_doc_dom)

@accepts(IsCallable())
def replace_dom_text(make_parse_state):
    """Return a function """
    
    @accepts(etree._Element, base.TranslationUnit)
    def action(dom_node, unit):
        """Use the unit's target (or source in the case where there is no translation)
        to update the text in the dom_node and at the tails of its children."""
        source_dom            = etree.fromstring(u'<source>%s</source>' % unicode(unit.source))
        target_dom            = etree.fromstring(u'<target>%s</target>' % unicode(unit.target or unit.source))
        unit_node             = extract.find_translatable_dom_nodes(dom_node, make_parse_state())[0]        
        target_dom_to_doc_dom = _build_target_dom_to_doc_dom(unit_node, source_dom, target_dom)
        
        dom_node[:] = []
        _build_translated_dom(dom_node, target_dom, target_dom_to_doc_dom)

    return action
