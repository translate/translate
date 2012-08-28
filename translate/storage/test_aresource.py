#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py import test
from lxml import etree
from py.test import deprecated_call

from translate.misc import wStringIO
from translate.storage import aresource
from translate.storage import test_monolingual

class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

    escape_data = [
        ('message\nwith newline', '<string name="Test String">message\\nwith newline</string>\n\n'),
        ('@twitterescape', '<string name="Test String">\\@twitterescape</string>\n\n'),
        ('quote \'escape\'', '<string name="Test String">quote \\\'escape\\\'</string>\n\n'),
    ]

    parse_test_data = escape_data + [
        ('double quoted text', '<string name="Test String">"double quoted text"</string>\n\n'),
    ]

    def test_escape(self):
        unit = self.unit
        for string, xml in self.escape_data:
            unit = self.UnitClass("Test String")
            unit.target = string
            print "unit.target:", repr(unit.target)
            print "xml:", repr(xml)
            assert str(unit) == xml

    def test_parse(self):
        if etree.LXML_VERSION >= (2, 1, 0):
            #Since version 2.1.0 we can pass the strip_cdata parameter to
            #indicate that we don't want cdata to be converted to raw XML
            parser = etree.XMLParser(strip_cdata=False)
        else:
            parser = etree.XMLParser()
        for string, xml in self.parse_test_data:
            et = etree.fromstring(xml, parser)
            unit = self.UnitClass.createfromxmlElement(et)
            print "unit.target:", repr(unit.target)
            print "string:", string
            assert unit.target == string

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

