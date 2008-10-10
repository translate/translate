#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test baseplaceables module."""

from translate.storage.placeables import baseplaceables


class TestPlaceable:
    """Test Placeable base class.
    
    Derived classes can reuse these basic tests by pointing PlaceableClass 
    to a derived Placeable.
    
    """
    PlaceableClass = baseplaceables.Placeable

    def setup_method(self, method):
        self.placeable = self.PlaceableClass("&lt;br/&gt;", "x-html-br", " ")

    def test_create(self):
        """Tests a simple creation"""
        placeable = self.placeable
        print 'placeable: ', placeable
        if not placeable.emptycontent:
            print 'placeable.content: ', placeable.content
            assert placeable.content == "&lt;br/&gt;"
        print 'placeable.ctype: ', placeable.ctype
        assert placeable.ctype == "x-html-br"
        print 'placeable.equiv_text: >>%s<<' % placeable.equiv_text
        assert placeable.equiv_text == " "       
        placeable = self.PlaceableClass("")
        print 'default placeable: ', placeable
        assert placeable.content == ""
        assert placeable.ctype == None
        assert placeable.equiv_text == None    
        
    def test_eq(self):
        """Tests equality comparison"""
        placeable1 = self.placeable
        placeable1b =  self.PlaceableClass("&lt;br/&gt;", "x-html-br", " ")
        placeable2 = self.PlaceableClass("&amp;", "x-akey", "")
        placeable2b = self.PlaceableClass("&amp;", "x-akey", "")
        placeable3 = self.PlaceableClass("&amp;", "x-akey", "&")
        placeable4 = self.PlaceableClass("&amp;", "x-ampersand", "&")
        placeable5 = self.PlaceableClass("|", "x-akey", "")
        assert placeable1 == placeable1b
        assert placeable2 == placeable2b
        assert placeable1 != placeable2        
        assert placeable2 != placeable3
        assert placeable2 != placeable4
        assert placeable3 != placeable4
        assert placeable2 != placeable5
        