#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)
#

from PyQt4 import QtCore, QtGui
import sys, os

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
        (path, fileForSave) = os.path.split(str(self.fileName))
        ##detecting file type
        if (fileForSave.endswith("po")):
            extension = ".po"
            defaultFileType = "Po File (*.po);;"
            otherFileType = "XLIFF Files (*.xliff *.xlf)"
        else:
            extension = ".xlf"
            defaultFileType = "XLIFF Files (*.xliff *.xlf);;"
            otherFileType =  "Po File (*.po)"
        fileType = defaultFileType + otherFileType
        # TODO: set selected Filter to all support Files        
        self.fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),
                                                     QtCore.QDir.currentPath(), self.tr(fileType))
        # TODO: Detect which buttion is clicked (Save or Cancel)
        
        if not self.fileName.isEmpty():
            if not (str(self.fileName).endswith("po") and str(self.fileName).endswith("xlf")):
                self.fileName = self.fileName + extension
                self.emitFileName()      
        else:
            return False
##            QtGui.QMessageBox.information(self,self.tr("Information") ,self.tr("Please specify the filename to save to"))
##            self.saveAs()
        
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
