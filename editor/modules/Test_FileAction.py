#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for FileAction classes"""

import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
import FileAction
from PyQt4 import QtCore, QtGui
import unittest

class TestFileAction(unittest.TestCase):
    def setUp(self):
        self.fileActionObj = FileAction.FileAction(None)
        self.isFileName = False
        self.fileName = ""
        
    def testOpenFile(self):
        QtCore.QObject.connect(self.fileActionObj, QtCore.SIGNAL("fileOpened"), self.slot)
        self.isFileName = self.fileActionObj.openFile()
        if self.isFileName:
            self.assertEqual(self.fileName, "example")
        else:
            self.assertEqual(self.fileName, "")
        
    def slot(self):
        self.fileName = "example"
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
