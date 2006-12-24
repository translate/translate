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

"""classes that hold units of .properties files (propunit) or entire files (propfile)
these files are used in translating Mozilla and other software"""

from translate.storage import base
from translate.misc import quote
import sys
import sre

# the rstripeols convert dos <-> unix nicely as well
# output will be appropriate for the platform

eol = "\n"

class propunit(base.TranslationUnit):
  """an element of a properties file i.e. a name and value, and any comments associated"""
  def __init__(self, source=""):
    """construct a blank propunit"""
    super(propunit, self).__init__(source)
    self.name = ""
    self.comments = []
    self.source = source

  def setsource(self, source):
    """Sets the source AND the target to be equal"""
    self.msgid = quote.mozillapropertiesencode(source)

  def getsource(self):
    msgid = quote.mozillapropertiesdecode(self.msgid)
    msgid = msgid.lstrip(" ")
    rstriped = msgid.rstrip(" ")
    if rstriped and rstriped[-1] != "\\":
      msgid = rstriped

    msgid = sre.sub("\\\\ ", " ", msgid)
    return msgid

  source = property(getsource, setsource)

  def settarget(self, target):
    """Note: this also sets the .source attribute!"""
    # TODO: shouldn't this just call the .source property? no quoting done here...
    self.msgid = target

  def gettarget(self):
    return self.msgid
  target = property(gettarget, settarget)

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    source = self.getoutput()
    if isinstance(source, unicode):
      return source.encode(getattr(self, "encoding", "UTF-8"))
    return source

  def getoutput(self):
    """convert the element back into formatted lines for a .properties file"""
    if self.isblank():
      return "".join(self.comments + ["\n"])
    else:
      if "\\u" in self.msgid:
        self.msgid = quote.mozillapropertiesencode(quote.mozillapropertiesdecode(self.msgid))
      return "".join(self.comments + ["%s=%s\n" % (self.name, self.msgid)])

  def getlocations(self):
    return [self.name]

  def addnote(self, note, origin=None):
    self.comments.append(note)

  def getnotes(self, origin=None):
    return '\n'.join(self.comments)

  def removenotes(self):
    self.comments = []

  def isblank(self):
    """returns whether this is a blank element, containing only comments..."""
    return not (self.name or self.msgid)

class propfile(base.TranslationStore):
  """this class represents a .properties file, made up of propunits"""
  UnitClass = propunit
  def __init__(self, inputfile=None):
    """construct a propfile, optionally reading in from inputfile"""
    self.units = []
    self.filename = getattr(inputfile, 'name', '')
    if inputfile is not None:
      propsrc = inputfile.read()
      inputfile.close()
      self.parse(propsrc)

  def parse(self, propsrc):
    """read the source of a properties file in and include them as units"""
    newunit = propunit()
    inmultilinemsgid = 0
    lines = propsrc.split("\n")
    for line in lines:
      # handle multiline msgid if we're in one
      line = quote.rstripeol(line)
      if inmultilinemsgid:
        newunit.msgid += line.lstrip()
        # see if there's more
        inmultilinemsgid = (newunit.msgid[-1:] == '\\')
        # if we're still waiting for more...
        if inmultilinemsgid:
          # strip the backslash
          newunit.msgid = newunit.msgid[:-1]
        if not inmultilinemsgid:
          # we're finished, add it to the list...
          self.units.append(newunit)
          newunit = propunit()
      # otherwise, this could be a comment
      elif line.strip()[:1] == '#':
        # add a comment
        line = quote.escapecontrols(line)
        newunit.comments.append(line+"\n")
      elif not line.strip():
        # this is a blank line...
        if str(newunit).strip():
          self.units.append(newunit)
          newunit = propunit()
      else:
        equalspos = line.find('=')
        # if no equals, just ignore it
        if equalspos == -1:
          continue
        # otherwise, this is a definition
        else:
          newunit.name = line[:equalspos].strip()
          newunit.msgid = line[equalspos+1:].lstrip()
          # backslash at end means carry string on to next line
          if newunit.msgid[-1:] == '\\':
            inmultilinemsgid = 1
            newunit.msgid = newunit.msgid[:-1]
          else:
            self.units.append(newunit)
            newunit = propunit()
    # see if there is a leftover one...
    if inmultilinemsgid or len(newunit.comments) > 0:
      self.units.append(newunit)

  def __str__(self):
    """convert the units back to lines"""
    lines = []
    for unit in self.units:
      lines.append(str(unit))
    return "".join(lines)

  def parsestring(cls, storestring):
    """Parses the properties file contents in the storestring"""
    parsedfile = propfile()
    parsedfile.parse(storestring)
    return parsedfile
  parsestring = classmethod(parsestring)

if __name__ == '__main__':
  import sys
  pf = propfile(sys.stdin)
  sys.stdout.write(str(pf))

