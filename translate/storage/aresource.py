#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Michal Čihař
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""module for handling Android resource files"""

from lxml import etree

from translate.storage import lisa
from translate.storage import base

class AndroidResourceUnit(base.TranslationUnit):
    """A single term in the Android resource file."""
    rootNode = "string"
    languageNode = "string"

    def __init__(self, source, empty=False, **kwargs):
        self.xmlelement = etree.Element(self.rootNode)
        self.xmlelement.tail = '\n'
        if source is not None:
            self.xmlelement.set('name', source)
        super(AndroidResourceUnit, self).__init__(source)

    def _parse(self):
        self.target = self.gettarget()
        self.source = self.getid()

    def getid(self):
        return self.xmlelement.get("name")

    def getcontext(self):
        return self.xmlelement.get("name")

    def setid(self, newid):
        return self.xmlelement.set("name", newid)

    def settarget(self, target):
        self.xmlelement.text = target
        super(AndroidResourceUnit, self).settarget(target)

    def gettarget(self, lang=None):
        return self.xmlelement.text
    target = property(gettarget, settarget)

    def getlanguageNode(self, lang=None, index=None):
        return self.xmlelement

    def createfromxmlElement(cls, element):
        term = cls(None, empty=True)
        term.xmlelement = element
        term._parse()
        return term
    createfromxmlElement = classmethod(createfromxmlElement)

    def __str__(self):
        return etree.tostring(self.xmlelement, pretty_print=True,
                              encoding='utf-8')

class AndroidResourceFile(lisa.LISAfile):
    """Class representing a Android resource file store."""
    UnitClass = AndroidResourceUnit
    Name = _("Android Resource")
    Mimetypes = ["application/xml"]
    Extensions = ["xml"]
    rootNode = "resources"
    bodyNode = "resources"
    XMLskeleton = '''<?xml version="1.0" encoding="utf-8"?>
<resources></resources>'''

    def initbody(self):
        """Initialises self.body so it never needs to be retrieved from the
        XML again."""
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.getroot()

    def set_base_resource(self, storefile):
        """Loads base resource (containing English strings and all messages)."""
        # Load resource
        r = AndroidResourceFile.parsefile(storefile)
        # We will need index
        self.require_index()
        # Update all units
        for unit in r.units:
            our_unit = self.findid(unit.getid())
            if our_unit is None:
                newunit = AndroidResourceUnit(unit.target)
                newunit.setid(unit.getid())
                newunit.target = ''
                self.addunit(newunit)
            else:
                our_unit.source = unit.target
        self.makeindex()

    def __str__(self):
        """Converts to a string containing the file's XML"""
        doc = etree.Element(self.rootNode)
        doc.tail = self.document.getroot().tail
        # Use only non blank elements
        for elm in self.document.iter('string'):
            if not elm.text is None and elm.text != '':
                doc.append(elm)
        return etree.tostring(doc, pretty_print=True,
                              xml_declaration=True, encoding='utf-8')

