#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002-2006 Zuza Software Foundation
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

"""classes that hold units of .oo files (oounit) or entire files (oofile)
these are specific .oo files for localisation exported by OpenOffice - SDF format
See http://l10n.openoffice.org/L10N_Framework/Intermediate_file_format.html
FIXME: add simple test which reads in a file and writes it out again"""

import os
import sys
from translate.misc import quote
from translate.misc import wStringIO
import warnings

normalfilenamechars = "/#.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
normalizetable = ""
for i in map(chr, range(256)):
  if i in normalfilenamechars:
    normalizetable += i
  else:
    normalizetable += "_"

class unormalizechar(dict):
  def __init__(self, normalchars):
    self.normalchars = {}
    for char in normalchars:
      self.normalchars[ord(char)] = char
  def __getitem__(self, key):
    return self.normalchars.get(key, u"_")

unormalizetable = unormalizechar(normalfilenamechars.decode("ascii"))

def normalizefilename(filename):
  """converts any non-alphanumeric (standard roman) characters to _"""
  if isinstance(filename, str):
    return filename.translate(normalizetable)
  else:
    return filename.translate(unormalizetable)

class ooline:
  """this represents one line, one translation in an .oo file"""
  def __init__(self, parts=None):
    """construct an ooline from its parts"""
    if parts is None:
      self.project, self.sourcefile, self.dummy, self.resourcetype, \
        self.groupid, self.localid, self.helpid, self.platform, self.width, \
        self.languageid, self.text, self.helptext, self.quickhelptext, self.title, self.timestamp = [""] * 15
    else:
      self.setparts(parts)

  def setparts(self, parts):
    """create a line from its tab-delimited parts"""
    if len(parts) != 15:
      warnings.warn("oo line contains %d parts, it should contain 15: %r" % (len(parts), parts))
      newparts = list(parts)
      if len(newparts) < 15:
        newparts = newparts + [""] * (15-len(newparts))
      else:
        newparts = newparts[:15]
      parts = tuple(newparts)
    self.project, self.sourcefile, self.dummy, self.resourcetype, \
      self.groupid, self.localid, self.helpid, self.platform, self.width, \
      self.languageid, self.text, self.helptext, self.quickhelptext, self.title, self.timestamp = parts

  def getparts(self):
    """return a list of parts in this line"""
    return (self.project, self.sourcefile, self.dummy, self.resourcetype,
            self.groupid, self.localid, self.helpid, self.platform, self.width, 
            self.languageid, self.text, self.helptext, self.quickhelptext, self.title, self.timestamp)

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    source = self.getoutput()
    if isinstance(source, unicode):
      return source.encode(getattr(self, "encoding", "UTF-8"))
    return source

  def getoutput(self):
    """return a line in tab-delimited form"""
    parts = [part.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r") for part in self.getparts()]
    return "\t".join(parts)

  def getkey(self):
    """get the key that identifies the resource"""
    return (self.project, self.sourcefile, self.resourcetype, self.groupid, self.localid, self.platform)

class oounit:
  """this represents a number of translations of a resource"""
  def __init__(self):
    """construct the oounit"""
    self.languages = {}
    self.lines = []

  def addline(self, line):
    """add a line to the oounit"""
    self.languages[line.languageid] = line
    self.lines.append(line)

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    source = self.getoutput()
    if isinstance(source, unicode):
      return source.encode(getattr(self, "encoding", "UTF-8"))
    return source

  def getoutput(self):
    """return the lines in tab-delimited form"""
    return "\r\n".join([str(line) for line in self.lines])

class oofile:
  """this represents an entire .oo file"""
  UnitClass = oounit
  def __init__(self, input=None):
    """constructs the oofile"""
    self.oolines = []
    self.units = []
    self.ookeys = {}
    self.filename = "(unknown file)"
    self.languages = []
    if input is not None:
      self.parse(input)

  def addline(self, thisline):
    """adds a parsed line to the file"""
    key = thisline.getkey()
    element = self.ookeys.get(key, None)
    if element is None:
      element = self.UnitClass()
      self.units.append(element)
      self.ookeys[key] = element
    element.addline(thisline)
    self.oolines.append(thisline)
    if thisline.languageid not in self.languages:
      self.languages.append(thisline.languageid)

  def parse(self, input):
    """parses lines and adds them to the file"""
    self.filename = getattr(input, 'name', '')
    if hasattr(input, "read"):
      src = input.read()
      input.close()
    else:
      src = input
    for line in src.split("\n"):
      line = quote.rstripeol(line)
      if not line:
        continue
      parts = line.split("\t")
      thisline = ooline(parts)
      self.addline(thisline)

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    source = self.getoutput()
    if isinstance(source, unicode):
      return source.encode(getattr(self, "encoding", "UTF-8"))
    return source

  def getoutput(self):
    """converts all the lines back to tab-delimited form"""
    lines = []
    for oe in self.units:
      if len(oe.lines) > 2:
        warnings.warn("contains %d lines (should be 2 at most): languages %r" % (len(oe.lines), oe.languages))
        oekeys = [line.getkey() for line in oe.lines]
        warnings.warn("contains %d lines (should be 2 at most): keys %r" % (len(oe.lines), oekeys))
      oeline = str(oe) + "\r\n"
      lines.append(oeline)
    return "".join(lines)

class oomultifile:
  """this takes a huge GSI file and represents it as multiple smaller files..."""
  def __init__(self, filename, mode=None, multifilestyle="single"):
    """initialises oomultifile from a seekable inputfile or writable outputfile"""
    self.filename = filename
    if mode is None:
      if os.path.exists(filename):
        mode = 'r'
      else:
        mode = 'w'
    self.mode = mode
    self.multifilestyle = multifilestyle
    self.multifilename = os.path.splitext(filename)[0]
    self.multifile = open(filename, mode)
    self.subfilelines = {}
    if mode == "r":
      self.createsubfileindex()

  def createsubfileindex(self):
    """reads in all the lines and works out the subfiles"""
    linenum = 0
    for line in self.multifile:
      subfile = self.getsubfilename(line)
      if not subfile in self.subfilelines:
        self.subfilelines[subfile] = []
      self.subfilelines[subfile].append(linenum)
      linenum += 1

  def getsubfilename(self, line):
    """looks up the subfile name for the line"""
    if line.count("\t") < 2:
      raise ValueError("invalid tab-delimited line: %r" % line)
    lineparts = line.split("\t", 2)
    module, filename = lineparts[0], lineparts[1]
    if self.multifilestyle == "onefile":
      ooname = self.multifilename
    elif self.multifilestyle == "toplevel":
      ooname = module
    else:
      filename = filename.replace("\\", "/")
      fileparts = [module] + filename.split("/")
      ooname = os.path.join(*fileparts[:-1])
    return ooname + os.extsep + "oo"

  def listsubfiles(self):
    """returns a list of subfiles in the file"""
    return self.subfilelines.keys()

  def __iter__(self):
   """iterates through the subfile names"""
   for subfile in self.listsubfiles():
     yield subfile

  def __contains__(self, pathname):
    """checks if this pathname is a valid subfile"""
    return pathname in self.subfilelines

  def getsubfilesrc(self, subfile):
    """returns the list of lines matching the subfile"""
    lines = []
    requiredlines = dict.fromkeys(self.subfilelines[subfile])
    linenum = 0
    self.multifile.seek(0)
    for line in self.multifile:
      if linenum in requiredlines:
        lines.append(line)
      linenum += 1
    return "".join(lines)

  def openinputfile(self, subfile):
    """returns a pseudo-file object for the given subfile"""
    subfilesrc = self.getsubfilesrc(subfile)
    inputfile = wStringIO.StringIO(subfilesrc)
    inputfile.filename = subfile
    return inputfile

  def openoutputfile(self, subfile):
    """returns a pseudo-file object for the given subfile"""
    def onclose(contents):
      self.multifile.write(contents)
      self.multifile.flush()
    outputfile = wStringIO.CatchStringOutput(onclose)
    outputfile.filename = subfile
    return outputfile

  def getoofile(self, subfile):
    """returns an oofile built up from the given subfile's lines"""
    subfilesrc = self.getsubfilesrc(subfile)
    oosubfile = oofile()
    oosubfile.filename = subfile
    oosubfile.parse(subfilesrc)
    return oosubfile

if __name__ == '__main__':
  of = oofile()
  of.parse(sys.stdin.read())
  sys.stdout.write(str(of))


