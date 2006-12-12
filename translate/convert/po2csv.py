#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2003-2006 Zuza Software Foundation
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

"""convert gettext .po localization files to comma-separated values (.csv) files"""

from translate.storage import po
from translate.storage import csvl10n

class po2csv:
  def convertstring(self, postr):
    return po.unquotefrompo(postr, joinwithlinebreak=False)

  def convertcomments(self,thepo):
    commentparts = []
    for comment in thepo.sourcecomments:
      commentparts.append(comment.replace("#:","",1).strip())
    return " ".join(commentparts)

  def convertunit(self,thepo):
    thecsv = csvl10n.csvunit()
    if thepo.isheader():
      thecsv.comment = "comment"
      thecsv.source = "original"
      thecsv.target = "translation"
    elif thepo.isblank():
      return None
    else:
      thecsv.comment = self.convertcomments(thepo)
      thecsv.source = self.convertstring(thepo.msgid)
      # avoid plurals
      target = thepo.msgstr
      if isinstance(target, dict):
        target = thepo.msgstr[0]
      thecsv.target = self.convertstring(target)
    return thecsv

  def convertplurals(self,thepo):
    thecsv = csvl10n.csvunit()
    thecsv.comment = self.convertcomments(thepo)
    thecsv.source = self.convertstring(thepo.msgid_plural)
    thecsv.target = self.convertstring(thepo.msgstr[1])
    return thecsv

  def convertfile(self,thepofile,columnorder=None):
    thecsvfile = csvl10n.csvfile(fieldnames=columnorder)
    for thepo in thepofile.units:
      thecsv = self.convertunit(thepo)
      if thecsv is not None:
        thecsvfile.units.append(thecsv)
      if thepo.hasplural():
        thecsv = self.convertplurals(thepo)
        if thecsv is not None:
          thecsvfile.units.append(thecsv)
    return thecsvfile

def convertcsv(inputfile, outputfile, templatefile, columnorder=None):
  """reads in inputfile using po, converts using po2csv, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputpo = po.pofile(inputfile)
  if inputpo.isempty():
    return 0
  convertor = po2csv()
  outputcsv = convertor.convertfile(inputpo,columnorder)
  outputcsvsrc = str(outputcsv)
  outputfile.write(outputcsvsrc)
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {"po":("csv", convertcsv)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  parser.add_option("", "--columnorder", dest="columnorder", default=None,
    help="specify the order and position of columns (comment,source,target)")
  parser.passthrough.append("columnorder")
  parser.run(argv)


if __name__ == '__main__':
    main()
