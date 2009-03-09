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

from translate.storage.placeables import base, general, parse, xliff, StringElem


class TestStringElem:
    ORIGSTR = u'Ģët <a href="http://www.example.com" alt="Ģët &brand;!">&brandLong;</a>'

    def __init__(self):
        self.elem = parse(self.ORIGSTR, general.parsers)

    def test_parse(self):
        assert unicode(self.elem) == self.ORIGSTR

    def test_tree(self):
        assert len(self.elem.subelems) == 4
        assert unicode(self.elem.subelems[0]) == u'Ģët '
        assert unicode(self.elem.subelems[1]) == u'<a href="http://www.example.com" alt="Ģët &brand;!">'
        assert unicode(self.elem.subelems[2]) == u'&brandLong;'
        assert unicode(self.elem.subelems[3]) == u'</a>'

        assert len(self.elem.subelems[0].subelems) == 1 and self.elem.subelems[0].subelems[0] == u'Ģët '
        assert len(self.elem.subelems[1].subelems) == 3
        assert len(self.elem.subelems[2].subelems) == 1 and self.elem.subelems[2].subelems[0] == u'&brandLong;'
        assert len(self.elem.subelems[3].subelems) == 1 and self.elem.subelems[3].subelems[0] == u'</a>'

        subelems = self.elem.subelems[1].subelems # That's the "<a href... >" part
        assert unicode(subelems[0]) == u'<a href="http://www.example.com" '
        assert unicode(subelems[1]) == u'alt="Ģët &brand;!"'
        assert unicode(subelems[2]) == u'>'

        subelems = self.elem.subelems[1].subelems[1].subelems # The 'alt="Ģët &brand;!"' part
        assert len(subelems) == 3
        assert unicode(subelems[0]) == u'alt="Ģët '
        assert unicode(subelems[1]) == u'&brand;'
        assert unicode(subelems[2]) == u'!"'

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
            assert issubclass(chunk.__class__, StringElem)

    def test_len(self):
        assert len(self.elem) == len(self.ORIGSTR)

    def test_mul(self):
        assert self.elem * 2 == self.ORIGSTR * 2
        # ... and __rmul__()
        assert 2 * self.elem == 2 * self.ORIGSTR

    def test_elem_at_offset(self):
        assert self.elem.elem_at_offset(0) is self.elem.subelems[0]
        assert self.elem.elem_at_offset(self.elem.find('!')) is self.elem.subelems[1].subelems[1].subelems[2]

    def test_find(self):
        assert self.elem.find('example') == 24
        assert self.elem.find(u'example') == 24
        searchelem = parse('&brand;', general.parsers)
        assert self.elem.find(searchelem) == 46

    def test_find_elems_with(self):
        assert self.elem.find_elems_with(u'Ģët') == [ StringElem([u'Ģët ']), StringElem([u'alt="Ģët ']) ]
        assert len(self.elem.find_elems_with('a')) == 5

    def test_flatten(self):
        assert u''.join([unicode(i) for i in self.elem.flatten()]) == self.ORIGSTR


class TestConverters:
    def __init__(self):
        self.elem = parse(TestStringElem.ORIGSTR, general.parsers)

    def test_to_base_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        # The following asserts say that, even though tree and newtree represent the same string
        # (the unicode() results are the same), they are composed of different classes (and so
        # their repr()s are different
        assert unicode(self.elem) == unicode(basetree)
        assert repr(self.elem) != repr(basetree)

    def test_to_general_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        gentree = general.to_general_placeables(basetree)
        assert gentree == self.elem

    def test_to_xliff_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        xliff_from_base = xliff.to_xliff_placeables(basetree)
        assert unicode(xliff_from_base) != unicode(self.elem)
        assert repr(xliff_from_base) != repr(self.elem)

        xliff_from_gen = xliff.to_xliff_placeables(self.elem)
        assert unicode(xliff_from_gen) != unicode(self.elem)
        assert repr(xliff_from_gen) != repr(self.elem)

        assert unicode(xliff_from_base) == unicode(xliff_from_gen)
        assert repr(xliff_from_base) == repr(xliff_from_gen)


if __name__ == '__main__':
    for test in [TestStringElem(), TestConverters()]:
        for method in dir(test):
            if method.startswith('test_') and callable(getattr(test, method)):
                getattr(test, method)()

    test.elem.print_tree()
