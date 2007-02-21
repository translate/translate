#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for storage base classes"""

from translate.storage import base
from py import test
import os

def test_force_override():
    """Tests that derived classes are not allowed to call certain functions"""
    class BaseClass:
        def test(self):
            base.force_override(self.test, BaseClass)
            return True
        def classtest(cls):
            base.force_override(cls.classtest, BaseClass)
            return True
        classtest = classmethod(classtest)
    class DerivedClass(BaseClass):
        pass
    baseobject = BaseClass()
    assert baseobject.test()
    assert baseobject.classtest()
    derivedobject = DerivedClass()
    assert test.raises(NotImplementedError, derivedobject.test)
    assert test.raises(NotImplementedError, derivedobject.classtest)

class TestTranslationUnit:
    """Tests a TranslationUnit.
    Derived classes can reuse these tests by pointing UnitClass to a derived Unit"""
    UnitClass = base.TranslationUnit

    def setup_method(self, method):
        self.unit = self.UnitClass("Test String")

    def test_isfuzzy(self):
        """Test that we can call isfuzzy() on a unit.
        
        The default return value for isfuzzy() should be False.
        """
        assert not self.unit.isfuzzy()

    def test_create(self):
        """tests a simple creation with a source string"""
        unit = self.UnitClass("Test String")
        assert unit.source == "Test String"

    def test_eq(self):
        """tests equality comparison"""
        unit1 = self.UnitClass("Test String")
        unit2 = self.UnitClass("Test String")
        unit3 = self.UnitClass("Test String")
        unit4 = self.UnitClass("Blessed String")
        unit5 = self.UnitClass("Blessed String")
        unit6 = self.UnitClass("Blessed String")
        assert unit1 == unit1
        assert unit1 == unit2
        assert unit1 != unit4
        unit1.settarget("Stressed Ting")
        unit2.settarget("Stressed Ting")
        unit5.settarget("Stressed Bling")
        unit6.settarget("Stressed Ting")
        assert unit1 == unit2
        assert unit1 != unit3
        assert unit4 != unit5
        assert unit1 != unit6

    def test_target(self):
        unit = self.UnitClass("Test String")
        assert not unit.target
        unit.settarget("Stressed Ting")
        assert unit.target == "Stressed Ting"
        unit.settarget("Stressed Bling")
        assert unit.target == "Stressed Bling"
        unit.settarget("")
        assert unit.target == ""

    def test_escapes(self):
        """Test all sorts of characters that might go wrong in a quoting and 
        escaping roundtrip."""
        unit = self.UnitClass('bla')
        specials = ['Fish & chips', 'five < six', 'six > five', 'five &lt; six',
                    'Use &nbsp;', 'Use &amp;nbsp;', 'Use &amp;amp;nbsp;'
                    'A "solution"', "skop 'n bal", '"""', "'''", u'µ',
                    '\n', '\t', '\r', '\r\n', '\\r', '\\', '\\\r'] 
        for special in specials:
            unit.source = special
            print "unit.source:", repr(unit.source)
            print "special:", repr(special)
            assert unit.source == special

    def test_difficult_escapes(self):
        """Test difficult characters that might go wrong in a quoting and 
        escaping roundtrip."""

        unit = self.UnitClass('bla')
        specials = ['\\n', '\\t', '\\"', '\\ ',
                    '\\\n', '\\\t', '\\\\n', '\\\\t', '\\\\r', '\\\\"',
                    '\\r\\n', '\\\\r\\n', '\\r\\\\n', '\\\\n\\\\r']
        for special in specials:
            unit.source = special
            print "unit.source:", repr(unit.source) + '|'
            print "special:", repr(special) + '|'
            assert unit.source == special

    def test_markreview(self):
        """Tests if we can mark the unit to need review."""
        unit = self.UnitClass("Test String")
        # We have to explicitly set the target to nothing, otherwise xliff
        # tests will fail.
        # Can we make it default behavior for the UnitClass?
        unit.target = ""

        unit.addnote("Test note 1", origin="translator")
        unit.addnote("Test note 2", origin="translator")
        original_notes = unit.getnotes(origin="translator")

        # The base class methods won't be implemented:
        if self.__module__.endswith('test_base'):
            assert test.raises(NotImplementedError, unit.markreviewneeded) 
            return

        assert not unit.isreview()
        unit.markreviewneeded()
        assert unit.isreview()
        unit.markreviewneeded(False)
        assert not unit.isreview()
        assert unit.getnotes(origin="translator") == original_notes
        unit.markreviewneeded(explanation="Double check spelling.")
        assert unit.isreview()
        notes = unit.getnotes(origin="translator")
        assert notes.count("Double check spelling.") == 1

    def test_note_sanity(self):
        """Tests that all subclasses of the base behaves consistently with regards to notes."""
        unit = self.UnitClass("Test String")

        unit.addnote("Test note 1", origin="translator")
        unit.addnote("Test note 2", origin="translator")
        unit.addnote("Test note 3", origin="translator")
        expected_notes = u"Test note 1\nTest note 2\nTest note 3"
        actual_notes = unit.getnotes(origin="translator")
        assert actual_notes == expected_notes

        # Test with no origin.
        unit.removenotes()
        assert not unit.getnotes()
        unit.addnote("Test note 1")
        unit.addnote("Test note 2")
        unit.addnote("Test note 3")
        expected_notes = u"Test note 1\nTest note 2\nTest note 3"
        actual_notes = unit.getnotes()
        assert actual_notes == expected_notes

    def test_errors(self):
        """Tests that we can add and retrieve error messages for a unit."""
        unit = self.UnitClass("Test String")

        # The base class methods won't be implemented:
        if self.__module__.endswith('test_base'):
            assert test.raises(NotImplementedError, unit.markreviewneeded) 
            return

        assert len(unit.geterrors()) == 0
        unit.adderror(errorname='test1', errortext='Test error message 1.')
        unit.adderror(errorname='test2', errortext='Test error message 2.')
        unit.adderror(errorname='test3', errortext='Test error message 3.')
        assert len(unit.geterrors()) == 3
        assert unit.geterrors()['test1'] == 'Test error message 1.'
        assert unit.geterrors()['test2'] == 'Test error message 2.'
        assert unit.geterrors()['test3'] == 'Test error message 3.'
        unit.adderror(errorname='test1', errortext='New error 1.')
        assert unit.geterrors()['test1'] == 'New error 1.'

class TestTranslationStore:
    """Tests a TranslationStore.
    Derived classes can reuse these tests by pointing StoreClass to a derived Store"""
    StoreClass = base.TranslationStore

    def setup_method(self, method):
        """Allocates a unique self.filename for the method, making sure it doesn't exist"""
        self.filename = "%s_%s.test" % (self.__class__.__name__, method.__name__)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def teardown_method(self, method):
        """Makes sure that if self.filename was created by the method, it is cleaned up"""
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_create_blank(self):
        """Tests creating a new blank store"""
        store = self.StoreClass()
        assert len(store.units) == 0

    def test_add(self):
        """Tests adding a new unit with a source string"""
        store = self.StoreClass()
        unit = store.addsourceunit("Test String")
        print str(unit)
        print str(store)
        assert len(store.units) == 1
        assert unit.source == "Test String"

    def test_find(self):
        """Tests searching for a given source string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        assert store.findunit("Test String") == unit1
        assert store.findunit("Blessed String") == unit2
        assert store.findunit("Nest String") is None

    def test_translate(self):
        """Tests the translate method and non-ascii characters."""
        store = self.StoreClass()
        unit = store.addsourceunit("scissor")
        unit.target = u"skêr"
        unit = store.addsourceunit(u"Beziér curve")
        unit.target = u"Beziér-kurwe"
        assert store.translate("scissor") == u"skêr"
        assert store.translate(u"Beziér curve") == u"Beziér-kurwe"

    def reparse(self, store):
        """converts the store to a string and back to a store again"""
        storestring = str(store)
        newstore = self.StoreClass.parsestring(storestring)
        return newstore

    def check_equality(self, store1, store2):
        """asserts that store1 and store2 are the same"""
        assert len(store1.units) == len(store2.units)
        for n, store1unit in enumerate(store1.units):
            store2unit = store2.units[n]
            match = store1unit == store2unit
            if not match:
                print "match failed between elements %d of %d" % (n+1, len(store1.units))
                print "store1:"
                print str(store1)
                print "store2:"
                print str(store2)
                print "store1.units[%d].__dict__:" % n, store1unit.__dict__
                print "store2.units[%d].__dict__:" % n, store2unit.__dict__
                assert store1unit == store2unit

    def test_parse(self):
        """Tests converting to a string and parsing the resulting string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_files(self):
        """Tests saving to and loading from files"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_save(self):
        """Tests that we can save directly back to the original file."""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        store.savefile(self.filename)
        store.save()
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_markup(self):
        """Tests that markup survives the roundtrip. Most usefull for xml types."""
        store = self.StoreClass()
        unit = store.addsourceunit("<vark@hok.org> %d keer %2$s")
        unit.target = "bla"
        assert store.translate("<vark@hok.org> %d keer %2$s") == "bla"

    def test_nonascii(self):
        store = self.StoreClass()
        unit = store.addsourceunit(u"Beziér curve")
        string = u"Beziér-kurwe"
        unit.target = string.encode("utf-8")
        answer = store.translate(u"Beziér curve")
        if isinstance(answer, str):
            answer = answer.decode("utf-8")
        assert answer == u"Beziér-kurwe"
        #Just test that __str__ doesn't raise exception:
        src = str(store)

    def test_store_stats(self):
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test source")
        assert unit1.source_wordcount() == 2
        assert store.source_wordcount() == 2
        unit2 = store.addsourceunit("Test source 2")
        assert unit2.source_wordcount() == 3
        assert store.source_wordcount() == 5
        # If the source has also been changed, assume it's a monolingual file.
        if not unit1.source == unit1.target:
            assert store.translated_unitcount() == 0
            assert store.untranslated_unitcount() == 2
            assert store.translated_wordcount() == 0
            assert store.untranslated_wordcount() == 5
        unit1.settarget("Toets bron teks")
        # If the source has also been changed, assume it's a monolingual file.
        if not unit1.source == unit1.target:
            assert store.translated_unitcount() == 1
            assert store.untranslated_unitcount() == 1
            assert store.translated_wordcount() == 2
            assert store.untranslated_wordcount() == 3

        assert store.fuzzy_units() == 0
        unit1.markfuzzy(True)
        if unit1.isfuzzy():
            assert store.fuzzy_units() == 1

        store = self.StoreClass()
        unit1 = store.addsourceunit(u"ភាសា​ខ្មែរ")
        unit2 = store.addsourceunit(u"សាលារៀន")
        assert unit1.source_wordcount() == 2
        assert unit2.source_wordcount() == 1
        assert store.source_wordcount() == 3
