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
msgstr "unable, to read file"

#: archivedialog.cpp:126
msgid "Could not open a temporary file"
msgstr "Could not open"
'''
        self.operator.store = self.poparse(self.message)
        
    def testGetUnits(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("newUnits"), self.slot)
        self.operator.getUnits(wStringIO.StringIO(self.message))
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
    
    def testMakeNewHeader(self):
        pass
    
    def testUpdateNewHeader(self):
        pass
        
    def testSaveStoreToFile(self):
        pass
        
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
    
    def testIndexToUnit(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.indexToUnit(1)
        self.assertEqual(self.operator._unitpointer, 1)
    
    def testToggleFuzzy(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.toggleFuzzy()
        self.assertEqual(self.operator.store.units[0].isfuzzy(), False)
    
    def testInitSearch(self):
        self.operator.initSearch('Aaa', [World.source, World.target, World.comment], False)
        self.assertEqual(self.operator.searchString, str('aaa'))
        self.assertEqual(self.operator.searchableText, [World.source, World.target, World.comment])
        self.assertEqual(self.operator.matchCase, False)
        
    def testSearchNext(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.initSearch('To', [World.source, World.target, World.comment], False)
        
        # first found search will encounter in source
        self.operator.searchNext()
        self.assertEqual(self.operator._getUnitString(), u'Unable to open file for reading.'.lower())
        self.assertEqual(self.operator.foundPosition, 7)
        
        # second found search will encounter in target
        self.operator.searchNext()
        self.assertEqual(self.operator._getUnitString(), u'unable, to read file'.lower())
        self.assertEqual(self.operator.foundPosition, 8)
        
        # then search will not found and read end of units
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("generalInfo"), self.slot)
        self.operator.searchNext()
        self.assertEqual(self.slotReached, True)
        self.assertEqual(self.operator.searchPointer, 1)
    
    def testSearchPrevious(self):
        self.operator.getUnits(wStringIO.StringIO(self.message))
        self.operator.setCurrentUnit(1)
        self.operator.initSearch('To', [World.source, World.target, World.comment], False)
        
        # first found search will encounter in target
        self.operator.searchPrevious()
        self.assertEqual(self.operator._getUnitString(), u'unable, to read file'.lower())
        self.assertEqual(self.operator.foundPosition, 8)
        
        # second found search will encounter in source
        self.operator.searchPrevious()
        self.assertEqual(self.operator._getUnitString(), u'Unable to open file for reading.'.lower())
        self.assertEqual(self.operator.foundPosition, 7)
        
        # then search will not found and read the beginning of units
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("generalInfo"), self.slot)
        self.operator.searchNext()
        self.assertEqual(self.slotReached, True)
        self.assertEqual(self.operator.searchPointer, 0)
    
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
    
    def slot(self):
        self.slotReached = True

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
