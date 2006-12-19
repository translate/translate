#!/usr/bin/env python
# -*- coding: utf-8 -*

"""tests for Operator classes"""

import sys
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
        self.operator.filteredList = self.operator.store.units
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.slot)
        self.operator.emitCurrentUnit()
        self.assertEqual(self.slotReached, True)
    
    def testFilteredFuzzy(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.filter = World.filterAll
        #test if filter fuzzy is checked
        self.operator.filterFuzzy(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter fuzzy is unchecked
        self.operator.filterFuzzy(False)
        self.assertEqual(self.operator.filter, 6)
    
    def testFilterTranslated(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter translated is checked
        self.operator.filterTranslated(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter translated is unchecked
        self.operator.filterTranslated(False)
        self.assertEqual(self.operator.filter, 5)
    
    def testFilterUntranslated(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter untranslated is checked
        self.operator.filterUntranslated(True)
        self.assertEqual(self.operator.filter, 7)
       
        #test if filter untranslated is unchecked
        self.operator.filterUntranslated(False)
        self.assertEqual(self.operator.filter, 3)
    
    def testEmitFiltered(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("filteredList"), self.slot)
        self.operator.emitFiltered(World.fuzzy + World.translated + World.untranslated)
        self.assertEqual(self.slotReached, True)
        
    def testEmitUpdateUnit(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.slot)
        self.operator.filteredList = self.operator.store.units
     
        #test unitpointer is less than or equal to length of filteredList
        self.operator._unitpointer = 1
        self.operator.emitUpdateUnit()
        self.assertEqual(self.slotReached, True)
     
        #test unitpointer is bigger than length of filteredList
        self.operator._unitpointer = 3
        self.slotReached = False
        self.operator.emitUpdateUnit()
        self.assertEqual(not(self.slotReached), True)
        
    def testHeaderData(self):
    
        # test message Header which has no data
        self.assertEqual(self.operator.headerData(), ('', {}))
     
        # test message Header which has data
        self.message = '''msgid ""
msgstr ""
"POT-Creation-Date: 2005-05-18 21:23+0200\n"
"PO-Revision-Date: 2006-11-27 11:50+0700\n"
"Project-Id-Version: cupsdconf\n"
""
# aaaaa
#: kfaximage.cpp:189
msgid "Unable to open file for reading."
msgstr "unable to read file"
'''
        self.operator.store = self.poparse(self.message)
        self.assertEqual(self.operator.headerData(), ('', {'POT-Creation-Date': u'2005-05-18 21:23+0200', 'PO-Revision-Date': u'2006-11-27 11:50+0700', 'Project-Id-Version': u'cupsdconf'}))
        
##    def testPrevious(self):
##        self.operator._unitpointer = 1
##        self.operator.filteredList = self.operator.store.units
##        self.operator.previous()
##        self.assertEqual(self.operator._unitpointer, 0)
##    
##    def testNext(self):
##        self.operator._unitpointer = 0
##        self.operator.filteredList = self.operator.store.units
##        self.operator.next()
##        self.assertEqual(self.operator._unitpointer, 1)
##    
##    def testFirst(self):
##        self.operator._unitpointer = 1
##        self.operator.filteredList = self.operator.store.units
##        self.operator.first()
##        self.assertEqual(self.operator._unitpointer, 0)
##        
##    def testLast(self):
##        self.operator._unitpointer = 0
##        self.operator.filteredList = self.operator.store.units
##        self.operator.last()
##        self.assertEqual(self.operator._unitpointer, 1)
    
    def testModified(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        # test it will return True, if _modified is true
        self.operator._modified = True
        self.assertEqual(self.operator.modified(), True)
        
        # test it will return False, if _modified is False
        self.operator._modified = False
        self.assertEqual(self.operator.modified(), False)
        
    def testSetComment(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator._unitpointer = 1
        self.operator.setComment('comments')
        self.assertEqual(self.operator.filteredList[self.operator._unitpointer].getnotes(), u'comments')
    
    def testSetTarget(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator._unitpointer = 1
        self.operator.setTarget('target')
        self.assertEqual(self.operator.filteredList[self.operator._unitpointer].target, u'target')
    
    def testSetCurrentUnit(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.setCurrentUnit(1)
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
