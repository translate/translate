#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module stores status

from translate.tools import pocount
import modules.World as World

class Status:
    def __init__(self, units):
        self.numTotal = len(units)
        self.numFuzzy = len(pocount.fuzzymessages(units))
        self.numTranslated = len(pocount.translatedmessages(units))
        self.numUntranslated = self.numTotal - self.numTranslated
    
    def addNumFuzzy(self, value):
        """calculate the number of fuzzy messages."""
        self.numFuzzy += value
    
    def addNumTranslated(self, value):
        """calculate the number of translated/untranslated messages."""
        self.numTranslated += value
        self.numUntranslated = self.numTotal - self.numTranslated
    
    def getStatus(self, unit):
        """return the status (as integer) of unit."""
        unitState = 0
        if unit.isfuzzy():
            unitState += World.fuzzy
        if unit.istranslated():
            unitState += World.translated
        else:
            unitState += World.untranslated
        # add unit to filteredList if it is in the filter
        return unitState
    
    def statusString(self):
        """return string of total, fuzzy, translated, and untranslated messages."""
        return "Total: "+ str(self.numTotal) + \
                "  |  Fuzzy: " +  str(self.numFuzzy) + \
                "  |  Translated: " +  str(self.numTranslated) + \
                "  |  Untranslated: " + str(self.numUntranslated)
        
