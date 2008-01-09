#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Zuza Software Foundation
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

"""Segment PO files at the sentence level"""

from translate.storage import factory
from translate.lang.common import Common as lang
import os
import re

class segment:

    def segmentunit(self, unit):
        if unit.isheader() or unit.hasplural():
            return [unit]
        sourcesegments = lang.sentences(unit.source, strip=False)
        targetsegments = lang.sentences(unit.target, strip=False)
        if unit.istranslated() and (len(sourcesegments) != len(targetsegments)):
            return [unit]
        units = []
        for i in range(len(sourcesegments)):
            newunit = unit.copy()
            newunit.source = sourcesegments[i]
            if not unit.istranslated():
                newunit.target = ""
            else:
                newunit.target = targetsegments[i]
            units.append(newunit)
            for unit in units:
                print unit.source
        return units

    def convertstore(self, fromstore):
        tostore = type(fromstore)()
        for unit in fromstore.units:
            newunits = self.segmentunit(unit)
            for newunit in newunits:
                tostore.addunit(newunit)
        return tostore

def segmentfile(inputfile, outputfile, templatefile, format=None, rewritestyle=None, hash=None):
  """reads in inputfile, segments it then, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputstore = factory.getobject(inputfile)
  if inputstore.isempty():
    return 0
  convertor = segment()
  outputstore = convertor.convertstore(inputstore)
  outputfile.write(str(outputstore))
  return 1

def main():
  from translate.convert import convert
  formats = {"po":("po", segmentfile), "xlf":("xlf", segmentfile)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  parser.run()


if __name__ == '__main__':
  main()
