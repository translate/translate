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

"""Converts a OpenOffice Writer files to Gettext .po files"""

from translate.storage import po
from translate.misc import quote
from translate.misc import xmlwrapper
import zipfile

class OpenOfficeDocument(xmlwrapper.XMLWrapper):
  def __init__(self, xmlstring, startnum=0):
    root = xmlwrapper.BuildTree(xmlstring)
    xmlwrapper.XMLWrapper.__init__(self, root)
    if self.tag != "document-content": raise ValueError("root %r != 'document-content'" % self.tag)
    self.body = self.getchild("body")

  def excludeiterator(self, obj, excludetags):
    nodes = []
    for node in obj._children:
      if xmlwrapper.splitnamespace(node.tag)[1] not in excludetags:
        nodes.append(node)
        nodes.extend(self.excludeiterator(node, excludetags))
    return nodes

  def getmessages(self):
    nodes = self.excludeiterator(self.body.obj, ["tracked-changes"])
    paragraphs = []
    for node in nodes:
      childns, childtag = xmlwrapper.splitnamespace(node.tag)
      if childtag == "p":
        paragraphs.append(xmlwrapper.XMLWrapper(node))
    messages = []
    for child in paragraphs:
      text = child.getplaintext().strip()
      messages.append(text)
    return messages

class sxw2po:
  def convertfile(self, inputfile, filename):
    """converts a file to .po format"""
    thepofile = po.pofile()
    headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit")
    thepofile.units.append(headerpo)
    try:
      z = zipfile.ZipFile(filename, 'r')
      contents = z.read("content.xml")
    except (ValueError, zipfile.BadZipfile):
      contents = open(filename, 'r').read()
    sxwdoc = OpenOfficeDocument(contents)
    blocknum = 0
    for message in sxwdoc.getmessages():
      if not message: continue
      blocknum += 1
      thepo = po.pounit(encoding="UTF-8")
      thepo.sourcecomments.append("#: %s:%d\n" % (filename,blocknum))
      thepo.msgid = [quote.quotestr(quote.rstripeol(message), escapeescapes=1)]
      if len(thepo.msgid) > 1:
        thepo.msgid = [quote.quotestr("")] + thepo.msgid
      thepo.msgstr = []
      thepofile.units.append(thepo)
    return thepofile

def convertsxw(inputfile, outputfile, templates):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  convertor = sxw2po()
  outputpo = convertor.convertfile(inputfile, getattr(inputfile, "name", "unknown"))
  outputposrc = str(outputpo)
  outputfile.write(outputposrc)
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {"sxw":("po",convertsxw)}
  parser = convert.ConvertOptionParser(formats, description=__doc__)
  parser.run(argv)


if __name__ == '__main__':
    main()
