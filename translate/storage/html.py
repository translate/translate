#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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

"""module for parsing html files for translation"""

from translate.storage import base
from HTMLParser import HTMLParser

class htmlunit(base.TranslationUnit):
  """A unit of translatable/localisable HTML content"""
  def __init__(self, source=None):
    self.locations = []
    self.setsource(source)

  def getsource(self):
    #TODO: Rethink how clever we should try to be with html entities.
    return self.text.replace("&amp;", "&").replace("&lt;", "<").replace("\n", " ")
  
  def setsource(self, source):
    self.text = source.replace("&", "&amp;").replace("<", "&lt;")
  source = property(getsource, setsource)

  def addlocation(self, location):
    self.locations.append(location)

  def getlocations(self):
    return self.locations


class htmlfile(HTMLParser, base.TranslationStore):
  UnitClass = htmlunit
  markingtags = ["p", "title", "h1", "h2", "h3", "h4", "h5", "h6", "th", "td", "div", "li", "dt", "dd", "address", "caption"]
  markingattrs = []
  includeattrs = ["alt", "summary", "standby", "abbr", "content"]

  def __init__(self, includeuntaggeddata=None, inputfile=None):
    self.units= []
    self.filename = getattr(inputfile, 'name', None) 
    if inputfile is not None:
      thmlsrc = inputfile.read()
      inputfile.close()
      self.parse(htmlsrc)
    
    self.currentblock = ""
    self.currentblocknum = 0
    self.currenttag = None
    self.includeuntaggeddata = includeuntaggeddata
    HTMLParser.__init__(self)

  def parsestring(cls, storestring):
    """Parses the html file contents in the storestring"""
    parsedfile = htmlfile()
    parsedfile.parse(storestring)
    return parsedfile
  parsestring = classmethod(parsestring)

  def addcurrentblock(self):
    if self.currentblock:
      self.currentblocknum += 1
      unit = self.addsourceunit(self.currentblock.strip())
      unit.addlocation("%s:%d" % (self.filename, self.currentblocknum))


#From here on below, follows the methods of the HTMLParser

  def startblock(self, tag):
    self.addcurrentblock()
    self.currentblock = ""
    self.currenttag = tag

  def endblock(self):
    self.addcurrentblock()
    self.currentblock = ""
    self.currenttag = None

  def handle_starttag(self, tag, attrs):
    newblock = 0
    if tag in self.markingtags:
      newblock = 1
    for attrname, attrvalue in attrs:
      if attrname in self.markingattrs:
        newblock = 1
      if attrname in self.includeattrs:
        self.currentblocknum += 1
        unit = self.addsourceunit(attrvalue)
        unit.addlocation("%s:%d" % (self.filename, self.currentblocknum))

    if newblock:
      self.startblock(tag)
    elif self.currenttag is not None:
      self.currentblock += self.get_starttag_text()

  def handle_startendtag(self, tag, attrs):
    for attrname, attrvalue in attrs:
      if attrname in self.includeattrs:
        self.currentblocknum += 1
        unit = self.addsourceunit(attrvalue)
        unit.addlocation("%s:%d" % (self.filename, self.currentblocknum))
    if self.currenttag is not None:
      self.currentblock += self.get_starttag_text()

  def handle_endtag(self, tag):
    if tag == self.currenttag:
      self.endblock()
    elif self.currenttag is not None: 
      self.currentblock += '</%s>' % tag

  def handle_data(self, data):
    if self.currenttag is not None:
      self.currentblock += data
    elif self.includeuntaggeddata:
      self.startblock(None)
      self.currentblock += data

  def handle_charref(self, name):
    self.handle_data("&#%s;" % name)

  def handle_entityref(self, name):
    self.handle_data("&%s;" % name)

  def handle_comment(self, data):
    # we don't do anything with comments
    pass

class POHTMLParser(htmlfile):
  pass
  
