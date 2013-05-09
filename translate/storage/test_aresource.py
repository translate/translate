#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

from translate.storage import aresource
from translate.storage import test_monolingual


class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

    escape_data = [
        ('message\nwith newline', '<string name="Test String">message\\nwith newline</string>\n\n'),
        ('message \nwith newline in xml', '<string name="Test String">message\n\\nwith newline in xml</string>\n\n'),
        ('@twitterescape', '<string name="Test String">\\@twitterescape</string>\n\n'),
        ('quote \'escape\'', '<string name="Test String">quote \\\'escape\\\'</string>\n\n'),
        ('double  space', '<string name="Test String">"double  space"</string>\n\n'),
        (' leading space', '<string name="Test String">" leading space"</string>\n\n'),
        ('>xml&entities', '<string name="Test String">&gt;xml&amp;entities</string>\n\n'),
        ('some <b>html code</b> here', '<string name="Test String">some <b>html code</b> here</string>\n\n'),
        ('<<< arrow', '<string name="Test String">&lt;&lt;&lt; arrow</string>\n\n'),
    ]

    parse_test_data = escape_data + [
        # Check that double quotes got removed
        ('double quoted text', '<string name="Test String">"double quoted text"</string>\n\n'),
        # Check that newline is read as space (at least it seems to be what Android does)
        ('newline in string', '<string name="Test String">newline\nin string</string>\n\n'),
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
