# -*- coding: utf-8 -*-

from pytest import raises

from translate.misc import wStringIO
from translate.storage import l20n, test_monolingual


class TestL20nUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = l20n.l20nunit

    def test_rich_get(self):
        pass

    def test_rich_set(self):
        pass


class TestL20n(test_monolingual.TestMonolingualStore):
    StoreClass = l20n.l20nfile

    def l20n_parse(self, l20n_source):
        """helper that parses l20n source without requiring files"""
        dummyfile = wStringIO.StringIO(l20n_source)
        l20n_file = l20n.l20nfile(dummyfile)
        return l20n_file

    def l20n_regen(self, l20n_source):
        """helper that converts l20n source to l20nfile object and back"""
        return bytes(self.l20n_parse(l20n_source)).decode('utf-8')

    def test_parse(self):
        """Tests converting to a string and parsing the resulting string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.setid("test-string")
        unit2 = store.addsourceunit("Test String 2")
        unit2.setid("test-string-2")
        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_files(self):
        """Tests saving to and loading from files"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.setid("test-string")
        unit2 = store.addsourceunit("Test String 2")
        unit2.setid("test-string-2")
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_save(self):
        """Tests that we can save directly back to the original file."""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.setid("test-string")
        unit2 = store.addsourceunit("Test String 2")
        unit2.setid("test-string-2")
        store.savefile(self.filename)
        store.save()
        newstore = self.StoreClass.parsefile(self.filename)
        self.check_equality(store, newstore)

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        l20n_source = 'test_me = I can code!'
        l20n_file = self.l20n_parse(l20n_source)
        assert len(l20n_file.units) == 1
        l20n_unit = l20n_file.units[0]
        assert l20n_unit.id == "test_me"
        assert l20n_unit.source == "I can code!"

    def test_simpledefinition_source(self):
        """checks that a simple properties definition can be regenerated as source"""
        l20n_source = 'test_me = I can code!'
        l20n_regen = self.l20n_regen(l20n_source)
        assert l20n_source + '\n' == l20n_regen

    def test_comments(self):
        """checks that we handle # and ! comments"""
        l20n_source = '''# A comment
key = value
'''
        l20n_file = self.l20n_parse(l20n_source)
        print(repr(l20n_source))
        assert len(l20n_file.units) == 1
        l20n_unit = l20n_file.units[0]
        assert l20n_unit.comment == 'A comment'

    def test_source_with_variants(self):
        """checks that we handle l20n value as variants"""
        l20n_source = 'test_me = ' + '''
  [varaint1] I can code!
  [varaint2] I can't code!
'''
        l20n_regen = self.l20n_regen(l20n_source)
        assert l20n_source == l20n_regen

    def test_source_with_traits(self):
        """checks that we handle l20n value as variants"""
        l20n_source = '''test_me = I can code!
  [attr1] value1
  [attr2] value2
'''
        l20n_regen = self.l20n_regen(l20n_source)
        assert l20n_source == l20n_regen
