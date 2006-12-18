#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for FileAction classes"""

import sys
import FileAction
from PyQt4 import QtCore, QtGui
import unittest

class TestFileAction(unittest.TestCase):
    def setUp(self):
        self.fileActionObj = FileAction.FileAction(None)
        self.slotReached = False
        self.fileName = ""
        
    def testOpenFile(self):
        QtCore.QObject.connect(self.fileActionObj, QtCore.SIGNAL("fileOpened"), self.slot)
        isFileName = self.fileActionObj.openFile()
        if isFileName:
            self.assertEqual(self.slotReached, True)
            self.assertEqual(len(self.fileName) > 0, True)
        else:
            self.assertEqual(self.slotReached, False)
    
    def testSave(self):
        QtCore.QObject.connect(self.fileActionObj, QtCore.SIGNAL("fileSaved"), self.slot)
        self.fileActionObj.fileName = QtCore.QString("example")
        self.fileActionObj.save()
        self.assertEqual(self.fileName, self.fileActionObj.fileName)
        
    def testSaveAs(self):
        self.fileActionObj.fileName = "example.po"
        self.fileActionObj.fileExtension = ".po"
        QtCore.QObject.connect(self.fileActionObj, QtCore.SIGNAL("fileSaved"), self.slot)
        self.fileActionObj.saveAs()
        if (len(self.fileName) > 0):
            self.assertEqual(QtCore.QString(self.fileName).endsWith("po",  QtCore.Qt.CaseInsensitive), True)
     
    def slot(self, fileName):
        self.fileName = fileName
        self.slotReached = True    
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    unittest.main()
