#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for Comment classes"""


import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import Comment
from translate.misc import wStringIO
from translate.storage import po
from PyQt4 import QtCore, QtGui
import unittest

class TestComment(unittest.TestCase):
    def setUp(self):
        self.commentObj = Comment.CommentDock(None)
        self.slotReached = False

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
        message = '''# aaaaa
#: kfaximage.cpp:189
#, fuzzy
msgid "Unable to open file for reading."
msgstr "unable to read file"
'''
        self.pofile = self.poparse(message)
        currentunit = self.pofile.units[0]
        self.commentObj.updateView(currentunit)
        self.assertEqual(str(self.commentObj.ui.txtTranslatorComment.toPlainText()), currentunit.getnotes())
        self.assertEqual(self.commentObj.ui.txtTranslatorComment.isEnabled(), True)
    
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
        
    def slot(self, text):
        self.slotReached = True
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
