#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import properties
from translate.storage import test_monolingual
from translate.misc import wStringIO

def test_find_delimeter_pos_simple():
    assert properties.find_delimeter("key=value") == ('=', 3)
    assert properties.find_delimeter("key:value") == (':', 3)
    assert properties.find_delimeter("key value") == (' ', 3)

def test_find_delimeter_pos_whitespace():
    assert properties.find_delimeter("key = value") == ('=', 4)
    assert properties.find_delimeter("key : value") == (':', 4)
    assert properties.find_delimeter("key   value") == (' ', 3)
    assert properties.find_delimeter("key key = value") == (' ', 3)
    assert properties.find_delimeter("key value value") == (' ', 3)
    assert properties.find_delimeter(" key = value") == ('=', 5)

def test_find_delimeter_pos_escapes():
    assert properties.find_delimeter("key\:=value") == ('=', 5)
    assert properties.find_delimeter("key\=: value") == (':', 5)
    assert properties.find_delimeter("key\   value") == (' ', 5)
    assert properties.find_delimeter("key\ key\ key\: = value") == ('=', 16)

def test_is_line_continuation():
    assert properties.is_line_continuation("") == False
    assert properties.is_line_continuation("some text") == False
    assert properties.is_line_continuation("""some text\\""") == True
    assert properties.is_line_continuation("""some text\\\\""") == False  # Escaped \
    assert properties.is_line_continuation("""some text\\\\\\""") == True  # Odd num. \ is line continuation
    assert properties.is_line_continuation("""\\\\\\""") == True

class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = properties.propunit

    def test_difficult_escapes(self):
        """It doesn't seem that properties files can store double backslashes.
        
        We are disabling the double-backslash tests for now.
        If we are mistaken in the above assumption, we need to fix getsource()
        and setsource() and delete this test override.
        
        """
        pass

    def test_rich_get(self):
        pass

    def test_rich_set(self):
        pass

class TestProp(test_monolingual.TestMonolingualStore):
    StoreClass = properties.propfile
    
    def propparse(self, propsource):
        """helper that parses properties source without requiring files"""
        dummyfile = wStringIO.StringIO(propsource)
        propfile = properties.propfile(dummyfile)
        return propfile

    def propregen(self, propsource):
        """helper that converts properties source to propfile object and back"""
        return str(self.propparse(propsource))

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        propsource = 'test_me=I can code!'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"

    def test_simpledefinition_source(self):
        """checks that a simple properties definition can be regenerated as source"""
        propsource = 'test_me=I can code!'
        propregen = self.propregen(propsource)
        assert propsource + '\n' == propregen

    def test_unicode_escaping(self):
        """check that escapes unicode is converted properly"""
        propsource = "unicode=\u0411\u0416\u0419\u0428"
        messagevalue = u'\u0411\u0416\u0419\u0428'.encode("UTF-8")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "unicode"
        assert propunit.source.encode("UTF-8") == "БЖЙШ"
        regensource = str(propfile)
        assert messagevalue in regensource
        assert "\\u" not in regensource

    def test_newlines_startend(self):
        """check that we preserver \n that appear at start and end of properties"""
        propsource = "newlines=\\ntext\\n"
        propregen = self.propregen(propsource)
        assert propsource + '\n' == propregen

    def test_whitespace_removal(self):
        """check that we remove extra whitespace around property"""
        propsource = '''  whitespace  =  Start \n'''
        propfile = self.propparse(propsource)
        propunit = propfile.units[0]
        assert propunit.name == "whitespace"
        assert propunit.source == "Start"
     
    def test_key_value_delimeters_simple(self):
        """test that we can handle colon, equals and space delimeter
        between key and value.  We don't test any space removal or escaping"""
        delimeters = [":", "=", " "]
        for delimeter in delimeters:
            propsource = "key%svalue" % delimeter
            print "source: '%s'\ndelimeter: '%s'" % (propsource, delimeter)
            propfile = self.propparse(propsource)
            assert len(propfile.units) == 1
            propunit = propfile.units[0]
            assert propunit.name == "key"
            assert propunit.source == "value"

