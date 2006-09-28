#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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
        self.fileExtension = ""
        self.fileDescription = ""
        
    def openFile(self):    
        #TODO: open one or more existing files selected
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                        QtCore.QDir.currentPath(),
                        self.tr("Supported Files (*.po *.pot *.xliff *.xlf);;All Files(*.*)"))
                        #self.tr("Po Files (*.po);; XLIFF Files (*.xliff *.xlf);;Po Templates (*.pot)"))

        if not self.fileName.isEmpty():
            self.emitFileOpened()
            return True
        else:
            return False

    def save(self):        
        if not self.fileName.isEmpty():
            self.emitFileName()

    def saveAs(self):      
        # TODO: set selected Filter to all support Files
        labelSaveAs = self.tr("Save As")
        labelAllFiles = self.tr("All Files")
        self.fileForSave = QtGui.QFileDialog.getSaveFileName(self,
            labelSaveAs, QtCore.QDir.currentPath(), 
            self.fileDescription + " (*" + self.fileExtension + ");;" + labelAllFiles + " (*.*)")
        
        # perform save as only when there is filename
        if not self.fileForSave.isNull():
            (path, saveFile) = os.path.split(str(self.fileForSave))
            if not (saveFile.endswith(self.fileExtension)):
                # add extension according to existing open file
                self.fileForSave = str(self.fileForSave) + self.fileExtension
                self.fileName = self.fileForSave
            self.emitFileName()

    def aboutToClose(self, main):
        """Action before closing the program when file has modified"""
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
        """emit signal fileName, with a filename as string"""
        self.emit(QtCore.SIGNAL("fileName"), str(self.fileName))               
    
    def emitStatus(self):
        self.emit(QtCore.SIGNAL("statusActivated"), str(self.fileName))
    
    def emitFileOpened(self):
        """emit signal fileOpened, with a filename as string"""
        # get default file extension and description
        (path, fileName) = os.path.split(str(self.fileName).lower())
        if (fileName.endswith(".po")):
            self.fileExtension = ".po"
            self.fileDescription = "Po Files"
        elif (fileName.endswith(".pot")):
            self.fileExtension = ".pot"
            self.fileDescription = "Po TemplateFiles"
        elif (fileName.endswith(".xlf")):
            self.fileExtension = ".xlf"
            self.fileDescription = "XLIFF Files"
        self.emit(QtCore.SIGNAL("fileOpened"), str(self.fileName))
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    fileaction = FileAction()   
    fileaction.show()
    sys.exit(app.exec_())
