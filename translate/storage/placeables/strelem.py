#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
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
Contains the base L{StringElem} class that represents a node in a parsed rich-
string tree. It is the base class of all placeables.
"""

import sys


class StringElem(object):
    """
    This class represents a sub-tree of a string parsed into a rich structure.
    It is also the base class of all placeables.
    """

    subelems = []
    """The sub-elements that make up this this string."""
    iseditable = True
    """Whether this string should be changable by the user. Not used at the moment."""
    isvisible = True
    """Whether this string should be visible to the user. Not used at the moment."""

    # INITIALIZERS #
    def __init__(self, subelems=None, id=None, rid=None, xid=None):
        if subelems is None:
            subelems = []

        for elem in subelems:
            if not isinstance(elem, (str, unicode, StringElem)):
                raise ValueError(elem)

        self.subelems   = subelems
        self.id         = id
        self.rid        = rid
        self.xid        = xid

    # SPECIAL METHODS #
    def __add__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) + rhs

    def __contains__(self, item):
        """Emulate the C{unicode} class."""
        return item in unicode(self)

    def __eq__(self, rhs):
        """@returns: C{True} if (and only if) all members as well as sub-trees
            are equal. False otherwise."""
        if not isinstance(rhs, StringElem):
            return False

        return  self.id            == rhs.id            and \
                self.iseditable    == rhs.iseditable    and \
                self.isvisible     == rhs.isvisible     and \
                self.rid           == rhs.rid           and \
                self.xid           == rhs.xid           and \
                len(self.subelems) == len(rhs.subelems) and \
                not [i for i in range(len(self.subelems)) if self.subelems[i] != rhs.subelems[i]]

    def __ge__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) >= rhs

    def __getitem__(self, i):
        """Emulate the C{unicode} class."""
        return unicode(self)[i]

    def __getslice__(self, i, j):
        """Emulate the C{unicode} class."""
        return unicode(self)[i:j]

    def __gt__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) > rhs

    def __iter__(self):
        """Create an iterator of this element's sub-elements."""
        for elem in self.subelems:
            yield elem

    def __le__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) <= rhs

    def __len__(self):
        """Emulate the C{unicode} class."""
        return len(unicode(self))

    def __lt__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) < rhs

    def __mul__(self, rhs):
        """Emulate the C{unicode} class."""
        return unicode(self) * rhs

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __radd__(self, lhs):
        """Emulate the C{unicode} class."""
        return self + lhs

    def __rmul__(self, lhs):
        """Emulate the C{unicode} class."""
        return self * lhs

    def __repr__(self):
        elemstr = ', '.join([repr(elem) for elem in self.subelems])
        return '<%(class)s(%(id)s%(rid)s%(xid)s[%(subs)s])>' % {
            'class': self.__class__.__name__,
            'id':  self.id  is not None and 'id="%s" '  % (self.id) or '',
            'rid': self.rid is not None and 'rid="%s" ' % (self.rid) or '',
            'xid': self.xid is not None and 'xid="%s" ' % (self.xid) or '',
            'subs': elemstr
        }

    def __str__(self):
        if not self.isvisible:
            return ''
        return ''.join([str(elem) for elem in self.subelems])

    def __unicode__(self):
        if not self.isvisible:
            return u''
        return u''.join([unicode(elem) for elem in self.subelems])

    # METHODS #
    def encode(self, encoding=sys.getdefaultencoding()):
        """More C{unicode} class emulation."""
        return unicode(self).encode(encoding)

    def elem_offset(self, elem):
        """Find the offset of C{elem} in the current tree."""
        flattened = self.flatten()
        if not elem in flattened:
            return -1

        return len(u''.join([unicode(e) for e in flattened[:flattened.index(elem)]]))

    def elem_at_offset(self, offset):
        """Get the C{StringElem} in the tree that contains the string rendered
            at the given offset."""
        if offset < 0 or offset > len(self):
            return None

        length = 0
        elem = None
        for elem in self.flatten():
            elem_len = len(elem)
            if length <= offset < length+elem_len:
                return elem
            length += elem_len
        return elem

    def find(self, x):
        """Find sub-string C{x} in this string tree and return the position
            at which it starts."""
        if isinstance(x, basestring):
            return unicode(self).find(x)
        if isinstance(x, StringElem):
            return unicode(self).find(unicode(x))
        return None

    def find_elems_with(self, x):
        """Find all elements in the current sub-tree containing C{x}."""
        return [elem for elem in self.flatten() if x in unicode(elem)]

    def flatten(self):
        """Flatten the tree by returning a depth-first search over the tree's leaves."""
        subelems = []
        for elem in self.subelems:
            if not isinstance(elem, StringElem):
                continue

            if len(elem.subelems) > 1:
                subelems.extend(elem.flatten())
            else:
                subelems.append(elem)
        return subelems

    def depth_first(self):
        elems = [self]
        for sub in self.subelems:
            if isinstance(sub, StringElem):
                elems.extend(sub.depth_first())
        return elems

    def iter_depth_first(self):
        for elem in self.depth_first():
            yield elem

    @classmethod
    def parse(cls, pstr):
        """Parse an instance of this class from the start of the given string.
            This method should be implemented by any sub-class that wants to
            parseable by L{translate.storage.placeables.parse}.

            @type  pstr: unicode
            @param pstr: The string to parse into an instance of this class.
            @returns: An instance of the current class, or C{None} if the
                string not parseable by this class."""
        return cls(pstr)

    def print_tree(self, indent=0):
        """Print the tree from the current instance's point in an indented
            manner."""
        indent_prefix = " " * indent * 2
        print "%s%s [%s]" % (indent_prefix, self.__class__.__name__, unicode(self))
        for elem in self.subelems:
            if isinstance(elem, StringElem):
                elem.print_tree(indent+1)
            else:
                print '%s%s[%s]' % (indent_prefix, indent_prefix, elem)

    def transform(self, *args, **kwargs):
        """Transform the sub-tree according to some class-specific needs.
            This method should be either overridden in implementing sub-classes
            or dynamically replaced by specific applications.

            @returns: The transformed Unicode string representing the sub-tree.
            """
        return u''.join([elem.translate(*args, **kwargs) for elem in self.subelems])
