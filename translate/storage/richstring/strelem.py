#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
#
# This file is part of Virtaal.
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


class StringElem(unicode):
    chunks = []
    """The sub-elements that make up this this string."""
    iseditable = True
    """Whether this string should be changable by the user."""
    isvisible = True
    """Whether this string should be visible to the user."""

    # INITIALIZERS #
    def __init__(self, *args, **kwargs):
        super(StringElem, self).__init__()
        for elem in args:
            if not isinstance(elem, (str, unicode, StringElem)):
                raise ValueError(elem)
        self.chunks = args

        self.iseditable = kwargs.get('iseditable', True)
        self.isvisible = kwargs.get('isvisible', True)

    def __new__(cls, *args, **kwargs):
        # This is necessary to override str.__new__(), which can't handle extra parameters
        instance = super(StringElem, cls).__new__(cls)
        return instance

    # SPECIAL METHODS #
    def __add__(self, rhs):
        return unicode(self) + rhs

    def __contains__(self, item):
        return item in unicode(self)

    def __ge__(self, rhs):
        return unicode(self) >= rhs

    def __getitem__(self, i):
        return unicode(self)[i]

    def __getslice__(self, i, j):
        return unicode(self)[i:j]

    def __gt__(self, rhs):
        return unicode(self) > rhs

    def __iter__(self):
        for chunk in self.chunks:
            yield chunk

    def __le__(self, rhs):
        return unicode(self) <= rhs

    def __len__(self):
        return len(unicode(self))

    def __lt__(self, rhs):
        return unicode(self) < rhs

    def __mul__(self, rhs):
        return unicode(self) * rhs

    def __radd__(self, lhs):
        return self + lhs

    def __rmul__(self, lhs):
        return self * lhs

    def __repr__(self):
        chunkstr = ', '.join([repr(chunk) for chunk in self.chunks])
        return '<%s([%s])>' % (self.__class__.__name__, chunkstr)

    def __str__(self):
        if not self.isvisible:
            return ''
        return ''.join([unicode(chunk).encode('utf-8') for chunk in self.chunks])

    def __unicode__(self):
        if not self.isvisible:
            return u''
        return u''.join([unicode(chunk) for chunk in self.chunks])

    # METHODS #
    def flatten(self):
        """Flatten the tree by returning a depth-first search over the tree."""
        chunks = []
        for chunk in self.chunks:
            if not isinstance(chunk, StringElem):
                continue

            if len(chunk.chunks) > 1:
                chunks.extend(chunk.flatten())
            else:
                chunks.append(chunk)
        return chunks

    @classmethod
    def parse(cls, pstr):
        """Parse an instance of this class from the start of the given string.
            @type  pstr: unicode
            @param pstr: The string to parse into an instance of this class.
            @returns: An instance of the current class, or C{None} if the
                string not parseable by this class."""
        return cls(pstr)

    def print_tree(self, indent=0):
        """Print the tree from the current instance's point in an indented
            manner."""
        indent_prefix = " " * indent * 2
        print "%s%s [%s]" % (indent_prefix, self.__class__.__name__, str(self))
        for chunk in self.chunks:
            if isinstance(chunk, StringElem):
                chunk.print_tree(indent+1)
            else:
                print '%s%s[%s]' % (indent_prefix, indent_prefix, chunk)

    def translate(self, *args, **kwargs):
        return u''.join([chunk.translate(*args, **kwargs) for chunk in self.chunks])


class GenericPlaceable(StringElem):
    parse = None
    def __init__(self, *args):
        super(GenericPlaceable, self).__init__(iseditable=False, *args)


class InvisiblePlaceable(StringElem):
    parse = None
    def __init__(self, *args):
        super(InvisiblePlaceable, self).__init__(iseditable=False, isvisible=False, *args)


class AltAttrPlaceable(GenericPlaceable):
    @classmethod
    def parse(cls, pstr):
        """@see: StringElem.parse"""
        if pstr.startswith('alt="') and pstr.find('"', 5) > 0:
            return cls(pstr[:pstr.find('"', 5)+1])
        return None


class XMLElementPlaceable(GenericPlaceable):
    @classmethod
    def parse(cls, pstr):
        """@see: StringElem.parse"""
        if pstr.startswith('&') and pstr.index(';') > 0:
            return cls(pstr[:pstr.index(';')+1])
        return None


class XMLTagPlaceable(GenericPlaceable):
    @classmethod
    def parse(cls, pstr):
        """@see: StringElem.parse"""
        if pstr.startswith('<') and pstr.index('>') > 0:
            bracket_count = 0
            for i in range(len(pstr)):
                if pstr[i] == '>':
                    i += 1
                    bracket_count -= 1
                elif pstr[i] == '<':
                    bracket_count += 1
                if bracket_count == 0:
                    break
            if i <= len(pstr):
                return cls(pstr[:i])
            return None


parsers = []
for local in locals().values():
    if hasattr(local, '__bases__') and issubclass(local, StringElem) and local is not StringElem and local.parse is not None:
        parsers.append(local.parse)

def parse(parsable_string, parse_funcs=parsers, i=0):
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
                    elements.append(StringElem(parsable_string[last_used:i]))

                subtree = parse(unicode(elem), i=1)
                if len(subtree.chunks) > 1:
                    elem.chunks = subtree.chunks
                elements.append(elem)

                i += len(elem)
                last_used = i
                break

        if not elem_parsed:
            i += 1

    if last_used < len(parsable_string):
        elements.append(StringElem(parsable_string[last_used:]))

    return StringElem(*elements)
