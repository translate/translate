#
# Copyright 2006-2009 Zuza Software Foundation
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

"""Helper functions for working with XML."""

import re

from lxml import etree


# some useful xpath expressions
xml_preserve_ancestors = etree.XPath(
    "ancestor-or-self::*[attribute::xml:space='preserve']"
)
"""All ancestors with xml:space='preserve'"""

xml_space_ancestors = etree.XPath("ancestor-or-self::*/attribute::xml:space")
"""All xml:space attributes in the ancestors"""

string_xpath = etree.XPath("string()")
"""Return a non-normalized string in the node subtree"""

string_xpath_normalized = etree.XPath("normalize-space()")
"""Return a (space) normalized string in the node subtree"""


def getText(node, xml_space="preserve"):
    """Extracts the plain text content out of the given node.

    This method checks the xml:space attribute of the given node, and takes an
    optional default to use in case nothing is specified in this node.
    """
    xml_space = getXMLspace(node, xml_space)
    if xml_space == "default":
        return str(string_xpath_normalized(node))  # specific to lxml.etree
    else:
        return str(string_xpath(node))  # specific to lxml.etree

    # If we want to normalise space and only preserve it when the directive
    # xml:space="preserve" is given in node or in parents, consider this code:
    # xml_preserves = xml_preserve_ancestors(node)
    # if xml_preserves and xml_preserves[-1] == "preserve":
    #    return unicode(string_xpath(node)) # specific to lxml.etree
    # else:
    #    return unicode(string_xpath_normalized(node)) # specific to lxml.etree


XML_NS = "http://www.w3.org/XML/1998/namespace"


def getXMLlang(node):
    """Gets the xml:lang attribute on node"""
    return node.get("{%s}lang" % XML_NS)


def setXMLlang(node, lang):
    """Sets the xml:lang attribute on node"""
    node.set("{%s}lang" % XML_NS, lang)


def getXMLspace(node, default=None):
    """Gets the xml:space attribute on node"""
    value = node.get("{%s}space" % XML_NS)
    if value is None:
        return default
    return value


def setXMLspace(node, value):
    """Sets the xml:space attribute on node"""
    node.set("{%s}space" % XML_NS, value)


def namespaced(namespace, name):
    """Returns name in Clark notation within the given namespace.

    For example namespaced("source") in an XLIFF document might return::

      {urn:oasis:names:tc:xliff:document:1.1}source

    This is needed throughout lxml.
    """
    if namespace:
        return f"{{{namespace}}}{name}"
    return name


MULTIWHITESPACE_PATTERN = r"[\n\r\t ]+"
MULTIWHITESPACE_RE = re.compile(MULTIWHITESPACE_PATTERN, re.MULTILINE)


def normalize_space(text):
    """Normalize the given text for implementation of ``xml:space="default"``."""
    return MULTIWHITESPACE_RE.sub(" ", text)


def normalize_xml_space(node, xml_space, remove_start=False):
    """normalize spaces following the nodes xml:space, or alternatively the
    given xml_space parameter.
    """
    xml_space = getXMLspace(node) or xml_space
    if xml_space == "preserve":
        return
    if node.text:
        node.text = normalize_space(node.text)
        if remove_start and node.text[0] == " ":
            node.text = node.text.lstrip()
            remove_start = False
        if len(node.text) > 0 and node.text.endswith(" "):
            remove_start = True
        if len(node) == 0:
            node.text = node.text.rstrip()
    if node.tail:
        node.tail = normalize_space(node.tail)

    for child in node:
        normalize_xml_space(child, remove_start)


def reindent(
    elem, level=0, indent="  ", max_level=4, skip=None, toplevel=True, leaves=None
):
    """Adjust indentation to match specification.

    Each nested tag is identified by indent string, up to
    max_level depth, possibly skipping tags listed in skip.
    """
    if elem.tag is etree.Entity:
        return
    i = "\n" + (indent * level)
    if skip and elem.tag in skip:
        next_level = level
        extra_i = i
    else:
        next_level = level + 1
        extra_i = i + indent
    if len(elem) and level < max_level:
        is_leave = leaves and elem.tag in leaves
        if (
            (not elem.text or not elem.text.strip())
            and getXMLspace(elem) != "preserve"
            and elem[0].tag is not etree.Entity
            and not is_leave
        ):
            elem.text = extra_i
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        if not is_leave:
            for child in elem:
                reindent(child, next_level, indent, max_level, skip, False, leaves)
            if (
                not child.tail or not child.tail.strip()
            ) and child.tag is not etree.Entity:
                child.tail = i
    if toplevel:
        if not elem.tail or not elem.tail.strip():
            elem.tail = ""
    else:
        if not elem.tail or not elem.tail.strip():
            elem.tail = i


def validate_char(c):
    """
    identify valid chars for XML, based on xmlIsChar_ch from
    https://github.com/GNOME/libxml2/blob/master/include/libxml/chvalid.h
    """
    return (0x9 <= ord(c) <= 0xA) or (ord(c) == 0xD) or (0x20 <= ord(c))


def valid_chars_only(s):
    """
    prevent to crash libxml with unexpected chars
    """
    return "".join(ch for ch in s if validate_char(ch))
