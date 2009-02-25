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

"""
Contains the C{parse} function that parses normal strings into StringElem-
based "rich" string element trees.
"""

from translate.storage.placeables import placeables, StringElem


default_parsers = []
for attr in dir(placeables):
    pclass = getattr(placeables, attr)
    if  hasattr(pclass, '__bases__')   and \
        issubclass(pclass, StringElem) and \
        pclass       is not StringElem and \
        pclass.parse is not None:
        default_parsers.append(pclass.parse)

def parse(parsable_string, parse_funcs=default_parsers, i=0):
    """Parse the given string into a tree of string elements.

        @type  parsable_string: unicode
        @param parsable_string: The string to parse. Preferably in Unicode.
        @type  parse_funcs: list
        @param parse_funcs: A list of functions that meet the following
            cirteria:
            * Takes a single string parameter
            * Parses only at the beginning of the string
            * Returns a L{StringElem} (or sub-class) instance that represents
                exactly the sub-string parsed by the function.
            * Returns C{None} if the parser could not find a parseable sub-
                string at the start of the given string.

            These functions are ideally the sub-class implementations of
            C{StringElem.parse}."""
    elements = []
    last_used = 0
    while i < len(parsable_string):
        elem_parsed = False

        for parser in parse_funcs:
            elem = parser(parsable_string[i:])
            if unicode(elem) == parsable_string:
                return elem
            if elem is not None:
                elem_parsed = True
                if parsable_string[last_used:i]:
                    elements.append(StringElem([parsable_string[last_used:i]]))

                subtree = parse(unicode(elem), i=1)
                if len(subtree.subelems) > 1:
                    elem.subelems = subtree.subelems
                elements.append(elem)

                i += len(elem)
                last_used = i
                break

        if not elem_parsed:
            i += 1

    if last_used < len(parsable_string):
        elements.append(StringElem([parsable_string[last_used:]]))

    return StringElem(elements)
