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

  def convertcomments(self, pounit):
    commentparts = []
    for comment in pounit.sourcecomments:
      commentparts.append(comment.replace("#:","",1).strip())
    return " ".join(commentparts)

  def convertunit(self, pounit):
    csvunit = csvl10n.csvunit()
    if pounit.isheader():
      csvunit.comment = "comment"
      csvunit.source = "original"
      csvunit.target = "translation"
    elif pounit.isblank():
      return None
    else:
      csvunit.comment = self.convertcomments(pounit)
      csvunit.source = self.convertstring(pounit.msgid)
      # avoid plurals
      target = pounit.msgstr
      if isinstance(target, dict):
        target = pounit.msgstr[0]
      csvunit.target = self.convertstring(target)
    return csvunit

  def convertplurals(self, pounit):
    csvunit = csvl10n.csvunit()
    csvunit.comment = self.convertcomments(pounit)
    csvunit.source = self.convertstring(pounit.msgid_plural)
    csvunit.target = self.convertstring(pounit.msgstr[1])
    return csvunit

  def convertfile(self, thepofile, columnorder=None):
    thecsvfile = csvl10n.csvfile(fieldnames=columnorder)
    for pounit in thepofile.units:
      csvunit = self.convertunit(pounit)
      if csvunit is not None:
        thecsvfile.units.append(csvunit)
      if pounit.hasplural():
        csvunit = self.convertplurals(pounit)
        if csvunit is not None:
          thecsvfile.units.append(csvunit)
    return thecsvfile

def convertcsv(inputfile, outputfile, templatefile, columnorder=None):
  """reads in inputfile using po, converts using po2csv, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputstore = po.pofile(inputfile)
  if inputstore.isempty():
    return 0
  convertor = po2csv()
  outputstore = convertor.convertfile(inputstore,columnorder)
  outputfile.write(str(outputstore))
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
