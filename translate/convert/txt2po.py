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

"""Converts plain text files to Gettext .po files
You can convert back to .txt using po2txt"""

from translate.storage import txt
from translate.storage import po
from translate.misc import quote

class txt2po:
  def __init__(self, duplicatestyle="msgctxt"):
    self.duplicatestyle = duplicatestyle

  def convertfile(self, thetxtfile):
    """converts a file to .po format"""
    thepofile = po.pofile()
    headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit")
    headerpo.othercomments.append("# extracted from %s\n" % thetxtfile.filename)
    thepofile.units.append(headerpo)
    for txtunit in thetxtfile.units:
       thepofile.addsourceunit(txtunit.source)
    thepofile.removeduplicates(self.duplicatestyle)
    return thepofile

def converttxt(inputfile, outputfile, templates, duplicatestyle="msgctxt"):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputtxt = txt.TxtFile(inputfile)
  convertor = txt2po(duplicatestyle=duplicatestyle)
  outputpo = convertor.convertfile(inputtxt)
  if outputpo.isempty():
    return 0
  outputposrc = str(outputpo)
  outputfile.write(outputposrc)
  return 1

def main(argv=None):
  from translate.misc import stdiotell
  from translate.convert import convert
  import sys
  sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
  formats = {"txt":("po",converttxt), "*":("po",converttxt)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  parser.add_duplicates_option()
  parser.run(argv)

