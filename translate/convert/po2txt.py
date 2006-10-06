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

"""script to translate a set of plain text message files using gettext .po localization
You can generate the po files using txt2po"""

from translate.storage import po
from translate.misc import quote
try:
  import textwrap
except:
  textwrap = None

class po2txt:
  """po2txt can take a po file and generate txt. best to give it a template file otherwise will just concat msgstrs"""
  def __init__(self, wrap=None):
    self.wrap = wrap

  def wrapmessage(self, message):
    """rewraps text as required"""
    if self.wrap is None:
      return message
    return "\n".join([textwrap.fill(line, self.wrap, replace_whitespace=False) for line in message.split("\n")])

  def convertfile(self, inputpo):
    """converts a file to .po format"""
    txtresult = ""
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      if thepo.isfuzzy() or thepo.isblank():
        txtresult += self.wrapmessage(thepo.source) + "\n" + "\n"
      else:
        txtresult += self.wrapmessage(thepo.target) + "\n" + "\n"
    return txtresult
 
  def mergefile(self, inputpo, templatetext):
    """converts a file to .po format"""
    txtresult = templatetext
    # TODO: make a list of blocks of text and translate them individually
    # rather than using replace
    for thepo in inputpo.units:
      if thepo.isheader():
        continue
      msgid = thepo.source
      msgstr = self.wrapmessage(thepo.target)
      txtresult = txtresult.replace(msgid, msgstr)
    return txtresult

def converttxt(inputfile, outputfile, templatefile, wrap=None):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputpo = po.pofile(inputfile)
  convertor = po2txt(wrap=wrap)
  if templatefile is None:
    outputtxt = convertor.convertfile(inputpo)
  else:
    templatetext = templatefile.read()
    outputtxt = convertor.mergefile(inputpo, templatetext)
  outputfilepos = outputfile.tell()
  outputfile.write(outputtxt.encode('utf-8'))
  return 1

def main(argv=None):
  from translate.convert import convert
  from translate.misc import stdiotell
  import sys
  sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
  formats = {("po", "txt"):("txt",converttxt), ("po"):("txt",converttxt)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  if textwrap is not None:
    parser.add_option("-w", "--wrap", dest="wrap", default=None, type="int",
                      help="set number of columns to wrap text at", metavar="WRAP")
    parser.passthrough.append("wrap")
  parser.run(argv)

