#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for storage base classes"""

from translate.misc.multistring import multistring
from translate.storage import base
from translate.storage.placeables import parse as rich_parse
from py import test
import os
import warnings

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
        unit = self.unit
        print 'unit.source:', unit.source
        assert unit.source == "Test String"

    def test_eq(self):
        """tests equality comparison"""
        unit1 = self.unit
        unit2 = self.UnitClass("Test String")
        unit3 = self.UnitClass("Test String")
        unit4 = self.UnitClass("Blessed String")
        unit5 = self.UnitClass("Blessed String")
        unit6 = self.UnitClass("Blessed String")
        assert unit1 == unit1
        assert unit1 == unit2
        assert unit1 != unit4
        unit1.target = "Stressed Ting"
        unit2.target = "Stressed Ting"
        unit5.target = "Stressed Bling"
        unit6.target = "Stressed Ting"
        assert unit1 == unit2
        assert unit1 != unit3
        assert unit4 != unit5
        assert unit1 != unit6

    def test_target(self):
        unit = self.unit
        assert not unit.target
        unit.target = "Stressed Ting"
        assert unit.target == "Stressed Ting"
        unit.target = "Stressed Bling"
        assert unit.target == "Stressed Bling"
        unit.target = ""
        assert unit.target == ""

    def test_escapes(self):
        """Test all sorts of characters that might go wrong in a quoting and 
        escaping roundtrip."""
        unit = self.unit
        specials = ['Fish & chips', 'five < six', 'six > five', 'five &lt; six',
                    'Use &nbsp;', 'Use &amp;nbsp;', 'Use &amp;amp;nbsp;',
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

        unit = self.unit
        specials = ['\\n', '\\t', '\\"', '\\ ',
                    '\\\n', '\\\t', '\\\\n', '\\\\t', '\\\\r', '\\\\"',
                    '\\r\\n', '\\\\r\\n', '\\r\\\\n', '\\\\n\\\\r']
        for special in specials:
            unit.source = special
            print "unit.source:", repr(unit.source) + '|'
            print "special:", repr(special) + '|'
            assert unit.source == special

    def test_note_sanity(self):
        """Tests that all subclasses of the base behaves consistently with regards to notes."""
        unit = self.unit

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

    def test_rich_get(self):
        """Basic test for converting from multistrings to StringElem trees."""
        target_mstr = multistring([u'tėst', u'<b>string</b>'])
        unit = self.UnitClass(multistring([u'a', u'b']))
        unit.target = target_mstr
        elems = unit.target_rich

        if unit.hasplural():
            assert len(elems) == 2
            assert len(elems[0].subelems) == 1
            assert len(elems[1].subelems) == 3

            assert unicode(elems[0]) == target_mstr.strings[0]
            assert unicode(elems[1]) == target_mstr.strings[1]

            assert unicode(elems[1].subelems[0]) == u'<b>'
            assert unicode(elems[1].subelems[1]) == u'string'
            assert unicode(elems[1].subelems[2]) == u'</b>'
        else:
            assert len(elems[0].subelems) == 1
            assert unicode(elems[0]) == target_mstr.strings[0]

    def test_rich_set(self):
        """Basic test for converting from multistrings to StringElem trees."""
        elems = [
            rich_parse(u'Tëst <x>string</x>'),
            rich_parse(u'Another test string.'),
            rich_parse('A non-Unicode string.')
        ]
        unit = self.UnitClass(multistring([u'a', u'b']))
        unit.target_rich = elems

        if unit.hasplural():
            assert unit.target.strings[0] == u'Tëst <x>string</x>'
            assert unit.target.strings[1] == u'Another test string.'
            assert unit.target.strings[2] == 'A non-Unicode string.'
        else:
            assert unit.target == u'Tëst <x>string</x>'

class TestTranslationStore(object):
    """Tests a TranslationStore.
    Derived classes can reuse these tests by pointing StoreClass to a derived Store"""
    StoreClass = base.TranslationStore

    def setup_method(self, method):
        """Allocates a unique self.filename for the method, making sure it doesn't exist"""
        self.filename = "%s_%s.test" % (self.__class__.__name__, method.__name__)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        warnings.resetwarnings()

    def teardown_method(self, method):
        """Makes sure that if self.filename was created by the method, it is cleaned up"""
        if os.path.exists(self.filename):
            os.remove(self.filename)
        warnings.resetwarnings()

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
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_files(self):
        """Tests saving to and loading from files"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_save(self):
        """Tests that we can save directly back to the original file."""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        store.savefile(self.filename)
        store.save()
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_markup(self):
        """Tests that markup survives the roundtrip. Most usefull for xml types."""
        store = self.StoreClass()
        unit = store.addsourceunit("<vark@hok.org> %d keer %2$s")
        assert unit.source == "<vark@hok.org> %d keer %2$s"
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
