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

    def markFuzzy(self, unit, fuzzy):
        unit.markfuzzy(fuzzy)
        if (fuzzy):
            unit.x_editor_state |= World.fuzzy
            unit.x_editor_state &= ~World.translated
        else:
            unit.x_editor_state &= ~World.fuzzy
            unit.x_editor_state |= World.translated

    def markTranslated(self, unit, translated):
        if (translated):
            if (not hasattr(unit, "x_editor_state")) or (unit.x_editor_state & World.translated):
                return
            unit.x_editor_state |= World.translated
            unit.x_editor_state &= ~World.untranslated
        else:
            if (unit.x_editor_state & World.untranslated):
                return
            unit.x_editor_state &= ~World.translated
            unit.x_editor_state |= World.untranslated
        if (unit.isfuzzy()):
            unit.markfuzzy(False)
            unit.x_editor_state &= ~World.fuzzy

    def getStatus(self, unit):
        """return the unit's status flag."""
        unitState = 0
        if (unit.isheader()):
            return World.header
        if (unit.istranslated()):
            unitState |= World.translated
        elif (unit.isfuzzy()):
            unitState |= World.fuzzy
        else:
            unitState |= World.untranslated
        return unitState
    
