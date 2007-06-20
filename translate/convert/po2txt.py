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
from translate.storage import txt
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

  def convertfile(self, inputpo, includefuzzy):
    """converts a file to txt format"""
    txtresult = ""
    for pounit in inputpo.units:
      if pounit.isheader():
        continue
      if pounit.isblankmsgstr() or (not includefuzzy and pounit.isfuzzy()):
        txtresult += self.wrapmessage(pounit.source) + "\n" + "\n"
      else:
        txtresult += self.wrapmessage(pounit.target) + "\n" + "\n"
    return txtresult.rstrip()
 
  def mergefile(self, inputpo, templatetext, includefuzzy):
    """converts a file to txt format"""
    txtresult = templatetext
    # TODO: make a list of blocks of text and translate them individually
    # rather than using replace
    for pounit in inputpo.units:
      if pounit.isheader():
        continue
      if not pounit.isfuzzy() or includefuzzy:
        txtsource = pounit.source
        txttarget = self.wrapmessage(pounit.target)
        if not pounit.isblankmsgstr():
          txtresult = txtresult.replace(txtsource, txttarget)
    return txtresult

def converttxt(inputfile, outputfile, templatefile, wrap=None, includefuzzy=False, encoding='utf-8'):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  inputpo = po.pofile(inputfile)
  convertor = po2txt(wrap=wrap)
  if templatefile is None:
    outputtxt = convertor.convertfile(inputpo, includefuzzy)
  else:
    templatetext = templatefile.read().decode(encoding)
    outputtxt = convertor.mergefile(inputpo, templatetext, includefuzzy)
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
  parser.add_option("", "--encoding", dest="encoding", default='utf-8', type="string",
      help="The encoding of the template file (default: UTF-8)")
  parser.passthrough.append("encoding")
  if textwrap is not None:
    parser.add_option("-w", "--wrap", dest="wrap", default=None, type="int",
                      help="set number of columns to wrap text at", metavar="WRAP")
    parser.passthrough.append("wrap")
  parser.add_fuzzy_option()
  parser.run(argv)


if __name__ == '__main__':
    main()
