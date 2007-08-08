#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006-2007 Zuza Software Foundation
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

"""module for handling TBX glossary files"""

from translate.storage import lisa

class tbxunit(lisa.LISAunit):
    """A single term in the TBX file. 
Provisional work is done to make several languages possible."""
    rootNode = "termEntry"
    languageNode = "langSet"
    textNode = "term"
                   
    def createlanguageNode(self, lang, text, purpose):
        """returns a langset xml Element setup with given parameters"""
        if isinstance(text, str):
            text = text.decode("utf-8")
        langset = self.document.createElement(self.languageNode)
        assert self.document == langset.ownerDocument
        langset.setAttribute("xml:lang", lang)
        tig = self.document.createElement("tig") # or ntig with termGrp inside
        term = self.document.createElement(self.textNode)
        termtext = self.document.createTextNode(text)
        
        langset.appendChild(tig)
        tig.appendChild(term)
        term.appendChild(termtext)
        return langset


class tbxfile(lisa.LISAfile):
    """Class representing a TBX file store."""
    UnitClass = tbxunit
    rootNode = "martif"
    bodyNode = "body"
    XMLskeleton = '''<?xml version="1.0"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX">
<martifHeader>
 <fileDesc>
  <sourceDesc><p>Translate Toolkit - csv2tbx</p></sourceDesc>
 </fileDesc>
</martifHeader>
<text><body></body></text>
</martif>'''

    def addheader(self):
        """Initialise headers with TBX specific things."""
        self.document.documentElement.setAttribute("xml:lang", self.sourcelanguage)

