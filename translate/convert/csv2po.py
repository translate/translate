#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2003-2006 Zuza Software Foundation
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

"""converts comma-separated values (.csv) files to gettext .po localization files"""

import sys
from translate.misc import quote
from translate.misc import sparse
from translate.storage import po
from translate.storage import csvl10n

def replacestrings(source, *pairs):
  for orig, new in pairs:
    source = source.replace(orig, new)
  return source

def quotecsvstr(source):
  return '"' + replacestrings(source, ('\\"','"'), ('"','\\"'), ("\\\\'", "\\'"), ('\\\\n', '\\n')) + '"'

def simplify(string):
  return filter(type(string).isalnum, string)
  tokens = sparse.SimpleParser().tokenize(string)
  return " ".join(tokens)

class csv2po:
  """a class that takes translations from a .csv file and puts them in a .po file"""
  def __init__(self, templatepo=None, charset=None, duplicatestyle="keep"):
    """construct the converter..."""
    self.pofile = templatepo
    self.charset = charset
    self.duplicatestyle = duplicatestyle
    if self.pofile is not None:
      self.unmatched = 0
      self.makeindex()

  def makeindex(self):
    """makes indexes required for searching..."""
    self.commentindex = {}
    self.sourceindex = {}
    self.simpleindex = {}
    self.duplicatecomments = []
    for thepo in self.pofile.units:
      commentparts = []
      for comment in thepo.sourcecomments:
        commentparts.append(comment.replace("#:","",1).strip())
      joinedcomment = " ".join(commentparts)
      unquotedid = po.unquotefrompo(thepo.msgid)
      # the definitive way to match is by source comment (joinedcomment)
      if joinedcomment in self.commentindex:
        # unless more than one thing matches...
        self.duplicatecomments.append(joinedcomment)
      else:
        self.commentindex[joinedcomment] = thepo
      # do simpler matching in case things have been mangled...
      simpleid = simplify(unquotedid)
      # but check for duplicates
      if simpleid in self.simpleindex and not (unquotedid in self.sourceindex):
        # keep a list of them...
        self.simpleindex[simpleid].append(thepo)
      else:
        self.simpleindex[simpleid] = [thepo]
      # also match by standard msgid
      self.sourceindex[unquotedid] = thepo
    for comment in self.duplicatecomments:
      if comment in self.commentindex:
        del self.commentindex[comment]

  def convertelement(self,thecsv):
    """converts csv element to po element"""
    thepo = po.pounit(encoding="UTF-8")
    thepo.sourcecomments = ["#: " + thecsv.comment + "\n"]
    thepo.msgid = [quotecsvstr(line) for line in thecsv.source.split('\n')]
    thepo.msgstr = [quotecsvstr(line) for line in thecsv.target.split('\n')]
    return thepo

  def handlecsvunit(self, thecsv):
    """handles reintegrating a csv element into the .po file"""
    if len(thecsv.comment.strip()) > 0 and thecsv.comment in self.commentindex:
      thepo = self.commentindex[thecsv.comment]
    elif thecsv.source in self.sourceindex:
      thepo = self.sourceindex[thecsv.source]
    elif simplify(thecsv.source) in self.simpleindex:
      thepolist = self.simpleindex[simplify(thecsv.source)]
      if len(thepolist) > 1:
        csvfilename = getattr(self.csvfile, "filename", "(unknown)")
        matches = "\n  ".join(["possible match: " + po.unquotefrompo(thepo.msgid) for thepo in thepolist])
        print >>sys.stderr, "%s - csv entry not found in pofile, multiple matches found:\n  location\t%s\n  original\t%s\n  translation\t%s\n  %s" % (csvfilename, thecsv.comment, thecsv.source, thecsv.target, matches)
        self.unmatched += 1
        return
      thepo = thepolist[0]
    else:
      csvfilename = getattr(self.csvfile, "filename", "(unknown)")
      print >>sys.stderr, "%s - csv entry not found in pofile:\n  location\t%s\n  original\t%s\n  translation\t%s" % (csvfilename, thecsv.comment, thecsv.source, thecsv.target)
      self.unmatched += 1
      return
    csvtarget = [quotecsvstr(line) for line in thecsv.target.split('\n')]
    if thepo.hasplural():
      # we need to work out whether we matched the singular or the plural
      singularid = po.unquotefrompo(thepo.msgid)
      pluralid = po.unquotefrompo(thepo.msgid_plural)
      if thecsv.source == singularid:
        thepo.msgstr[0] = csvtarget
      elif thecsv.source == pluralid:
        thepo.msgstr[1] = csvtarget
      elif simplify(thecsv.source) == simplify(singularid):
        thepo.msgstr[0] = csvtarget
      elif simplify(thecsv.source) == simplify(pluralid):
        thepo.msgstr[1] = csvtarget
      else:
        print >>sys.stderr, "couldn't work out singular or plural: %r, %r, %r" %  \
          (thecsv.source, singularid, pluralid)
        self.unmatched += 1
        return
    else:
      thepo.msgstr = csvtarget

  def convertfile(self, thecsvfile):
    """converts a csvfile to a pofile, and returns it. uses templatepo if given at construction"""
    self.csvfile = thecsvfile
    if self.pofile is None:
      self.pofile = po.pofile()
      mergemode = False
    else:
      mergemode = True
    if self.pofile.units and self.pofile.units[0].isheader():
      headerpo = self.pofile.units[0]
      headerpo.msgstr = [line.replace("CHARSET", "UTF-8").replace("ENCODING", "8bit") for line in headerpo.msgstr]
    else:
      headerpo = self.pofile.makeheader(charset="UTF-8", encoding="8bit")
    headerpo.othercomments.append("# extracted from %s\n" % self.csvfile.filename)
    mightbeheader = True
    for thecsv in self.csvfile.units:
      if self.charset is not None:
        thecsv.source = thecsv.source.decode(self.charset)
        thecsv.target = thecsv.target.decode(self.charset)
      if mightbeheader:
        # ignore typical header strings...
        mightbeheader = False
        if [item.strip().lower() for item in thecsv.comment, thecsv.source, thecsv.target] == \
           ["comment", "original", "translation"]:
          continue
        if len(thecsv.comment.strip()) == 0 and thecsv.source.find("Content-Type:") != -1:
          continue
      if mergemode:
        self.handlecsvunit(thecsv)
      else:
        thepo = self.convertelement(thecsv)
        self.pofile.units.append(thepo)
    self.pofile.removeduplicates(self.duplicatestyle)
    return self.pofile

  def getmissing(self):
    """get the number of missing translations..."""
    # TODO: work out how to print out the following if in verbose mode
    missing = 0
    for thepo in self.pofile.units:
      if thepo.isblankmsgstr():
        missing += 1

def convertcsv(inputfile, outputfile, templatefile, charset=None, columnorder=None, duplicatestyle="msgctxt"):
  """reads in inputfile using csvl10n, converts using csv2po, writes to outputfile"""
  inputcsv = csvl10n.csvfile(inputfile, fieldnames=columnorder)
  if templatefile is None:
    convertor = csv2po(charset=charset, duplicatestyle=duplicatestyle)
  else:
    templatepo = po.pofile(templatefile)
    convertor = csv2po(templatepo, charset=charset, duplicatestyle=duplicatestyle)
  outputpo = convertor.convertfile(inputcsv)
  if outputpo.isempty():
    return 0
  outputposrc = str(outputpo)
  outputfile.write(outputposrc)
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {("csv", "po"): ("po", convertcsv), ("csv", "pot"): ("po", convertcsv), 
             ("csv", None): ("po", convertcsv)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  parser.add_option("", "--charset", dest="charset", default=None,
    help="set charset to decode from csv files", metavar="CHARSET")
  parser.add_option("", "--columnorder", dest="columnorder", default=None,
    help="specify the order and position of columns (source,source,target)")
  parser.add_duplicates_option()
  parser.passthrough.append("charset")
  parser.passthrough.append("columnorder")
  parser.run(argv)

