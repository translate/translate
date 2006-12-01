#!/usr/bin/env python

from translate.storage import csvl10n
from translate.storage import test_base
from translate.misc import wStringIO
from py import test

class TestCSVUnit(test_base.TestTranslationUnit):
    UnitClass = csvl10n.csvunit

    def setup_method(self, method):
        self.unit = self.UnitClass("Test Source String")

    def test_markreview(self):
        assert test.raises(NotImplementedError, self.unit.markreviewneeded)
    
    def test_note_sanity(self):
        """This test should be removed (in favour of the base test)
        as soon as csvunit has a 'notes' attribute."""
        assert test.raises(AttributeError, self.unit.addnote, 'test note')

class TestCSV(test_base.TestTranslationStore):
    StoreClass = csvl10n.csvfile

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
        assert str(store) == str(newstore)

