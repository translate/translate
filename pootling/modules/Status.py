#!/usr/bin/python
# -*- coding: utf8 -*-
# Pootling
# Copyright 2006 WordForge Foundation
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module stores status

import pootling.modules.World as World

class Status:
    
    # FIXME: toggle unit's fuzzy is not working
    def __init__(self, store):
        self.store = store
        self.numTranslated = store.translated_unitcount()
        self.numFuzzy = store.fuzzy_unitcount()
        self.numUntranslated = store.untranslated_unitcount()
        self.numTotal = self.numTranslated + self.numFuzzy + self.numUntranslated
    
    def unitState(self, unit):
        """
        return bitwise indicating state of unit.
        bitwises are defined in World class.
        """
        state = 0
        if (unit.isheader()):
            return state
        if (unit.isfuzzy()):
            state += World.fuzzy
        elif (unit.istranslated()):
            state += World.translated
        else:
            state += World.untranslated
        return state
        
    def markFuzzy(self, unit, fuzzy):
        unit.markfuzzy(fuzzy)
        if (fuzzy):
            self.numFuzzy += 1
            self.numTranslated -= 1
            unit.x_editor_state |= World.fuzzy
            unit.x_editor_state &= ~World.translated
        else:
            self.numFuzzy -= 1
            self.numTranslated += 1
            unit.x_editor_state &= ~World.fuzzy
            unit.x_editor_state |= World.translated

    def markTranslated(self, unit, translated):
        if (unit.isfuzzy()):
            self.markFuzzy(unit, False)

        if (translated):
            if (not hasattr(unit, "x_editor_state")) or (unit.x_editor_state & World.translated):
                return
            self.numTranslated += 1
            unit.x_editor_state |= World.translated
            unit.x_editor_state &= ~World.untranslated
        else:
            if (unit.x_editor_state & World.untranslated):
                return
            self.numTranslated -= 1
            unit.x_editor_state &= ~World.translated
            unit.x_editor_state |= World.untranslated
    
    def statusString(self):
        '''show total of messages in a file, fuzzy, translated messages and untranslate  messages which are not fuzzy.
        
        '''
        # Untranslated messages, here, are not fuzzy messages (for user-easy understainding)
        statusString = "Total: " + str(self.numTotal) + "  |  " + \
                "Fuzzy: " +  str(self.numFuzzy) + "  |  " + \
                "Translated: " +  str(self.numTranslated) + "  |  " + \
                "Untranslated: " + str(self.numTotal - self.numTranslated - self.numFuzzy)
        return statusString
    
