#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for Comment classes"""


import sys
import Comment
from translate.misc import wStringIO
from translate.storage import po
from PyQt4 import QtCore, QtGui
import unittest
import World

class TestComment(unittest.TestCase):
    def setUp(self):
        self.commentObj = Comment.CommentDock(None)
        self.slotReached = False
        self.message = '''# aaaaa
#: kfaximage.cpp:189
#, fuzzy
msgid "Unable to open file for reading."
msgstr "unable to read file"
'''
        self.pofile = self.poparse(self.message)
        self.currentunit = self.pofile.units[0]

    def testCheckModified(self):
        QtCore.QObject.connect(self.commentObj, QtCore.SIGNAL("commentChanged"), self.slot)
        self.commentObj.ui.txtTranslatorComment.document().setModified(True)
        self.commentObj.checkModified()
        self.assertEqual(self.slotReached, True)
    
    def testCloseEvent(self):
        close_event = QtGui.QCloseEvent()
        self.commentObj.closeEvent(close_event)
        self.assertEqual(self.commentObj.toggleViewAction().isChecked(), False)
    
    def testUpdateView(self):
        self.commentObj.updateView(self.currentunit)
        self.assertEqual(str(self.commentObj.ui.txtTranslatorComment.toPlainText()), self.currentunit.getnotes())
        self.assertEqual(self.commentObj.ui.txtTranslatorComment.isEnabled(), True)
    
    def testHighLightSearch(self):
        position = 0
        length = 2
        self.commentObj.updateView(self.currentunit)
        self.commentObj.highlightSearch(World.comment, position, length)
        self.assertEqual(self.commentObj.highlightRange.start, position)
        self.assertEqual(self.commentObj.highlightRange.length, length )
    
    def testEmitReadyForSave(self):
        QtCore.QObject.connect(self.commentObj, QtCore.SIGNAL("readyForSave"), self.slot)
        self.commentObj.updateView(self.currentunit)
        self.assertEqual(self.slotReached, True)
    
    def testReplaceText(self):
        position = 0
        length = 2
        self.commentObj.updateView(self.currentunit)
        self.commentObj.replaceText(World.comment, position, length, 'k')
        self.assertEqual(str(self.commentObj.ui.txtTranslatorComment.toPlainText()), 'kaaa')
    
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
        
    def slot(self):
        self.slotReached = True
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
