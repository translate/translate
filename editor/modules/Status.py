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
        self.units = units
    
    def getStatus(self, unit):
        """return the unit's status flag."""
        unitState = 0
        if unit.isfuzzy():
            unitState += World.fuzzy
        if unit.istranslated():
            unitState += World.translated
        else:
            unitState += World.untranslated
        return unitState
        
    def statusString(self):
        """return string of total, fuzzy, translated, and untranslated messages."""
        numTotal = len(self.units)
        numFuzzy = len(pocount.fuzzymessages(self.units))
        numTranslated = len(pocount.translatedmessages(self.units))
        numUntranslated = numTotal - numTranslated
        return "Total: "+ str(numTotal) + \
                "  |  Fuzzy: " +  str(numFuzzy) + \
                "  |  Translated: " +  str(numTranslated) + \
                "  |  Untranslated: " + str(numUntranslated)

