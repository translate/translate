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
        self.origstr = u'Ģët <a href="http://www.example.com" alt="Ģët &brand;!">&brandLong;</a>'
        self.richstr = strelem.parse(self.origstr)

    def test_parse(self):
        assert unicode(self.richstr) == self.origstr

    def test_add(self):
        assert self.richstr + ' ' == self.origstr + ' '
        # ... and __radd__()... doesn't work
        #assert ' ' + self.richstr == ' ' + self.origstr

    def test_contains(self):
        assert 'href' in self.richstr
        assert u'hrȩf' not in self.richstr

    def test_getitem(self):
        assert self.richstr[0] == u'Ģ'
        assert self.richstr[2] == 't'

    def test_getslice(self):
        assert self.richstr[0:3] == u'Ģët'

    def test_iter(self):
        for chunk in self.richstr:
            assert issubclass(chunk.__class__, strelem.StringElem)

    def test_len(self):
        assert len(self.richstr) == len(self.origstr)

    def test_mul(self):
        assert self.richstr * 2 == self.origstr * 2
        # ... and __rmul__()
        assert 2 * self.richstr == 2 * self.origstr

    def test_flatten(self):
        assert u''.join(unicode(i) for i in self.richstr.flatten()) == self.origstr


if __name__ == '__main__':
    test = origstrings()
    for method in dir(test):
        if method.startswith('test_') and callable(getattr(test, method)):
            getattr(test, method)()

    print 'Test string:   %s' % (test.origstr)
    print 'Parsed string: %s' % (str(test.richstr))
    test.richstr.print_tree()
