#!/usr/bin/env python
# -*- coding: utf-8 -*

"""tests for Operator classes"""

import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import unittest
import Operator
import Status
import World
from translate.misc import wStringIO
from translate.storage import po
from PyQt4 import QtCore, QtGui

class TestOperator(unittest.TestCase):
    def setUp(self):
        self.operator = Operator.Operator()
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
        self.operator.store = self.poparse(self.message)
        
    def testGetUnits(self):
        dummyfile = wStringIO.StringIO(self.message)
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("newUnits"), self.slot)
        self.operator.getUnits(dummyfile)
        self.assertEqual(self.slotReached, True)
    
    def testEmitStatus(self):
        self.operator.status = Status.Status(self.operator.store.units)
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.slot)
        self.operator.emitStatus()
        self.assertEqual(self.slotReached, True)
    
    def testEmitCurrentIndex(self):
        self.operator._unitpointer = 0
        self.operator.filteredList = [0,1]
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.slot)
        self.operator.emitCurrentUnit()
        self.assertEqual(self.slotReached, True)
    
    def test_GetCurrentIndex(self):
        self.operator.filteredList = [0, 1]
        
        # test _unitpointer found in the list
        self.operator._unitpointer = 1
        self.assertEqual(self.operator._getCurrentIndex(), 1)
        
        # test _unitpointer not found in the list
        self.operator._unitpointer = 2
        self.assertEqual(self.operator._getCurrentIndex(), -1)
    
    def testFilteredFuzzy(self):
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter fuzzy is checked
        self.operator.filterFuzzy(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter fuzzy is unchecked
        self.operator.filterFuzzy(False)
        self.assertEqual(self.operator.filter, 6)
    
    def testFilterTranslated(self):
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter translated is checked
        self.operator.filterTranslated(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter translated is unchecked
        self.operator.filterTranslated(False)
        self.assertEqual(self.operator.filter, 5)
    
    def testFilterUntranslated(self):
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter untranslated is checked
        self.operator.filterUntranslated(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter untranslated is unchecked
        self.operator.filterUntranslated(False)
        self.assertEqual(self.operator.filter, 3)
    
    def testEmitFiltered(self):
        self.status = Status.Status(self.operator.store.units)
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("filteredList"), self.slot)
        self.operator.emitFiltered(World.fuzzy + World.translated + World.untranslated)
        self.assertEqual(self.slotReached, True)
    
    def testEmitUpdateUnit(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.slot)
        self.operator.filteredList = [0, 1]
        
        #test unitpointer is not None
        self.operator._unitpointer = 1
        self.operator.emitUpdateUnit()
        self.assertEqual(self.slotReached, True)
        
        #test unitpointer is None
        self.operator._unitpointer = None
        self.slotReached = False
        self.operator.emitUpdateUnit()
        self.assertEqual(not(self.slotReached), True)
    
    def testHeaderData(self):
    
        # test Header which is none
        self.assertEqual(self.operator.headerData(), ('', {}))
        
        # test Header which is not None and no Comment
        
    
    def testPrevious(self):
        self.operator._unitpointer = 1
        self.operator.filteredList = [0, 1]
        self.operator.previous()
        self.assertEqual(self.operator._unitpointer, 0)
    
    def testNext(self):
        self.operator._unitpointer = 0
        self.operator.filteredList = [0, 1]
        self.operator.next()
        self.assertEqual(self.operator._unitpointer, 1)
    
    def testFirst(self):
        self.operator._unitpointer = 1
        self.operator.filteredList = [0, 1]
        self.operator.first()
        self.assertEqual(self.operator._unitpointer, 0)
    
    def testLast(self):
        self.operator._unitpointer = 0
        self.operator.filteredList = [0, 1]
        self.operator.last()
        self.assertEqual(self.operator._unitpointer, 1)
    
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
    
    def slot(self):
        self.slotReached = True

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
