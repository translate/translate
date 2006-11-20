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


from PyQt4 import QtCore

# helper constants for filtering
fuzzy = 1
translated = 2
untranslated = 4
filterAll = 4 + 2 + 1

source = 1
target = 2
comment = 4

searchForward = 1
searchBackward = 2
searchStatic = 4

# this is the global settings object, use only this for saving and restoring settings
settings = QtCore.QSettings("WordForge", "Translation Editor")

# maximum number of files in the recent file menu
MaxRecentFiles = 10

