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

# NOTE:
# This is a class created from the original msgfmt.py written by 
# Martin v. Löwis <loewis@informatik.hu-berlin.de> which is release
# as part of 4Suite (Python tools and libraries for XML processing and databases.)
# which is itself released under the Apache License.  If there is any conflict
# between the Apache license and the GPL then the Apache license is the one that
# applies to the changes made to this file.
#
# 2006-06-07: Updated using:
#  http://svn.python.org/projects/python/trunk/Tools/i18n/msgfmt.py
#  versions 1.1

"""Compile PO files into MO (Machine Object) files."""

import struct
import array
from translate.storage import po

class POCompile:

  MESSAGES = {}

  def generate(self, MESSAGES):
      "Return the generated output."
      keys = MESSAGES.keys()
      # the keys are sorted in the .mo file
      keys.sort()
      offsets = []
      ids = strs = ''
      for id in keys:
          # For each string, we need size and file offset.  Each string is NUL
          # terminated; the NUL does not count into the size.
          # TODO: We don't handle plural forms
          # TODO: We don't do any encoding detection from the PO Header
          id = id.encode('utf-8')
          str = MESSAGES[id].encode('utf-8')
          offsets.append((len(ids), len(id), len(strs), len(str)))
          ids = ids + id + '\0'
          strs = strs + str + '\0'
      output = ''
      # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
      # the keys start right after the index tables.
      # translated string.
      keystart = 7*4+16*len(keys)
      # and the values start after the keys
      valuestart = keystart + len(ids)
      koffsets = []
      voffsets = []
      # The string table first has the list of keys, then the list of values.
      # Each entry has first the size of the string, then the file offset.
      for o1, l1, o2, l2 in offsets:
          koffsets = koffsets + [l1, o1+keystart]
          voffsets = voffsets + [l2, o2+valuestart]
      offsets = koffsets + voffsets
      output = struct.pack("Iiiiiii",
                           0x950412deL,        # Magic
                           0,                 # Version
                           len(keys),         # # of entries
                           7*4,               # start of key index
                           7*4+len(keys)*8,   # start of value index
                           0, 0)              # size and offset of hash table
      output = output + array.array("i", offsets).tostring()
      output = output + ids
      output = output + strs
      return output

  def convertfile(self, thepofile, includefuzzy=False):
    MESSAGES = {}
    #themofile = self.make(thepofile)
    for thepo in thepofile.units:
      if not thepo.isblank():
        if not thepo.isfuzzy() or includefuzzy:
          msgid = po.unquotefrompo(thepo.msgid, joinwithlinebreak=False).replace("\\n", "\n")
          msgstr = po.unquotefrompo(thepo.msgstr, joinwithlinebreak=False).replace("\\n", "\n")
          MESSAGES[msgid] = msgstr
    return self.generate(MESSAGES)

def convertmo(inputfile, outputfile, templatefile, includefuzzy=False):
  """reads in inputfile using po, converts using pocompile, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputpo = po.pofile(inputfile)
  if inputpo.isempty():
    return 0
  convertor = POCompile()
  outputmo = convertor.convertfile(inputpo, includefuzzy)
  outputfile.write(outputmo)
  return 1

def main():
  from translate.convert import convert
  formats = {"po":("mo", convertmo)}
  parser = convert.ConvertOptionParser(formats, usepots=False, description=__doc__)
  parser.add_fuzzy_option()
  parser.run()

if __name__ == '__main__':
    main()
