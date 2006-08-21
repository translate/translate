#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# (c) 2006 WordForge Foundation, all rights reserved.
#
# Version 1.0
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details.
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)
#

from PyQt4 import QtCore, QtGui
import sys

class FileAction(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)        
        self.fileName = None
        
    def openFile(self):        
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open Xliff File"),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr("XLIFF Files (*.xliff *.xlf);; Po File (*.po)"))        
        if not self.fileName.isEmpty():
            self.emitFileOpened()

    def save(self):        
        if not self.fileName.isEmpty():
            self.emitFileName()

    def saveAs(self):        
        # TODO: set selected Filter to all support Files        
        ret = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),
                                                     QtCore.QDir.currentPath(), self.tr("XLIFF Files (*.xliff *.xlf);; Po File (*.po)"))
        # TODO: Detect which buttion is clicked (Save or Cancel)
        if not ret.isEmpty():
            self.fileName   = ret            
            self.emitFileName()            
        # TODO: create a saved file with an extension
    
    def aboutToSave(self, main):                    
            ret = QtGui.QMessageBox.question(main, self.tr("File Modified"),
                        self.tr("The file has been modified.\n"
                                "Do you want to save your changes?"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                        QtGui.QMessageBox.No,
                        QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
            if ret == QtGui.QMessageBox.Yes:
                self.save()
                return True
            elif ret == QtGui.QMessageBox.No:
                return True            
            elif ret == QtGui.QMessageBox.Cancel:
                return False   
        
    def setFileName(self, filename):
        self.fileName = filename
        self.emitFileOpened()
    
    def emitFileName(self):
        '''emit signal fileName, with a filename as string'''
        self.emit(QtCore.SIGNAL("fileName"), str(self.fileName))               
    
    def emitStatus(self):
        self.emit(QtCore.SIGNAL("statusActivated"), str(self.fileName))
    
    def emitFileOpened(self):
        '''emit signal fileOpened, with a filename as string'''
        self.emit(QtCore.SIGNAL("fileOpened"), str(self.fileName))              

    def cutEdit(self, object):
        self.connect(object, QtCore.SIGNAL("triggered()"), object.cut())
            
    def copyEdit(self, object):
        self.connect(object, QtCore.SIGNAL("copyAvailable()"), object.copy())        
        
    def pasteEdit(self, object):
        self.connect(object, QtCore.SIGNAL("triggered()"), object.paste ())
      

    
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    fileaction = FileAction()   
    fileaction.show()
    sys.exit(app.exec_())
