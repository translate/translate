#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005, 2006 Zuza Software Foundation
# 
# This file is part of the translate-toolkit
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

"""Compile base class files into Gettext MO (Machine Object) files."""

import struct
import array
from translate.storage import factory
from translate.storage import po
from translate.storage import mo

def mounpack(mofile='messages.mo'):
  """Helper to unpack Gettext MO files into a Python string"""
  f = open(mofile)
  s = f.read()
  print "\\x%02x"*len(s) % tuple(map(ord, s))
  f.close()

class POCompile:

  def convertfile(self, inputfile, includefuzzy=False):
    MESSAGES = {}
    outputfile = mo.mofile()
    for unit in inputfile.units:
      if unit.istranslated() or (unit.isfuzzy() and includefuzzy and unit.target):
          mounit = mo.mounit()
          if unit.isheader():
            mounit.source = ""
          else:
            mounit.source = unit.source
            if hasattr(unit, "msgidcomments"):
              mounit.source.strings[0] = po.unquotefrompo(unit.msgidcomments) + mounit.source.strings[0]
            if hasattr(unit, "msgctxt"):
              mounit.msgctxt = po.unquotefrompo(unit.msgctxt)
          mounit.target = unit.target
          outputfile.addunit(mounit)
    return str(outputfile)

def convertmo(inputfile, outputfile, templatefile, includefuzzy=False):
  """reads in a base class derived inputfile, converts using pocompile, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  input = factory.getobject(inputfile)
  if input.isempty():
    return 0
  convertor = POCompile()
  outputmo = convertor.convertfile(input, includefuzzy)
  outputfile.write(outputmo)
  return 1

def main():
  from translate.convert import convert
  formats = {"po":("mo", convertmo), "xlf":("mo", convertmo)}
  parser = convert.ConvertOptionParser(formats, usepots=False, description=__doc__)
  parser.add_fuzzy_option()
  parser.run()

if __name__ == '__main__':
    main()
