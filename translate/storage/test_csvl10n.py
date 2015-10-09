# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pytest import mark

from translate.misc import wStringIO
from translate.storage import csvl10n, test_base


class TestCSVUnit(test_base.TestTranslationUnit):
    UnitClass = csvl10n.csvunit


class TestCSV(test_base.TestTranslationStore):
    StoreClass = csvl10n.csvfile

    def parse_store(self, source):
        """Helper that parses source without requiring files."""
        return self.StoreClass(wStringIO.StringIO(source))

    def test_singlequoting(self):
        """Tests round trip on single quoting at start of string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test 'String'")
        unit2 = store.addsourceunit("'Blessed' String")
        unit3 = store.addsourceunit("'Quoted String'")
        assert unit3.source == "'Quoted String'"
        newstore = self.reparse(store)
        self.check_equality(store, newstore)
        assert store.units[2] == newstore.units[2]
        assert bytes(store) == bytes(newstore)

    def test_utf_8(self):
        store = self.parse_store('foo.c:1;test;zkouška sirén'.encode('utf-8'))
        assert len(store.units) == 1
        assert store.units[0].source == 'test'
        assert store.units[0].target == 'zkouška sirén'

    def test_utf_8_sig(self):
        store = self.parse_store('foo.c:1;test;zkouška sirén'.encode('utf-8-sig'))
        assert len(store.units) == 1
        assert store.units[0].source == 'test'
        assert store.units[0].target == 'zkouška sirén'

    @mark.xfail(reason="Bug #3356")
    def test_context_is_parsed(self):
        """Tests that units with the same source are different based on context."""
        source = ('"65066","Ogre","Ogro"\n'
                  '"65067","Ogre","Ogros"')
        store = self.parse_store(source)
        assert len(store.units) == 2
        unit1 = store.units[0]
        assert unit1.context == "65066"
        assert unit1.source == "Ogre"
        assert unit1.target == "Ogro"
        unit2 = store.units[1]
        assert unit2.context == "65067"
        assert unit2.source == "Ogre"
        assert unit2.target == "Ogros"
        assert unit1.getid() != unit2.getid()
