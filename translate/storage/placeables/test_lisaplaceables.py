#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test lisaplaceables module."""

from translate.storage.placeables import baseplaceables
from translate.storage.placeables import lisaplaceables
from translate.storage.placeables import test_baseplaceables

from lxml import etree


class TestLISAPlaceablesModule:
    
    xlfsource_all = \
    '''<source xml:lang="en-us" ts="String">TextA 
           <ph id="_234">code1
               <sub>TextC
                   <ph id="_1_ski_1623">subcode1</ph>TEXT9
                   <ph id="_1_ski_1722">subcode2</ph>TEXT10.
               </sub>
               <sub>SUB children 2</sub>
           </ph>TEXT11
           <ph id="_1_ski_2020">code3</ph>TEXTg.
           <g id="_1_ski_040">text</g>TEXT1
           <bpt id="_1_ski_139">code
               <sub>TextB</sub>
           </bpt>TEXT2
           <ept id="_1_ski_238">code</ept>TEXT3
           <ph id="_1_ski_337">TEXT4</ph>
           <it id="_1_ski_436" pos="open">code</it>TEXT5
           <x id="_1_ski_535"/>TEXT6
           <bx id="_1_ski_634"/>TEXT7
           <ex id="_1_ski_733"/>TEXT8
    </source>'''
    
    xlfsource_subs = \
        '''<ph id="_123">code1
              <sub>TextB
                <ph id="_1_ski_1623">subcode1</ph>TEXTc
                <ph id="_1_ski_1722">subcode2</ph>TEXTd.
              </sub>
           </ph>'''
    
    def test_getmarkedcontent(self):
        xmlelem = etree.fromstring(self.xlfsource_all)
        markedcontent = lisaplaceables.getmarkedcontent(xmlelem, 'xliff')
        for elem in markedcontent:
            print "(%s, %s)" % (elem[0], str(elem[1]))
        assert markedcontent[0][0].startswith("TextA")
        assert markedcontent[0][1] is None
        
        assert markedcontent[1][0].startswith("code1")
        assert markedcontent[1][1].__class__.__name__ == "XLIFFPHPlaceable"
        assert markedcontent[1][1].content == markedcontent[1][0]
        
        assert markedcontent[2][0].startswith("TEXT11")
        assert markedcontent[2][1] is None
        
        assert markedcontent[3][0].startswith("code3")
        assert markedcontent[3][1].__class__.__name__ == "XLIFFPHPlaceable"
        assert markedcontent[3][1].content == markedcontent[3][0]
       
    def test_createLISAplaceable(self):
        xmlelem = etree.fromstring(self.xlfsource_subs)
        xlfplaceable = lisaplaceables.createLISAplaceable(xmlelem, 'xliff')
        print xlfplaceable
        assert xlfplaceable.__class__.__name__ == "XLIFFPHPlaceable"
        assert xlfplaceable.content == xmlelem.xpath("string()")
        markedcontent = xlfplaceable.markedcontent
        print markedcontent
        assert len(markedcontent) == 3 
        assert markedcontent[0][0].startswith("code1")
        assert markedcontent[0][1] is None
    
        assert markedcontent[1][0].startswith("TextB") 
        assert markedcontent[1][1].__class__.__name__ == "XLIFFSubText"
        assert markedcontent[1][1].content == markedcontent[1][0]
                
        assert markedcontent[2][0].startswith('\n')
        assert markedcontent[2][1] is None
        
                
class TestXLIFFPlaceable(test_baseplaceables.TestPlaceable):
    disabled = True
    
    content = "&lt;br/&gt;"
    ctype = "x-html-br"
    equiv_text = " "
    id = "__id_br_1"
    attribs = {"ctype":ctype, "equiv-text":equiv_text, "id":id}
    xlfsource_mcontent = \
        '<source>Beginning marked content <ph id="_1_ski_1623">subcode1 <sub>sub text</sub></ph> TEXTc \
                <ph id="_1_ski_1722">subcode2</ph> finishing marked content</source>'                     
    xmlelem = etree.fromstring(xlfsource_mcontent)        
    new_markedcontent = lisaplaceables.getmarkedcontent(xmlelem, 'xliff')
    new_ctype = "x-html-NEW"
    new_equiv_text = "NEW"
    new_id = "__id_NEW_1"
     
    def test_xliffcreate(self):
        placeable_class = self.PlaceableClass
        if not placeable_class.emptycontent:
            placeable_obj = placeable_class(self.content, self.ctype, self.equiv_text)
        else:
            placeable_obj = placeable_class(None, self.ctype, self.equiv_text)
        print placeable_obj
        print placeable_obj.xmlelement.text
        print placeable_obj.xmlelement.tag
        print placeable_obj.xmlelement.attrib
        assert isinstance(placeable_obj, placeable_class)
        if not placeable_class.emptycontent:
            assert placeable_obj.content == self.content
        else:
            assert placeable_obj.content == u""
        assert placeable_obj.ctype == self.ctype
        assert placeable_obj.equiv_text == self.equiv_text 
        
    def test_markedcontent(self):
        placeable_class = self.PlaceableClass
        if not placeable_class.emptycontent:
            placeable_obj = placeable_class(self.content, self.ctype, self.equiv_text)
        else:
            placeable_obj = placeable_class(None, self.ctype, self.equiv_text)
        placeable_obj.markedcontent = self.new_markedcontent
        placeable_obj.ctype = self.new_ctype
        placeable_obj.equiv_text = self.new_equiv_text
        if not placeable_class.emptycontent:
            assert placeable_obj.markedcontent == self.new_markedcontent
        assert placeable_obj.ctype == self.new_ctype
        assert placeable_obj.equiv_text == self.new_equiv_text

    def test_attribs(self):
        placeable_class = self.PlaceableClass
        if not placeable_class.emptycontent:
            placeable_obj = placeable_class(self.content, self.ctype, self.equiv_text)
        else:
            placeable_obj = placeable_class(None, self.ctype, self.equiv_text)
        placeable_obj.attribs["id"] = self.id
        assert placeable_obj.attribs["id"] == self.id
        placeable_obj.attribs["id"] = self.new_id
        assert placeable_obj.attribs["id"] == self.new_id

        
class TestXLIFFBPTPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFBPTPlaceable
    
        
class TestXLIFFBXPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFBXPlaceable    
        
    
class TestXLIFFEPTPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFEPTPlaceable
    
        
class TestXLIFFEXPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFEXPlaceable
    
        
class TestXLIFFGPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFGPlaceable

        
class TestXLIFFITPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFITPlaceable

    
class TestXLIFFPHPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFPHPlaceable
    
    
#class TestXLIFFSubText(TestXLIFFPlaceable):
    
    #disabled = False
    #PlaceableClass = lisaplaceables.XLIFFSubText

    
class TestXLIFFXPlaceable(TestXLIFFPlaceable):
    
    disabled = False
    PlaceableClass = lisaplaceables.XLIFFXPlaceable
        
        
#if __name__=="__main__":
    #test1 = TestLISAPlaceablesModule()
    #test1.test_getmarkedcontent()
    #test1.test_createLISAplaceable()
    #test1.test_xliffplaceables()

