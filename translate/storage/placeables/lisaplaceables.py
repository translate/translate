#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""Classes for common placeable tags in various LISA standards (TMX, TBX, XLIFF)."""

from translate.storage.placeables import baseplaceables
from translate.lang import data
try:
    from lxml import etree
except ImportError, e:
    raise ImportError("lxml is not installed. It might be possible to continue without support for XML formats.")


#---- Module private functions and variables ----

# Dict variable containing all the implementing classes for the supported tags. 
# Any new supported tag must be added to the dictionary in the following way:
#        _ClassDictionary[PlaceableTag] = "PlaceableClassName"
#
# All the class name strings are replaced for the actual classes when loading
# the module.  
# TODO: implement support for TMX and TBX tags
_classDictionary = { 'xliff:bpt': 'XLIFFBPTPlaceable', 
                     'xliff:bx': 'XLIFFBXPlaceable', 
                     'xliff:ept': 'XLIFFEPTPlaceable',
                     'xliff:ex': 'XLIFFEXPlaceable',
                     'xliff:g': 'XLIFFGPlaceable', 
                     'xliff:it': 'XLIFFITPlaceable',
                     'xliff:ph': 'XLIFFPHPlaceable', 
                     'xliff:sub': 'XLIFFSubText',
                     'xliff:x': 'XLIFFXPlaceable' }


def _strreduce(accumlist, current):
    """Reduce a list of marked content tuples deleting unnecessary elements."""
    previous = accumlist[-1]
    if previous[1] is None and current[1] is None:
        if isinstance(current[0], basestring) and \
           isinstance(previous[0], basestring):
            accumlist[-1] = (previous[0] + current[0], None)
        else:
            return accumlist
    else:
        accumlist.append(current)
    return accumlist

def _cleancontent(slist):
    """Delete unnecessary elements from a (string, placeable object) list."""
    if slist is None:
        return None
    if len(slist) < 2:
        return slist
    return reduce(_strreduce, slist[1:], [slist[0]])    
        
def _unnamespaced(nmtag):
    """Delete namespace in Clark notation."""
    return nmtag[nmtag.find('}')+1:]

def _namespaced(namespace, name): # copied from translate.storage.lisa
    """Returns name in Clark notation within the given namespace."""
    if namespace:
        return "{%s}%s" % (namespace, name)
    else:
        return name
    
def _gettext(node):  # copied from translate.storage.lisa
    """Join together the text from all the descendant text nodes."""
    if len(node):    # The etree way of testing for children
        return node.xpath("string()") # specific to lxml.etree
    else:
        return data.forceunicode(node.text) or u""

def _getplaintext(markedtuple):
    if markedtuple[1] is None:
        return data.forceunicode(markedtuple[0])
    else:
        return u""


#---- Module public functions and variables ----

def createLISAplaceable(xmlelem, format):
    """Create placeable object from a LISA format XML node (factory)."""
    if xmlelem is None:
        return None   
    assert format
    tagkey = "%s:%s" % (format, _unnamespaced(xmlelem.tag))
    if tagkey in _classDictionary:
        placeableclass = _classDictionary[tagkey] 
    else:
        return None  
    return placeableclass.createfromxmlElement(xmlelem)

def getmarkedcontent(xmlelem, format):
    """Create marked content list from a LISA format XML node.  

    Marked content list is a list of tuples (string, placeable object).  
    
    """
    if xmlelem is None:
        return None
    markedcontent = []
    if xmlelem.text:        
        markedcontent.append((xmlelem.text, None))
    for child in xmlelem:
        if isinstance(child.tag, basestring):
            markedcontent.append((_gettext(child), #Should it be child.text ? 
                                  createLISAplaceable(child, format)))
        if child.tail:
            markedcontent.append((child.tail, None))
    return _cleancontent(markedcontent)


#---- LISA Base classes ----
    
class LISAPlaceable(baseplaceables.Placeable):
    """Base LISA placeable class."""
    # Element info (lowercase). They should be defined in the subclasses
    format = ""
    namespace = ""
    tag = ""
#    childrentags = []
       
    def __init__(self, content, ctype=None, equiv_text=None):
        """Create a placeable object. 
        
        Note that if all the parameters are B{None}, the inner xmlelement is
        not created as there is not actual content to populate the XML node.
        This I{empty} initialization provides a convenient way to create
        a placeable object from an already existing XML node in class factory
        methods like I{createfromxmlElement()}.
        
        """
        if content is None and ctype is None and equiv_text is None:
            self.xmlelement = None
            return
        self.xmlelement = etree.Element(self.tag)
        super(LISAPlaceable, self).__init__(content, ctype, equiv_text)
        
    def getcontent(self):
        return _gettext(self.xmlelement)
    
    def setcontent(self, content):
        if self.emptycontent: # Should this test be here ?
            return
        if self.xmlelement is None:
            self.xmlelement = etree.Element(self.namespaced(self.tag))
        self.xmlelement.text = data.forceunicode(content)
    
    content = property(getcontent, setcontent)
    
    def getmarkedcontent(self):  
        return getmarkedcontent(self.xmlelement, self.format)
    
    def setmarkedcontent(self, markedcontent):  
        if self.emptycontent: # Should this test be here ?
            return
        if self.xmlelement is None:
            self.xmlelement = etree.Element(self.namespaced(self.tag))
        for child in self.xmlelement: 
            self.xmlelement.remove(child)
        if len(markedcontent) == 0:
            self.xmlelement.text = u""
            return
        self.xmlelement.text = _getplaintext(markedcontent[0])
        previous = None
        for markedelem in markedcontent[1:]:
            if markedelem[1] is not None:
                self.xmlelement.append(markedelem[1].xmlelement)
                previous = markedelem[1].xmlelement
            else:
                previous.tail = _getplaintext(markedelem)
                     
    markedcontent = property(getmarkedcontent, setmarkedcontent)
    
    def has_children(self):
        return len(self.xmlelement)
    
    def getattribs(self): 
        if self.xmlelement is None:
            return None
        return self.xmlelement.attrib
    
    def setattribs(self, attribs): 
        if self.xmlelement is None:
            self.xmlelement = etree.Element(self.tag)
        self.xmlelement.attrib = attribs
    
    attribs = property(getattribs, setattribs)
        
    def createfromxmlElement(cls, element):
        """Class method to create objects from a XML Element.  
        
        Subclasses should override it to extract the right data from 
        the XML Element.  
        
        """
        return None            
    
    createfromxmlElement = classmethod(createfromxmlElement)
        
              
#---- XLIFF classes ----
    
class XLIFFPlaceable(LISAPlaceable):
    """Base XLIFF placeable class."""
    format = "xliff"
    namespace = 'urn:oasis:names:tc:xliff:document:1.1'
    
    def getctype(self):  
        return self.xmlelement.attrib.get("ctype")
    
    def setctype(self, ctype):
        if ctype is not None:
            self.xmlelement.attrib['ctype'] = ctype
        elif self.xmlelement.attrib.has_key('ctype'):
            del self.xmlelement.attrib['ctype']
    
    ctype = property(getctype, setctype)    

    def getequiv_text(self):  
        return self.xmlelement.attrib.get("equiv-text")
    
    def setequiv_text(self, equiv_text):
        if equiv_text is not None:
            self.xmlelement.attrib['equiv-text'] = equiv_text
        elif self.xmlelement.attrib.has_key('equiv-text'):
            del self.xmlelement.attrib['equiv-text']
    
    equiv_text = property(getequiv_text, setequiv_text)
    
    def createfromxmlElement(cls, element):
        """Class method to create objects from a XML Element."""
        if element is None:
            return None
        if _unnamespaced(element.tag) != cls.tag:
            return None
        xliffplaceable = cls(None, None, None)
        xliffplaceable.xmlelement = element        
        return xliffplaceable
    
    createfromxmlElement = classmethod(createfromxmlElement)
  
    
class XLIFFBPTPlaceable(XLIFFPlaceable):
    """XLIFF's begin paired native code marking placeable (<bpt>)."""
    tag = "bpt"

    
class XLIFFBXPlaceable(XLIFFPlaceable):
    """XLIFF's begin paired native code replacing placeable (<bx>)."""   
    tag = "bx"
    emptycontent = True


class XLIFFEPTPlaceable(XLIFFPlaceable):
    """XLIFF's end paired native code marking placeable (<ept>)."""
    tag = "ept"
    

class XLIFFEXPlaceable(XLIFFPlaceable):
    """XLIFF's begin paired native code replacing placeable (<ex>)."""   
    tag = "ex"
    emptycontent = True
    
    
class XLIFFGPlaceable(XLIFFPlaceable):
    """XLIFF's generic group native code replacing placeable (<g>)."""
    tag = "g"

    
class XLIFFITPlaceable(XLIFFPlaceable):
    """XLIFF's isolated native code marking placeable (<it>)."""    
    tag = "it"
    

class XLIFFPHPlaceable(XLIFFPlaceable):
    """XLIFF's generic native code marking placeable (<ph>)."""
    tag = "ph"
  
    
class XLIFFSubText(XLIFFPlaceable):
    """XLIFF's sub-flow text content inside a sequence of native code <sub>."""    
    tag = "sub"
    
    def __init__(self, content, ctype=None, datatype=None):
        super(XLIFFSubText, self).__init__(content, ctype, None)
        if content is None and ctype is None and datatype is None:
            return
        self.datatype = datatype

    def getdatatype(self):  
        return self.xmlelement.attrib.get("datatype")
    
    def setdatatype(self, datatype):  
        self.xmlelement.attrib['datatype'] = datatype
    
    def getequiv_text(self):  
        return None
    
    def setequiv_text(self, equiv_text):  
        pass
    
    equiv_text = property(getequiv_text, setequiv_text)

    
class XLIFFXPlaceable(XLIFFPlaceable):
    """XLIFF's generic native code replacing placeable (<x>)."""
    tag = "x"
    emptycontent = True

    
#---- Module initialization ----

def _loadclassdictionary(classDictionary):
    """Replace the classname strings with the actual classes in the dictionary."""
    lisamod = __import__('lisaplaceables', globals(), locals(), 
                         ['translate.storage.placeables'])
    for elem in classDictionary.iteritems():
        classDictionary[elem[0]] = getattr(lisamod, elem[1])
    return None

_loadclassdictionary(_classDictionary)
