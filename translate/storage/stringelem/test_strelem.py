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

import strelem


class TestStrings:
    def __init__(self):
        self.ORIGSTR = u'Ģët <a href="http://www.example.com" alt="Ģët &brand;!">&brandLong;</a>'
        self.elem = strelem.parse(self.ORIGSTR)

    def test_parse(self):
        assert unicode(self.elem) == self.ORIGSTR

    def test_tree(self):
        assert len(self.elem.chunks) == 4
        assert unicode(self.elem.chunks[0]) == u'Ģët '
        assert unicode(self.elem.chunks[1]) == u'<a href="http://www.example.com" alt="Ģët &brand;!">'
        assert unicode(self.elem.chunks[2]) == u'&brandLong;'
        assert unicode(self.elem.chunks[3]) == u'</a>'

        assert len(self.elem.chunks[0].chunks) == 1 and self.elem.chunks[0].chunks[0] == u'Ģët '
        assert len(self.elem.chunks[1].chunks) == 3
        assert len(self.elem.chunks[2].chunks) == 1 and self.elem.chunks[2].chunks[0] == u'&brandLong;'
        assert len(self.elem.chunks[3].chunks) == 1 and self.elem.chunks[3].chunks[0] == u'</a>'

        chunks = self.elem.chunks[1].chunks # That's the "<a href... >" part
        assert unicode(chunks[0]) == u'<a href="http://www.example.com" '
        assert unicode(chunks[1]) == u'alt="Ģët &brand;!"'
        assert unicode(chunks[2]) == u'>'

        chunks = self.elem.chunks[1].chunks[1].chunks # The 'alt="Ģët &brand;!"' part
        assert len(chunks) == 3
        assert unicode(chunks[0]) == u'alt="Ģët '
        assert unicode(chunks[1]) == u'&brand;'
        assert unicode(chunks[2]) == u'!"'

    def test_add(self):
        assert self.elem + ' ' == self.ORIGSTR + ' '
        # ... and __radd__() ... doesn't work
        #assert ' ' + self.elem == ' ' + self.ORIGSTR

    def test_contains(self):
        assert 'href' in self.elem
        assert u'hrȩf' not in self.elem

    def test_getitem(self):
        assert self.elem[0] == u'Ģ'
        assert self.elem[2] == 't'

    def test_getslice(self):
        assert self.elem[0:3] == u'Ģët'

    def test_iter(self):
        for chunk in self.elem:
            assert issubclass(chunk.__class__, strelem.StringElem)

    def test_len(self):
        assert len(self.elem) == len(self.ORIGSTR)

    def test_mul(self):
        assert self.elem * 2 == self.ORIGSTR * 2
        # ... and __rmul__()
        assert 2 * self.elem == 2 * self.ORIGSTR

    def test_flatten(self):
        assert u''.join(unicode(i) for i in self.elem.flatten()) == self.ORIGSTR


if __name__ == '__main__':
    test = TestStrings()
    for method in dir(test):
        if method.startswith('test_') and callable(getattr(test, method)):
            getattr(test, method)()

    print 'Test string:   %s' % (test.ORIGSTR)
    print 'Parsed string: %s' % (str(test.elem))
    test.elem.print_tree()
