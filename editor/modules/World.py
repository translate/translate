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
# This module stores global variables for use in whole applicaion.

class World:
    def __init__(self):
        self.fuzzy = 1
        self.translated = 2
        self.untranslated = 4
        
        self.source = 1
        self.target = 2
        self.comment = 4
        self.searchableText = [self.source, self.target, self.comment]
        
        self.searchForward = 1
        self.searchBackward = 2
        self.searchStatic = 4
        
        
        self.settingOrg = "WordForge"
        self.settingApp = "Translation Editor"
        
