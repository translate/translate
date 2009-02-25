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
        return ''.join([str(chunk) for chunk in self.chunks])

    def __unicode__(self):
        if not self.isvisible:
            return u''
        return u''.join([str(chunk).decode('utf-8') for chunk in self.chunks])

    # METHODS #
    def flatten(self):
        """Flatten the tree by returning a depth-first search over the tree."""
        pass

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
    def __init__(self, *args):
        super(GenericPlaceable, self).__init__(iseditable=False, *args)


class InvisiblePlaceable(StringElem):
    def __init__(self, *args):
        super(InvisiblePlaceable, self).__init__(iseditable=False, isvisible=False, *args)


class AltAttrPlaceable(GenericPlaceable):
    pass


class XMLElementPlaceable(GenericPlaceable):
    pass


class XMLTagPlaceable(GenericPlaceable):
    pass
