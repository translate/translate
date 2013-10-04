#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

from translate.storage import aresource
from translate.storage import test_monolingual
from translate.misc.multistring import multistring


class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit
    StoreClass = aresource.AndroidResourceFile

    escape_data = [
        ('message\nwith newline', 'message\\nwith newline'),
        ('message \nwith newline in xml', 'message\n\\nwith newline in xml'),
        ('@twitterescape', '\\@twitterescape'),
        ('quote \'escape\'', 'quote \\\'escape\\\''),
        ('double  space', '"double  space"'),
        (' leading space', '" leading space"'),
        ('>xml&entities', '&gt;xml&amp;entities'),
        ('some <b>html code</b> here', 'some <b>html code</b> here'),
        ('<<< arrow', '&lt;&lt;&lt; arrow'),
        ('<a href="http://example.net">link</a>', '<a href="http://example.net">link</a>'),
        ('<a href="http://example.net">link</a> and text', '<a href="http://example.net">link</a> and text'),
        ('<a href="http://example.net">link\nwith new line</a> and text', '<a href="http://example.net">link\\nwith new line</a> and text'),
        ('<a href="http://example.net"><b>link\nwith inner</b> tag new line</a> and text', '<a href="http://example.net"><b>link\\nwith inner</b> tag new line</a> and text'),
        (' leading space<a href="http://example.net"><b>link\nwith  inner multiple space</b> tag new line</a> and trailing space ', 
            '" leading space"<a href="http://example.net"><b>"link\\nwith  inner multiple space"</b> tag new line</a>" and trailing space "'),
    ]

    parse_test_data = escape_data + [
        # Check that double quotes got removed
        ('double quoted text', '"double quoted text"'),
        # Check that newline is read as space (at least it seems to be what Android does)
        ('newline in string', 'newline\nin string'),
    ]
    
    string_xml_wrapper = '<string name="Test String">%s</string>\n\n'
    
    plural_xml_wrapper = '<plurals name="Test String">%s\n</plurals>\n\n'
    plural_item_xml_wrapper = '\n\t<item quantity="%s">%s</item>'
    
    en_quantities = ['one', 'other']
    
    def build_test_parser(self):
        if etree.LXML_VERSION >= (2, 1, 0):
            #Since version 2.1.0 we can pass the strip_cdata parameter to
            #indicate that we don't want cdata to be converted to raw XML
            return etree.XMLParser(strip_cdata=False)
        else:
            return etree.XMLParser()
            
    def build_test_store(self):
        testStore = self.StoreClass()
        testStore.parse(testStore.XMLskeleton)
        testStore.settargetlanguage('en')
        
        return testStore
    
    
    def test_string_recognition(self):
        xml = self.string_xml_wrapper % 'some text'
        
        parser = self.build_test_parser()
        et = etree.fromstring(xml, parser)
        unit = self.UnitClass.createfromxmlElement(et)
        
        assert unit.xmlelement.tag == 'string'
        
    def test_plural_recognition(self):
        innerXml = ''
        for quantity in self.en_quantities:
            innerXml += self.plural_item_xml_wrapper % (quantity, 'some text')
    
        xml = self.plural_xml_wrapper % innerXml
        
        parser = self.build_test_parser()
        et = etree.fromstring(xml, parser)
        unit = self.UnitClass.createfromxmlElement(et)
        
        assert unit.xmlelement.tag == 'plurals'
    
    def test_escape(self):
        for string, xmlText in self.escape_data:
            xml = self.string_xml_wrapper % xmlText
            
            unit = self.UnitClass("Test String")
            unit.setid("Test String")
            unit.target = string
            print
            print "unit.target:", repr(unit.target)
            print "unit:", repr(str(unit))
            print "xml:", repr(xml)
            assert str(unit) == xml

    def test_parse(self):
        parser = self.build_test_parser()
        for string, xmlText in self.parse_test_data:
            xml = self.string_xml_wrapper % xmlText
            
            et = etree.fromstring(xml, parser)
            unit = self.UnitClass.createfromxmlElement(et)
            print
            print "unit.target:", repr(unit.target)
            print "string:", string
            assert unit.target == string
				
				
    def test_plural_escape(self):
        store = self.build_test_store()
        for string, xmlText in self.escape_data:
            innerXml = ''
            pluralStrings = []
            for quantity in self.en_quantities:
                innerXml += self.plural_item_xml_wrapper % (quantity, xmlText)
                pluralStrings.append(string)
        
            xml = self.plural_xml_wrapper % innerXml
            
            unit = self.UnitClass(multistring(["Test String"]))
            unit.setid("Test String")
            store.addunit(unit)
            unit.target = multistring(pluralStrings)
            print
            print "multistring(pluralStrings):", repr(multistring(pluralStrings))
            print "unit.target:", repr(unit.target)
            print "unit:", repr(str(unit))
            print "xml:", repr(xml)
            assert str(unit) == xml

    def test_plural_parse(self):
        parser = self.build_test_parser()
        store = self.build_test_store()
        for string, xmlText in self.parse_test_data:
            innerXml = ''
            for quantity in self.en_quantities:
                innerXml += self.plural_item_xml_wrapper % (quantity, xmlText)
        
            xml = self.plural_xml_wrapper % innerXml
            et = etree.fromstring(xml, parser)
            unit = self.UnitClass.createfromxmlElement(et)
            store.addunit(unit)
            print
            print "unit.target:", repr(unit.target)
            print "string:", string
            assert unit.target == string
            
    def test_plural_values(self):
        store = self.build_test_store()
        
        innerXml = ''
        i = 0
        pluralStrings = []
        for quantity in self.en_quantities:
            innerXml += self.plural_item_xml_wrapper % (quantity, str(i))
            pluralStrings.append(str(i))
    
        xml = self.plural_xml_wrapper % innerXml
        
        unit = self.UnitClass(multistring(["Test String"]))
        unit.setid("Test String")
        store.addunit(unit)
        unit.target = multistring(pluralStrings)
        print
        print "multistring(pluralStrings):", repr(multistring(pluralStrings))
        print "unit.target:", repr(unit.target)
        print "unit:", repr(str(unit))
        print "xml:", repr(xml)
        assert str(unit) == xml

    def test_plural_parse_values(self):
        parser = self.build_test_parser()
        store = self.build_test_store()
        
        innerXml = ''
        i = 0
        pluralStrings = []
        for quantity in self.en_quantities:
            innerXml += self.plural_item_xml_wrapper % (quantity, str(i))
            pluralStrings.append(str(i))
    
        xml = self.plural_xml_wrapper % innerXml
        et = etree.fromstring(xml, parser)
        unit = self.UnitClass.createfromxmlElement(et)
        store.addunit(unit)
        print
        print "unit.target:", repr(unit.target)
        print "pluralStrings:", repr(multistring(pluralStrings))
        assert unit.target == multistring(pluralStrings)


class TestProp(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.AndroidResourceFile
