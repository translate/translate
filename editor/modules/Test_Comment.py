#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for Comment classes"""


import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import Comment
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
        
    def slot(self, text):
        self.slotReached = True

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
