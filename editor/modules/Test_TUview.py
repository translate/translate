import unittest
import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import TUview
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
        self.pofile = self.poparse(self.message)
    
    def testCloseEvent(self):
        close_event = QtGui.QCloseEvent()
        self.tuview.closeEvent(close_event)
        self.assertEqual(self.tuview.toggleViewAction().isChecked(), False)
    
    def testSetScrollbarMaximum(self):
        self.tuview.slotNewUnits(self.pofile.units)
        self.tuview.setScrollbarMaximum()
        self.assertEqual(self.tuview.ui.fileScrollBar.maximum(), len(self.pofile.units) - 1)  #fileScrollBar start from 0
        
    def testSlotNewUnits(self):
        self.tuview.slotNewUnits(self.pofile.units)
        self.assertEqual(len(self.tuview.indexes), len(self.pofile.units))
        self.assertEqual(self.tuview.ui.txtSource.isEnabled(), True)
        self.assertEqual(self.tuview.ui.txtTarget.isEnabled(), True)
    
    def testFilteredList(self):
        # test show only translated
        filter = World.translated
        fList = [1]
        self.tuview.filteredList(fList, filter)
        self.assertEqual(self.tuview.filter, filter)
        self.assertEqual(self.tuview.ui.fileScrollBar.maximum(), max(len(fList) - 1, 0))
        
        # test show fuzzy or untranslated
        filter = World.fuzzy + World.untranslated
        fList = [1]
        self.tuview.filteredList(fList, filter)
        self.assertEqual(self.tuview.filter, filter)
        self.assertEqual(self.tuview.ui.fileScrollBar.maximum(), max(len(fList) - 1, 0))
        
        # test show fuzzy, untranslated and translated
        filter = World.fuzzy + World.untranslated + World.translated
        fList = [2]
        self.tuview.filteredList(fList, filter)
        self.assertEqual(self.tuview.filter, filter)
        self.assertEqual(self.tuview.ui.fileScrollBar.maximum(), max(len(fList) - 1, 0))
    
    def testEmitCurrentIndex(self):
        QtCore.QObject.connect(self.tuview, QtCore.SIGNAL("currentIndex"), self.slot)
        self.tuview.slotNewUnits(self.pofile.units)
        self.tuview.emitCurrentIndex(1)
        self.assertEqual(self.slotReached, True)
    
    def testUpdateView(self):
        # test first-time updateview
        unit = self.pofile.units[0]
        index = 0
        state = World.fuzzy + World.untranslated
        self.tuview.slotNewUnits(self.pofile.units)
        self.tuview.updateView(unit, index, state)
        self.assertEqual(self.tuview.indexToUpdate, 0)
        
        # test second-time updateview
        unit = self.pofile.units[1]
        index = 1
        state = World.translated
        self.tuview.updateView(unit, index, state)
        self.assertEqual(self.tuview.indexToUpdate, 1)
    
    def testSetTarget(self):
        self.tuview.slotNewUnits(self.pofile.units)
        self.tuview.setTarget('hello')
        self.assertEqual(str(self.tuview.ui.txtTarget.toPlainText()), 'hello')
    
    def testCheckModified(self):
        QtCore.QObject.connect(self.tuview, QtCore.SIGNAL("targetChanged"), self.slot)
        self.tuview.ui.txtTarget.document().setModified(True)
        self.tuview.checkModified()
        self.assertEqual(self.slotReached, True)
    
    def testSetReadyForSave(self):
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
    
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
    
    def slot(self):
        self.slotReached = True
        
if __name__== '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
