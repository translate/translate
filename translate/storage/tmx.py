#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005-2007 Zuza Software Foundation
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

"""module for parsing TMX translation memeory files"""

from translate.storage import lisa
from lxml import etree

from translate import __version__

class tmxunit(lisa.LISAunit):
    """A single unit in the TMX file."""
    rootNode = "tu"
    languageNode = "tuv"
    textNode = "seg"
                   
    def createlanguageNode(self, lang, text, purpose):
        """returns a langset xml Element setup with given parameters"""
        if isinstance(text, str):
            text = text.decode("utf-8")
        langset = etree.Element(self.languageNode)
        lisa.setXMLlang(langset, lang)
        seg = etree.SubElement(langset, self.textNode)
        seg.text = text
        return langset


class tmxfile(lisa.LISAfile):
    """Class representing a TMX file store."""
    UnitClass = tmxunit
    rootNode = "tmx"
    bodyNode = "body"
    XMLskeleton = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
<header></header>
<body></body>
</tmx>'''
    
    def addheader(self):
        headernode = self.document.find("//%s" % self.namespaced("header"))
        headernode.set("creationtool", "Translate Toolkit - po2tmx")
        headernode.set("creationtoolversion", __version__.ver)
        headernode.set("segtype", "sentence")
        headernode.set("o-tmf", "UTF-8")
        headernode.set("adminlang", "en")
        #TODO: consider adminlang. Used for notes, etc. Possibly same as targetlanguage
        headernode.set("srclang", self.sourcelanguage)
        headernode.set("datatype", "PlainText")
        #headernode.set("creationdate", "YYYYMMDDTHHMMSSZ"
        #headernode.set("creationid", "CodeSyntax"

    def addtranslation(self, source, srclang, translation, translang):
        """addtranslation method for testing old unit tests"""
        unit = self.addsourceunit(source)
        unit.target = translation
        tuvs = unit.xmlelement.findall('.//%s' % self.namespaced('tuv'))
        lisa.setXMLlang(tuvs[0], srclang)
        lisa.setXMLlang(tuvs[1], translang)

    def translate(self, sourcetext, sourcelang=None, targetlang=None):
        """method to test old unit tests"""
        return getattr(self.findunit(sourcetext), "target", None)

