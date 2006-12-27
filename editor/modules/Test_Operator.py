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
msgstr "Could not open any"
'''
        
    def testsetNewStore(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("newUnits"), self.slot)
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.assertEqual(self.slotReached, True)
    
    def testEmitStatus(self):
        self.operator.status = Status.Status(po.pofile.parsestring(self.message).units)
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.slot)
        self.operator.emitStatus()
        self.assertEqual(self.slotReached, True)
    
    def testEmitUnit(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.slot)
        unit = po.pofile.parsestring(self.message).units[0]
        
        # test case unit has no attribute x_editor_index
        self.operator.emitUnit(unit)
        self.assertEqual(self.operator.currentUnitIndex, None)
        self.assertEqual(self.slotReached, True)
        
        # test case unit has attribute x_editor_index
        unit.x_editor_index = 1
        self.operator.emitUnit(unit)
        self.assertEqual(self.operator.currentUnitIndex, 1)
        self.assertEqual(self.slotReached, True)
        
    def testFilteredFuzzy(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.filter = World.filterAll
        #test if filter fuzzy is checked
        self.operator.filterFuzzy(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter fuzzy is unchecked
        self.operator.filterFuzzy(False)
        self.assertEqual(self.operator.filter, 6)
    
    def testFilterTranslated(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter translated is checked
        self.operator.filterTranslated(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter translated is unchecked
        self.operator.filterTranslated(False)
        self.assertEqual(self.operator.filter, 5)
    
    def testFilterUntranslated(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.status = Status.Status(self.operator.store.units)
        
        self.operator.filter = World.filterAll
        #test if filter untranslated is checked
        self.operator.filterUntranslated(True)
        self.assertEqual(self.operator.filter, 7)
       
        #test if filter untranslated is unchecked
        self.operator.filterUntranslated(False)
        self.assertEqual(self.operator.filter, 3)
    
    def testEmitFiltered(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.slot)
        self.operator.emitFiltered(World.fuzzy + World.translated + World.untranslated)
        self.assertEqual(self.slotReached, True)
        
    def testEmitUpdateUnit(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.slot)
     
        #test case self.store is valid
        self.operator.store = po.pofile.parsestring(self.message)
        self.operator.emitUpdateUnit()
        self.assertEqual(self.slotReached, True)
     
        #test case self.store is none
        self.operator.store = None
        self.slotReached = False
        self.operator.emitUpdateUnit()
        self.assertEqual(self.slotReached, False)
        
    def testHeaderData(self):
    
        # test message Header which has no data
        self.operator.store = po.pofile.parsestring(self.message)
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
        self.operator.store = po.pofile.parsestring(self.message)
        self.assertEqual(self.operator.headerData(), ('', {'POT-Creation-Date': u'2005-05-18 21:23+0200', 'PO-Revision-Date': u'2006-11-27 11:50+0700', 'Project-Id-Version': u'cupsdconf'}))
    
    def testMakeNewHeader(self):
        pass
    
    def testUpdateNewHeader(self):
        pass
        
    def testSaveStoreToFile(self):
        pass
        
    def testModified(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        # test it will return True, if _modified is true
        self.operator._modified = True
        self.assertEqual(self.operator.modified(), True)
        
        # test it will return False, if _modified is False
        self.operator._modified = False
        self.assertEqual(self.operator.modified(), False)
        
    def testSetComment(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.currentUnitIndex = 1
        self.operator.setComment('comments')
        self.assertEqual(self.operator.filteredList[self.operator.currentUnitIndex].getnotes(), u'comments')
    
    def testSetTarget(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.currentUnitIndex = 1
        self.operator.setTarget('target')
        self.assertEqual(self.operator.filteredList[self.operator.currentUnitIndex].target, u'target')
    
    def testToggleFuzzy(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.toggleFuzzy()
        self.assertEqual(self.operator.store.units[0].isfuzzy(), False)
    
    def testInitSearch(self):
        self.operator.initSearch('Aaa', [World.source, World.target, World.comment], False)
        self.assertEqual(self.operator.searchString, str('aaa'))
        self.assertEqual(self.operator.searchableText, [World.source, World.target, World.comment])
        self.assertEqual(self.operator.matchCase, False)
        
    def testSearchNext(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
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
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.searchPointer = 1
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
    
    def testReplace(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("replaceText"), self.slot)
        self.operator.initSearch("unable,", [World.source, World.target, World.comment], False)
        self.operator.replace("to")
        self.assertEqual(self.slotReached, True)
        self.assertEqual(self.operator.searchableText[self.operator.currentTextField], 2)
        self.assertEqual(self.operator.foundPosition, 0)
    
    def test_getUnitString(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.searchableText = [World.source, World.target]
        self.operator.matchCase = True
        self.operator.currentTextField = 1
        self.assertEqual(self.operator._getUnitString(), u"unable, to read file")
    
    def testSearchFound(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("searchResult"), self.slot)
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.operator.initSearch("temporary", [World.source, World.target], True)
        self.operator.searchNext()
        self.assertEqual(self.slotReached, True)
        self.assertEqual(self.operator.searchableText[self.operator.currentTextField], 1)
    
    def test_SearchNotFound(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("searchResult"), self.slot)
        self.operator.searchableText = [World.source, World.target]
        self.operator.currentTextField = 0
        self.operator._searchNotFound()
        self.assertEqual(self.slotReached, True)
    
    def slot(self):
        self.slotReached = True

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
