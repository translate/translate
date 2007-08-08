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

"""extracts localizable strings from HTML files to gettext .po files
You can merge translated strings back using po2html"""

from translate.storage import po
from translate.storage import html

class html2po:
  def convertfile(self, inputfile, filename, includeheader, includeuntagged=False, duplicatestyle="msgid_comment"):
    """converts a html file to .po format"""
    thepofile = po.pofile()
    htmlparser = html.htmlfile(includeuntaggeddata=includeuntagged, inputfile=inputfile)
    if includeheader:
      headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit")
      thepofile.units.append(headerpo)
    for htmlunit in htmlparser.units:
      thepo = thepofile.addsourceunit(htmlunit.source)
      thepo.addlocations(htmlunit.getlocations())
    thepofile.removeduplicates(duplicatestyle)
    return thepofile

def converthtml(inputfile, outputfile, templates, includeuntagged=False, pot=False, duplicatestyle="msgctxt"):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  convertor = html2po()
  outputfilepos = outputfile.tell()
  includeheader = outputfilepos == 0
  outputpo = convertor.convertfile(inputfile, getattr(inputfile, "name", "unknown"), includeheader, includeuntagged, duplicatestyle=duplicatestyle)
  outputposrc = str(outputpo)
  outputfile.write(outputposrc)
  return 1

def main(argv=None):
  from translate.convert import convert
  from translate.misc import stdiotell
  import sys
  sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
  formats = {"html":("po",converthtml), "htm":("po",converthtml), "xhtml":("po",converthtml), None:("po",converthtml)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  parser.add_option("-u", "--untagged", dest="includeuntagged", default=False, action="store_true",
                    help="include untagged sections")
  parser.passthrough.append("includeuntagged")
  parser.add_duplicates_option()
  parser.passthrough.append("pot")
  parser.run(argv)


if __name__ == '__main__':
  main()
