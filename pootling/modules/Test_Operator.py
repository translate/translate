#!/usr/bin/env python
# -*- coding: utf-8 -*

# Pootling
# Copyright 2006 WordForge Foundation
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
# 
# This module is working on tests for Operator classes


import sys
import os
import unittest
import time
import Operator
import Status
import World
import tempfile
from translate.storage import factory
from translate.misc import wStringIO
from translate.storage import po
from PyQt4 import QtCore, QtGui
import __version__

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
        self.operator.status = Status.Status(po.pofile.parsestring(self.message))
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.slot)
        self.operator.emitStatus()
        self.assertEqual(self.slotReached, True)
    
    def testEmitUnit(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.slot)
        unit = po.pofile.parsestring(self.message).units[0]
        unit.x_editor_filterIndex = 1
        
        # test case unit has no attribute x_editor_index
        self.operator.emitUnit(unit)
        self.assertEqual(self.operator.currentUnitIndex, 1)
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
        self.status = Status.Status(self.operator.store)
        
        self.operator.filter = World.filterAll
        #test if filter translated is checked
        self.operator.filterTranslated(True)
        self.assertEqual(self.operator.filter, 7)
        
        #test if filter translated is unchecked
        self.operator.filterTranslated(False)
        self.assertEqual(self.operator.filter, 5)
    
    def testFilterUntranslated(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        self.status = Status.Status(self.operator.store)
        
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
        """Test that it really createsa new header based on a given information in headerDic."""
        
        headerDic = {'charset':"CHARSET", 'encoding':"ENCODING", 'project_id_version': '1.po', 'pot_creation_date':None, 'po_revision_date': False, 'last_translator': 'AAA', 'language_team': 'KhmerOS', 'mime_version':None, 'plural_forms':None, 'report_msgid_bugs_to':None}
        
##        self.assertEqual(self.operator.store.x_generator, World.settingOrg + ' ' + World.settingApp + ' ' + __version__.ver)
        # test self.store is not instance of poheader.poheader()
        self.store = None
        self.assertEqual(self.operator.makeNewHeader(headerDic), {})
        
        # test self.store is instance of poheader.poheader()
        self.operator.store = po.pofile.parsestring(self.message)
        result = {'PO-Revision-Date': time.strftime("%Y-%m-%d %H:%M%z"), 'X-Generator': World.settingApp + ' ' + __version__.ver, 'Content-Transfer-Encoding': 'ENCODING', 'Plural-Forms': 'nplurals=INTEGER; plural=EXPRESSION;', 'Project-Id-Version': '1.po', 'Report-Msgid-Bugs-To': '', 'Last-Translator': 'AAA', 'Language-Team': 'KhmerOS', 'POT-Creation-Date': time.strftime("%Y-%m-%d %H:%M%z"), 'Content-Type': 'text/plain; charset=CHARSET', 'MIME-Version': '1.0'}
        self.assertEqual(self.operator.makeNewHeader(headerDic), result)
    
    def testUpdateNewHeader(self):
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
        # test self.store is not instance of poheader.poheader()
        self.store = None
        self.assertEqual(self.operator.updateNewHeader(None, None), {})
        
        # test self.store is instance of poheader.poheader()
        self.operator.store = po.pofile.parsestring(self.message)
        otherComment = "hello comment"
        headerDic = {"POT-Creation-Date":" 2005-05-18 21:23+0200",
"PO-Revision-Date":" 2007-02-22 11:50+0700",
"Project-Id-Version": "cupsdconf_new", "AAA":"BBB"}
        self.operator.updateNewHeader(otherComment, headerDic)
        self.assertEqual(self.operator.store.header().getnotes(), "hello comment")
        result = u'Project-Id-Version: cupsdconf_new\nReport-Msgid-Bugs-To: \nPOT-Creation-Date:  2005-05-18 21:23+0200\nPO-Revision-Date:  2007-02-22 11:50+0700\nLast-Translator: FULL NAME <EMAIL@ADDRESS>\nLanguage-Team: LANGUAGE <LL@li.org>\nMIME-Version: 1.0\nContent-Type: text/plain; charset=CHARSET\nContent-Transfer-Encoding: ENCODING\nPlural-Forms: nplurals=INTEGER; plural=EXPRESSION;\nX-Generator: ' + self.operator.store.x_generator + '\nAAA: BBB\n'
        self.assertEqual(self.operator.store.header().target, result)
        
    def testSaveStoreToFile(self):
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("headerAuto"), self.slot)
        self.operator.store = po.pofile.parsestring(self.message)
        handle, filename = tempfile.mkstemp('.po')
        
        # test headerAuto value is True
        World.settings.setValue("headerAuto", QtCore.QVariant(True))
        self.operator.saveStoreToFile(filename)
        self.assertEqual(self.slotReached, True)
        self.assertEqual(len(factory.getobject(filename).units), 2)
        
        # test headerAuto is False
        self.slotReached = False
        World.settings.setValue("headerAuto", QtCore.QVariant(False))
        self.operator.saveStoreToFile(filename)
        self.assertEqual(self.slotReached, False)
        
        os.remove(filename)
        
    def testgetModified(self):
        self.operator.setNewStore(po.pofile.parsestring(self.message))
        # test it will return True, if modified is true
        self.operator.modified = True
        self.assertEqual(self.operator.getModified(), True)
        
        # test it will return False, if modified is False
        self.operator.modified = False
        self.assertEqual(self.operator.getModified(), False)
        
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
        self.assertEqual(self.operator.searchPointer, 0)
    
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
