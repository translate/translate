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
#

"""module for parsing Gettext .mo files for translation

@note: This is a class created from the original msgfmt.py written by 
Martin v. Löwis <loewis@informatik.hu-berlin.de> which is release
as part of 4Suite (Python tools and libraries for XML processing and databases.)
which is itself released under the Apache License.  If there is any conflict
between the Apache license and the GPL then the Apache license is the one that
applies to the changes made to this file.

U{Version 1.1 of msgfmt.py<http://svn.python.org/projects/python/trunk/Tools/i18n/msgfmt.py>}

The coding of .mo files was produced from documentation in Gettext 0.16 and from observation
and testing of existing .mo files in the wild.

The class does not implement any of the hashing componets of Gettext.  This will probably
make the output file slower in some instances.
"""

from translate.storage import base
from translate.storage import po
from translate.misc.multistring import multistring
import struct
import array
import re

MO_MAGIC_NUMBER = 0x950412deL

def mounpack(mofile='messages.mo'):
  """Helper to unpack Gettext MO files into a Python string"""
  f = open(mofile)
  s = f.read()
  print "\\x%02x"*len(s) % tuple(map(ord, s))
  f.close()

class mounit(base.TranslationUnit):
    """A class representing a .mo translation message."""
    def __init__(self, source=None):
        self.msgctxt = []
        self.msgidcomments = []
        super(mounit, self).__init__(source)

    def getcontext(self):
        """Get the message context"""
        # Still need to handle KDE comments
        if self.msgctxt is None:
            return None
        return "".join(self.msgctxt)

    def isheader(self):
        """Is this a header entry?"""
        return self.source == ""

class mofile(base.TranslationStore):
    """A class representing a .mo file."""
    UnitClass = mounit
    def __init__(self, inputfile=None, unitclass=mounit):
        self.UnitClass = unitclass
        base.TranslationStore.__init__(self, unitclass=unitclass)
        self.units = []
        self.filename = ''
        if inputfile is not None:
          self.parsestring(inputfile)

    def __str__(self):
        """Output a string representation of the MO data file"""
        MESSAGES = {}
        for unit in self.units:
            if isinstance(unit.source, multistring):
                source = "".join(unit.msgidcomments) + "\0".join(unit.source.strings)
            else:
                source = "".join(unit.msgidcomments) + unit.source
            if unit.msgctxt:
                source = "".join(unit.msgctxt) + "\x04" + source
            if isinstance(unit.target, multistring):
                target = "\0".join(unit.target.strings)
            else:
                target = unit.target
            if unit.target:
                MESSAGES[source.encode("utf-8")] = target
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
                             MO_MAGIC_NUMBER,   # Magic
                             0,                 # Version
                             len(keys),         # # of entries
                             7*4,               # start of key index
                             7*4+len(keys)*8,   # start of value index
                             0, 0)              # size and offset of hash table
        output = output + array.array("i", offsets).tostring()
        output = output + ids
        output = output + strs
        return output

    def parsestring(cls, storestring):
        """Parses the po file contents in the storestring and returns a new pofile object (classmethod, constructor)"""
        parsedfile = mofile()
        parsedfile.parse(storestring)
        return parsedfile
    parsestring = classmethod(parsestring)

    def parse(self, input):
        """parses the given file or file source string"""
        if hasattr(input, 'name'):
            self.filename = input.name
        elif not getattr(self, 'filename', ''):
            self.filename = ''
        if hasattr(input, "read"):
            mosrc = input.read()
            input.close()
            input = mosrc
        little, = struct.unpack("<L", input[:4])
        big, = struct.unpack(">L", input[:4])
        if little == MO_MAGIC_NUMBER:
            endian = "<"
        elif big == MO_MAGIC_NUMBER:
            endian = ">"
        else:
            raise ValueError("This is not an MO file")
        magic, version, lenkeys, startkey, startvalue, sizehash, offsethash = struct.unpack("%sLiiiiii" % endian, input[:(7*4)])
        if version > 1:
            raise ValueError("Unable to process MO files with versions > 1.  This is a %d version MO file" % version)
        encoding = 'UTF-8'
        for i in range(lenkeys):
            nextkey = startkey+(i*2*4)
            nextvalue = startvalue+(i*2*4)
            klength, koffset = struct.unpack("%sii" % endian, input[nextkey:nextkey+(2*4)])
            vlength, voffset = struct.unpack("%sii" % endian, input[nextvalue:nextvalue+(2*4)])
            source = input[koffset:koffset+klength]
            context = None
            if "\x04" in source:
                context, source = source.split("\x04")
            # Still need to handle KDE comments
            source = multistring(source.split("\0"), encoding=encoding)
            if source == "":
                charset = re.search("charset=([^\\s]+)", input[voffset:voffset+vlength])
                if charset:
                    encoding = po.encodingToUse(charset.group(1))
            target = multistring(input[voffset:voffset+vlength].split("\0"), encoding=encoding)
            newunit = mounit(source)
            newunit.settarget(target)
            if context is not None:
                newunit.msgctxt.append(context)
            self.addunit(newunit)
