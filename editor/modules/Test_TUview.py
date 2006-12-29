#!/usr/bin/python
# -*- coding: utf8 -*-

# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
#
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

 
# This module is working on tests for TUview classes

import unittest
import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import TUview
import Status
import World
from PyQt4 import QtGui, QtCore
from translate.misc import wStringIO
from translate.storage import po

class TestTUview(unittest.TestCase):
    def setUp(self):
        self.tuview = TUview.TUview(None)
        self.slotReached = False
        self.message = '''# aaaaa
#: kfaximage.cpp:189
#, fuzzy
msgid "Unable to open file for reading."
msgstr "unable to read file"

#: archivedialog.cpp:126
msgid "Could not open a temporary file"
msgstr "Could not open"
'''
        self.store = po.pofile.parsestring(self.message)
        self.status = Status.Status(self.store.units)

    def testCloseEvent(self):
        close_event = QtGui.QCloseEvent()
        self.tuview.closeEvent(close_event)
        self.assertEqual(self.tuview.toggleViewAction().isChecked(), False)
    
    def testSetScrollbarMaximum(self):
        self.tuview.setScrollbarMaxValue(2)
        self.assertEqual(self.tuview.ui.fileScrollBar.maximum(), 1)  #fileScrollBar start from 0
    
    def testEmitCurrentIndex(self):
        self.tuview.setScrollbarMaxValue(4)
        QtCore.QObject.connect(self.tuview, QtCore.SIGNAL("filteredIndex"), self.slot)
        self.tuview.ui.fileScrollBar.setValue(4)
        self.assertEqual(self.slotReached, True)
    
    def testFilterChanged(self):
        filter = World.fuzzy + World.translated + World.untranslated
        self.tuview.filterChanged(filter, 2)
        self.assertEqual(self.tuview.filter, filter)
        
    def testUpdateView(self):
        # test unit has no x_editor_filterIndex
        unit = self.store.units[0]
        self.tuview.updateView(unit)
        self.assertEqual(self.tuview.ui.txtSource.isEnabled(), False)
        self.assertEqual(self.tuview.ui.txtTarget.isEnabled(), False)
        
        # test unit has x_editor_filterIndex
        unit.x_editor_filterIndex = 0
        self.tuview.updateView(unit)
        self.assertEqual(self.tuview.ui.txtSource.toPlainText(), unit.source)
        self.assertEqual(self.tuview.ui.txtTarget.toPlainText(), unit.target)
    
    def testCheckModified(self):
        QtCore.QObject.connect(self.tuview, QtCore.SIGNAL("targetChanged"), self.slot)
        self.tuview.ui.txtTarget.document().setModified(True)
        self.tuview.checkModified()
        self.assertEqual(self.slotReached, True)
    
    def testEmitReadyForSave(self):
        QtCore.QObject.connect(self.tuview, QtCore.SIGNAL("readyForSave"), self.slot)
        self.tuview.ui.txtTarget.setPlainText('hello')
        self.assertEqual(self.slotReached, True)
    
    def testSource2Target(self):
        self.tuview.ui.txtSource.setPlainText('a')
        self.tuview.source2target()
        self.assertEqual(self.tuview.ui.txtSource.toPlainText(), self.tuview.ui.txtTarget.toPlainText())
    
    def testHighLightSearch(self):
        position = 0
        length = 2
        self.tuview.ui.txtSource.setPlainText('hello')
        self.tuview.highlightSearch(World.source, position, length)
        self.assertEqual(self.tuview.highlightRange.start, position)
        self.assertEqual(self.tuview.highlightRange.length, length )
        
    def testReplaceText(self):
        position = 0
        length = 2
        self.tuview.ui.txtTarget.setPlainText('hello')
        self.tuview.replaceText(World.target, position, length, 'k')
        self.assertEqual(str(self.tuview.ui.txtTarget.toPlainText()), 'kllo')
    
    def slot(self):
        self.slotReached = True
        
if __name__== '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
