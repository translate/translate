#
# Copyright 2009 Zuza Software Foundation
# Copyright 2014 F Wolff
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

from pytest import mark

from translate.storage.placeables import StringElem, base, general, parse, xliff


class TestStringElem:
    ORIGSTR = 'Ģët <a href="http://www.example.com" alt="Ģët &brand;!">&brandLong;</a>'

    def setup_method(self, method):
        self.elem = parse(self.ORIGSTR, general.parsers)

    def test_parse(self):
        assert str(self.elem) == self.ORIGSTR

    def test_tree(self):
        assert len(self.elem.sub) == 4
        assert str(self.elem.sub[0]) == "Ģët "
        assert (
            str(self.elem.sub[1])
            == '<a href="http://www.example.com" alt="Ģët &brand;!">'
        )
        assert str(self.elem.sub[2]) == "&brandLong;"
        assert str(self.elem.sub[3]) == "</a>"

        assert len(self.elem.sub[0].sub) == 1 and self.elem.sub[0].sub[0] == "Ģët "
        assert (
            len(self.elem.sub[1].sub) == 1
            and self.elem.sub[1].sub[0]
            == '<a href="http://www.example.com" alt="Ģët &brand;!">'
        )
        assert (
            len(self.elem.sub[2].sub) == 1 and self.elem.sub[2].sub[0] == "&brandLong;"
        )
        assert len(self.elem.sub[3].sub) == 1 and self.elem.sub[3].sub[0] == "</a>"

    def test_add(self):
        assert self.elem + " " == self.ORIGSTR + " "
        # ... and __radd__() ... doesn't work
        # assert ' ' + self.elem == ' ' + self.ORIGSTR

    def test_contains(self):
        assert "href" in self.elem
        assert "hrȩf" not in self.elem

    def test_getitem(self):
        assert self.elem[0] == "Ģ"
        assert self.elem[2] == "t"

    def test_getslice(self):
        assert self.elem[0:3] == "Ģët"

    def test_iter(self):
        for chunk in self.elem:
            assert issubclass(chunk.__class__, StringElem)

    def test_len(self):
        assert len(self.elem) == len(self.ORIGSTR)

    def test_mul(self):
        assert self.elem * 2 == self.ORIGSTR * 2
        # ... and __rmul__()
        assert 2 * self.elem == 2 * self.ORIGSTR

    def test_elem_offset(self):
        assert self.elem.elem_offset(self.elem.sub[0]) == 0
        assert self.elem.elem_offset(self.elem.sub[1]) == 4

    def test_elem_at_offset(self):
        assert self.elem.elem_at_offset(0) is self.elem.sub[0]
        assert self.elem.elem_at_offset(self.elem.find("!")) is self.elem.sub[1]

    def test_find(self):
        assert self.elem.find("example") == 24
        assert self.elem.find("example") == 24
        searchelem = parse("&brand;", general.parsers)
        assert self.elem.find(searchelem) == 46

    def test_find_elems_with(self):
        assert self.elem.find_elems_with("Ģët") == [self.elem.sub[0], self.elem.sub[1]]
        assert len(self.elem.find_elems_with("a")) == 3

    def test_flatten(self):
        assert "".join(str(i) for i in self.elem.flatten()) == self.ORIGSTR

    def test_delete_range_case1(self):
        # Case 1: Entire string #
        elem = self.elem.copy()
        deleted, parent, offset = elem.delete_range(0, len(elem))
        assert deleted == self.elem
        assert parent is None and offset is None

    def test_delete_range_case2(self):
        # Case 2: An entire element #
        elem = self.elem.copy()
        offset = elem.elem_offset(elem.sub[2])
        deleted, parent, offset = elem.delete_range(offset, offset + len(elem.sub[2]))
        assert deleted == self.elem.sub[2]
        assert parent is elem
        assert offset == len(elem.sub[0]) + len(elem.sub[1])

    def test_delete_range_case3(self):
        # Case 3: Within a single element #
        elem = self.elem.copy()
        deleted, parent, offset = elem.delete_range(1, 2)
        assert deleted == StringElem("ë")
        assert parent is elem.sub[0]
        assert offset == 1

    def test_delete_range_case4(self):
        # Case 4: Across multiple elements #
        elem = self.elem.copy()
        # Delete the last two elements
        deleted, parent, offset = elem.delete_range(
            elem.elem_offset(elem.sub[2]), len(elem)
        )
        assert deleted == self.elem
        assert parent is None
        assert offset is None
        assert len(elem.sub) == 2
        assert str(elem) == 'Ģët <a href="http://www.example.com" alt="Ģët &brand;!">'

        # A separate test case where the delete range include elements between
        # the start- and end elements.
        origelem = parse("foo %s bar", general.parsers)
        elem = origelem.copy()
        assert len(elem.sub) == 3
        deleted, parent, offset = elem.delete_range(3, 7)
        assert deleted == origelem
        assert parent is None
        assert offset is None
        assert str(elem) == "foobar"

    def test_insert(self):
        # Test inserting at the beginning
        elem = self.elem.copy()
        elem.insert(0, "xxx")
        assert str(elem.sub[0]) == "xxx" + str(self.elem.sub[0])

        # Test inserting at the end
        elem = self.elem.copy()
        elem.insert(len(elem), "xxx")
        assert elem.flatten()[-1] == StringElem("xxx")
        assert str(elem).endswith("&brandLong;</a>xxx")

        elem = self.elem.copy()
        elem.insert(len(elem), ">>>", preferred_parent=elem.sub[-1])
        assert str(elem.flatten()[-1]) == "</a>>>>"
        assert str(elem).endswith("&brandLong;</a>>>>")

        # Test inserting in the middle of an existing string
        elem = self.elem.copy()
        elem.insert(2, "xxx")
        assert str(elem.sub[0]) == "Ģëxxxt "

        # Test inserting between elements
        elem = self.elem.copy()
        elem.insert(56, "xxx")
        assert str(elem)[56:59] == "xxx"

    def test_isleaf(self):
        for child in self.elem.sub:
            assert child.isleaf()

    @staticmethod
    def test_prune():
        elem = StringElem("foo")
        child = StringElem("bar")
        elem.sub.append(child)
        elem.prune()
        assert elem == StringElem("foobar")


class TestConverters:
    def setup_method(self, method):
        self.elem = parse(TestStringElem.ORIGSTR, general.parsers)

    def test_to_base_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        # The following asserts say that, even though tree and newtree represent the same string
        # (the unicode() results are the same), they are composed of different classes (and so
        # their repr()s are different
        assert str(self.elem) == str(basetree)
        assert repr(self.elem) != repr(basetree)

    @mark.xfail(reason="Test needs fixing, disabled for now")
    def test_to_general_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        gentree = general.to_general_placeables(basetree)
        assert gentree == self.elem

    @mark.xfail(reason="Test needs fixing, disabled for now")
    def test_to_xliff_placeables(self):
        basetree = base.to_base_placeables(self.elem)
        xliff_from_base = xliff.to_xliff_placeables(basetree)
        assert str(xliff_from_base) != str(self.elem)
        assert repr(xliff_from_base) != repr(self.elem)

        xliff_from_gen = xliff.to_xliff_placeables(self.elem)
        assert str(xliff_from_gen) != str(self.elem)
        assert repr(xliff_from_gen) != repr(self.elem)

        assert str(xliff_from_base) == str(xliff_from_gen)
        assert repr(xliff_from_base) == repr(xliff_from_gen)
