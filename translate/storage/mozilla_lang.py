#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008, 2011 Zuza Software Foundation
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

# Original Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

"""A class to manage Mozilla .lang files."""

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
