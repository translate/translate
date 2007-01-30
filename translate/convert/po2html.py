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

"""translates html files using gettext .po localization
You can generate the po files using html2po"""

from translate.storage import po
try:
  import textwrap
except:
  textwrap = None

try:
  import tidy
except:
  tidy = None

class po2html:
  """po2html can take a po file and generate html. best to give it a template file otherwise will just concat msgstrs"""
  def __init__(self, wrap=None):
    self.wrap = wrap

  def wrapmessage(self, message):
    """rewraps text as required"""
    if self.wrap is None:
      return message
    return "\n".join([textwrap.fill(line, self.wrap, replace_whitespace=False) for line in message.split("\n")])

  def convertfile(self, inputpo, includefuzzy):
    """converts a file to .po format"""
    htmlresult = ""
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      if includefuzzy or not thepo.isfuzzy():
        htmlresult += self.wrapmessage(thepo.target) + "\n" + "\n"
      else:
        htmlresult += self.wrapmessage(thepo.source) + "\n" + "\n"
    return htmlresult.encode('utf-8')
 
  def mergefile(self, inputpo, templatetext):
    """converts a file to .po format"""
    htmlresult = templatetext.replace("\n", " ")
    if isinstance(htmlresult, str):
      #TODO: get the correct encoding
      htmlresult = htmlresult.decode('utf-8')
    # TODO: use the algorithm from html2po to get blocks and translate them individually
    # rather than using replace
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      msgid = thepo.source
      msgstr = self.wrapmessage(thepo.target)
      if msgstr.strip():
        htmlresult = htmlresult.replace(msgid, msgstr, 1)
    htmlresult = htmlresult.encode('utf-8')
    if tidy:
      htmlresult = str(tidy.parseString(htmlresult))
    return htmlresult

def converthtml(inputfile, outputfile, templatefile, wrap=None, includefuzzy=False):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputpo = po.pofile(inputfile)
  convertor = po2html(wrap=wrap)
  if templatefile is None:
    outputhtml = convertor.convertfile(inputpo, includefuzzy)
  else:
    templatetext = templatefile.read()
    outputhtml = convertor.mergefile(inputpo, templatetext)
  outputfilepos = outputfile.tell()
  outputfile.write(outputhtml)
  return 1

def main(argv=None):
  from translate.convert import convert
  from translate.misc import stdiotell
  import sys
  sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
  formats = {("po", "htm"):("htm",converthtml), ("po", "html"):("html",converthtml), ("po", "xhtml"):("xhtml",converthtml), ("po"):("html",converthtml)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  if textwrap is not None:
    parser.add_option("-w", "--wrap", dest="wrap", default=None, type="int",
                      help="set number of columns to wrap html at", metavar="WRAP")
    parser.passthrough.append("wrap")
  parser.add_fuzzy_option()
  parser.run(argv)


if __name__ == '__main__':
    main()
