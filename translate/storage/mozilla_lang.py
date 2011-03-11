#!/usr/bin/env python

# lang.py
# Defines standard translation-toolkit structions for .lang files

# Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

from translate.storage import base
from translate.storage import txt


class LangUnit(base.TranslationUnit):
    """This is just a normal unit with a weird string output"""

    def __init__(self, source=None):
        self.locations = []
        base.TranslationUnit.__init__(self, source)

    def __str__(self):
        return u";%s\n%s" % (self.source, self.target)

    def getlocations(self):
        return self.locations

    def addlocation(self, location):
        self.locations.append(location)


class LangStore(txt.TxtFile):
    """We extend TxtFile, since that has a lot of useful stuff for encoding"""
    UnitClass = LangUnit

    def parse(self, lines):
        #Have we just seen a ';' line, and so are ready for a translation
        readyTrans = False

        if not isinstance(lines, list):
            lines = lines.split("\n")
        for lineoffset, line in enumerate(lines):
            line = line.rstrip("\n").rstrip("\r")

            if len(line) == 0: #Skip blank lines
                continue

            if readyTrans: #If we are expecting a translation, set the target
                u.target = line
                readyTrans = False #We already have our translation
                continue

            if line.startswith(';'):
                u = self.addsourceunit(line[1:])
                readyTrans = True # Now expecting a translation on the next line
                u.addlocation("%s:%d" % (self.filename, lineoffset + 1))

    def __str__(self):
        return u"\n\n".join([unicode(unit) for unit in self.units]).encode('utf-8')
