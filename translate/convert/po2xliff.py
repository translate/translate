#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005, 2006 Zuza Software Foundation
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

"""Converts Gettext .po files to .xliff localization files
You can convert back from .xliff to .po using po2xliff"""

from translate.storage import po
from translate.storage import poxliff
from translate.misc import quote
from xml.dom import minidom

class po2xliff:
  def convertunit(self, xlifffile, thepo, filename):
    """creates a transunit node"""
    source = thepo.source
    target = thepo.target
    if thepo.isheader():
      unit = xlifffile.addheaderunit(target, filename)
    else:
      unit = xlifffile.addsourceunit(source, filename, True)
      unit.target = target
      if thepo.isfuzzy():
        unit.markfuzzy()
      elif target:
        #TODO: consider if an empty target can be considered as translated
        unit.marktranslated()
      
      #Handle #: location comments
      for location in thepo.getlocations():
        unit.createcontextgroup("po-reference", self.contextlist(location), purpose="location")
      
      #Handle #. automatic comments
      comment = "\n".join([comment[3:-1] for comment in thepo.automaticcomments])
      if comment:
        unit.createcontextgroup("po-entry", [("x-po-autocomment", comment)], purpose="information")
        unit.addnote(comment, origin="developer")
    
      #TODO: x-format, etc.


    #Handle # other comments
    comment = "\n".join([comment[2:-1] for comment in thepo.othercomments])
    if comment:
      unit.createcontextgroup("po-entry", [("x-po-trancomment", comment)], purpose="information")
      unit.addnote(comment, origin="po-translator")
      
    return unit

  def contextlist(self, location):
    contexts = []
    if ":" in location:
      sourcefile, linenumber = location.split(":", 1)
    else:
      sourcefile, linenumber = location, None
    contexts.append(("sourcefile", sourcefile))
    if linenumber:
      contexts.append(("linenumber", linenumber))
    return contexts
    
  def convertfile(self, thepofile, templatefile=None):
    """converts a .po file to .xliff format"""
    if templatefile is None: 
      xlifffile = poxliff.PoXliffFile()
    else:
      xlifffile = poxliff.PoXliffFile(templatefile)
    filename = thepofile.filename
    for thepo in thepofile.units:
      if thepo.isblank():
        continue
      transunitnode = self.convertunit(xlifffile, thepo, filename)
    return str(xlifffile)

def convertpo(inputfile, outputfile, templatefile):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputpo = po.pofile(inputfile)
  if inputpo.isempty():
    return 0
  convertor = po2xliff()
  outputxliff = convertor.convertfile(inputpo, templatefile)
  outputfile.write(outputxliff)
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {"po": ("xliff", convertpo), ("po", "xliff"): ("xliff", convertpo)}
  parser = convert.ConvertOptionParser(formats, usepots=True, usetemplates=True, description=__doc__)
  parser.run(argv)

