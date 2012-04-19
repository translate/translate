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
        super(AndroidResourceUnit, self).__init__(source)

    def _parse(self):
        self._target = self.gettarget()
        self._source = self.getsource()

    def setsource(self, source):
        self.xmlelement.set("name", source)
        super(AndroidResourceUnit, self).setsource(source)

    def getsource(self):
        return self.xmlelement.get("name")
    source = property(getsource, setsource)

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
