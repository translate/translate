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

"""takes a .po translation file and produces word counts and other statistics"""

import sys
import os
from translate.storage import po
import sre

if not hasattr(__builtins__, "sum"):
  def sum(parts):
    return reduce(int.__add__, parts, 0)

def untranslatedwords(pair):
  original, translation = pair
  if translation.words != 0: return 0
  return original.words

def wordcount(postr):
  # TODO: po class should understand KDE style plurals and comments
  postr = sre.sub("^_n: ", "", postr)
  postr = sre.sub("^_: .*?\\n", "", postr)
  postr = sre.sub("<br>", "\n", postr)
  postr = sre.sub("<[^>]+>", "", postr)
  postr = sre.sub("\\D\\.\\D", " ", postr)
  return len(postr.split())

def wordsinpoel(poel):
  """counts the words in the msgid, msgstr, taking plurals into account"""
  (msgidwords, msgstrwords) = (0, 0)
  for s in poel.source.strings:
    msgidwords += wordcount(s)
  for s in poel.target.strings:
    msgstrwords += wordcount(s)
  return msgidwords, msgstrwords

def summarize(title, units, CSVstyle=False):
  # ignore totally blank or header units
  units = filter(lambda poel: not poel.isheader(), units)
  translated = translatedmessages(units)
  fuzzy = fuzzymessages(units)
  review = filter(lambda poel: poel.isreview(), units)
  untranslated = untranslatedmessages(units)
  wordcounts = dict(map(lambda poel: (poel, wordsinpoel(poel)), units))
  msgidwords = lambda elementlist: sum(map(lambda poel: wordcounts[poel][0], elementlist))
  msgstrwords = lambda elementlist: sum(map(lambda poel: wordcounts[poel][1], elementlist))
  if CSVstyle:
    print "%s, " % title,
    print "%d, %d, %d," % (len(translated), msgidwords(translated), msgstrwords(translated)),
    print "%d, %d," % (len(fuzzy), msgidwords(fuzzy)),
    print "%d, %d," % (len(untranslated), msgidwords(untranslated)),
    print "%d, %d" % (len(translated) + len(fuzzy) + len(untranslated), msgidwords(translated) + msgidwords(fuzzy) + msgidwords(untranslated)),
    if len(review) > 0:
      print ", %d, %d" % (len(review), msgidwords(review)),
    print
  else:
    print title
    print "type           strings words (source) words (translation)"
    print "translated:   %5d %10d %15d" % (len(translated), msgidwords(translated), msgstrwords(translated))
    print "fuzzy:        %5d %10d             n/a" % (len(fuzzy), msgidwords(fuzzy))
    print "untranslated: %5d %10d             n/a" % (len(untranslated), msgidwords(untranslated))
    print "Total:        %5d %10d %15d" % (len(translated) + len(fuzzy) + len(untranslated), msgidwords(translated) + msgidwords(fuzzy) + msgidwords(untranslated), msgstrwords(translated))
    if len(review) > 0:
      print "review:       %5d %10d             n/a" % (len(review), msgidwords(review))
    print

def fuzzymessages(units):
    return filter(lambda unit: unit.isfuzzy() and unit.target, units)

def translatedmessages(units):
    return filter(lambda unit: unit.istranslated(), units)

def untranslatedmessages(units):
    return filter(lambda unit: not (unit.istranslated() or unit.isfuzzy()), units)

class summarizer:
  def __init__(self, filenames, CSVstyle):
    self.allelements = []
    self.filecount = 0
    self.CSVstyle = CSVstyle
    if self.CSVstyle:
      print "Filename, Translated Messages, Translated Source Words, Translated \
Target Words, Fuzzy Messages, Fuzzy Source Words, Untranslated Messages, \
Untranslated Source Words, Total Message, Total Source Words, \
Review Messages, Review Source Words"
    for filename in filenames:
      if not os.path.exists(filename):
        print >>sys.stderr, "cannot process %s: does not exist" % filename
        continue
      elif os.path.isdir(filename):
        self.handledir(filename)
      else:
        self.handlefile(filename)
    if self.filecount > 1 and not self.CSVstyle:
      summarize("TOTAL:", self.allelements)
      print "File count:   %5d" % (self.filecount)
      print

  def handlefile(self, filename):
    infile = open(filename)
    pof = po.pofile()
    pof.parse(infile.read())
    infile.close()
    self.allelements.extend(pof.units)
    summarize(filename, pof.units, self.CSVstyle)
    self.filecount += 1

  def handlefiles(self, arg, dirname, filenames):
    for filename in filenames:
      pathname = os.path.join(dirname, filename)
      if not os.path.isdir(pathname):
        self.handlefile(pathname)

  def handledir(self, dirname):
    os.path.walk(dirname, self.handlefiles, None)

def main():
  # TODO: make this handle command line options using optparse...
  CSVstyle = False
  if "--csv" in sys.argv:
    sys.argv.remove("--csv")
    CSVstyle = True
  summarizer(sys.argv[1:], CSVstyle)

