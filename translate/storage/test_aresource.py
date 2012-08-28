#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py import test
from py.test import deprecated_call

from translate.misc import wStringIO
from translate.storage import aresource
from translate.storage import test_monolingual

class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

class TestProp(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.AndroidResourceFile

    def test_parse(self):
        """Tests converting to a string and parsing the resulting string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        newstore = self.reparse(store)
        self.check_equality(store, newstore)

