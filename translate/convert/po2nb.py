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

"""translates nanoblogger html part files using gettext .po localization
You can generate the po files using nb2po"""

from translate.storage import po
try:
  import textwrap
except:
  textwrap = None

class po2nb:
  """po2nb can take a po file and generate html. best to give it a template file otherwise will just concat msgstrs"""
  htmlfields = ["BODY"]

  def __init__(self, wrap=None):
    self.wrap = wrap

  def convertmessage(self, message):
    """converts a po message to a string"""
    unquotedmessage = po.getunquotedstr(message, joinwithlinebreak=False, includeescapes=True)
    return unquotedmessage.replace("\\n", "\n")

  def wrapmessage(self, message):
    """rewraps text as required"""
    if self.wrap is None:
      return message
    return "\n".join([textwrap.fill(line, self.wrap, replace_whitespace=False) for line in message.split("\n")])

  def convertfile(self, inputpo):
    """converts a file from .po format"""
    nbresult = ""
    cachefieldorder = []
    cachefields = {}
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      for source in thepo.getlocations():
        filename, fieldname = source.split("#", 1)
        fieldvalue = self.convertmessage(thepo.msgstr)
        if not fieldvalue.strip():
          fieldvalue = self.convertmessage(thepo.msgid)
        if ":" in fieldname:
          fieldname, blocknum = fieldname.split(":", 1)
          blocknum = int(blocknum)
          if not fieldname in cachefields:
            cachefields[fieldname] = [(blocknum, fieldvalue)]
            cachefieldorder.append(fieldname)
          else:
            cachefields[fieldname].append((blocknum, fieldvalue))
        else:
          nbresult += "%s: %s\n" % (fieldname, fieldvalue)
    for fieldname in cachefieldorder:
      blocks = cachefields[fieldname]
      blocks.sort()
      nbresult += "-----\n%s:\n" % fieldname
      for blocknum, block in blocks:
        nbresult += self.wrapmessage(block) + "\n" + "\n"
      nbresult += "-----\n"
    return nbresult
 
  def mergefile(self, inputpo, templatetext):
    """converts a file to .po format"""
    nbresult = templatetext
    # TODO: use the algorithm from html2po to get blocks and translate them individually
    # rather than using replace
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      msgid = self.convertmessage(thepo.msgid)
      msgstr = self.wrapmessage(self.convertmessage(thepo.msgstr))
      if msgstr.strip():
        nbresult = nbresult.replace(msgid, msgstr, 1)
    return nbresult

def convertnb(inputfile, outputfile, templatefile, wrap=None):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputpo = po.pofile(inputfile)
  convertor = po2nb(wrap=wrap)
  if templatefile is None:
    outputhtml = convertor.convertfile(inputpo)
  else:
    templatetext = templatefile.read()
    outputhtml = convertor.mergefile(inputpo, templatetext)
  outputfilepos = outputfile.tell()
  outputfile.write(outputhtml)
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {("po", "htm"):("htm",convertnb), ("po"):("htm",convertnb)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  if textwrap is not None:
    parser.add_option("-w", "--wrap", dest="wrap", default=None, type="int",
                      help="set number of columns to wrap html at", metavar="WRAP")
    parser.passthrough.append("wrap")
  parser.run(argv)


if __name__ == '__main__':
    main()
