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
        
    def openFile(self):    
        #TODO: open one or more existing files selected
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                        QtCore.QDir.currentPath(),
                        self.tr("Supported Files (*.po *.pot *.xliff *.xlf)"))
                        #self.tr("Po File (*.po);; XLIFF Files (*.xliff *.xlf);;Po Templet (*.pot)"))
        if not self.fileName.isEmpty():
            self.emitFileOpened()
            return True
        else:
            return False

    def save(self):        
        if not self.fileName.isEmpty():
            self.emitFileName()

    def fileType(self):
        (path, openedFile) = os.path.split(str(self.fileName))
        ##detecting file type
        # FIXME that does not work if my file ends with po but not with .po! Jens
        if (self.fileForSave.endswith("po")):
            extension = ".po"
            defaultFileType = "Po File (*.po);;"
            otherFileType = "XLIFF Files (*.xliff *.xlf);;Po TempleFile (*.pot)"
        elif (self.openedFile.endswith("pot")):
            self.extension = ".pot"
            defaultFileType = "Po TempleFile (*.pot);;"
            otherFileType = "XLIFF Files (*.xliff *.xlf);;Po File (*.po)"
        else:
            self.extension = ".xlf"
            defaultFileType = "XLIFF Files (*.xliff *.xlf);;"
            otherFileType =  "Po File (*.po);;XLIFF Files (*.xliff *.xlf)"
        return defaultFileType + otherFileType
            
    def saveAs(self):      
        # TODO: set selected Filter to all support Files        
        # FIXME how shall self.tr(fileType) work here? You can not translate what you only
        # know at runtime! You must use the tr() in the lines above! Jens
        #self.fileForSave = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"), QtCore.QDir.currentPath(), self.tr(self.fileType()))
        self.fileForSave = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"), QtCore.QDir.currentPath(), self.tr("Supported Files (*.*)"))
        
        # TODO: Detect which buttion is clicked (Save or Cancel)
        #save botton clicked
        if isinstance(self.fileForSave, QtCore.QString):
            print str(self.fileForSave)
            if str(self.fileForSave) != " ":
                print "non blank"
                print self.fileName
                (path, saveFile) = os.path.split(str(self.fileForSave))
                ##detecting extension
                # FIXME that does not work if my file ends with po or xlf but not with .po or .xlf! Jens
                # You allow *.xliff in the filter but you do not test here for it! Jens
                if not (saveFile.endswith("po") or saveFile.endswith("xlf")):
                    #adding extension auto according to existing open file
                    print "something"
                    self.fileForSave = str(self.fileForSave) + str(self.extension)
                print self.fileForSave
                self.fileName = self.fileForSave
                self.emitFileName()
            # FIXME add a return value here. Jens
            else:
                print "blank"
##                QtGui.QMessageBox.information(self,self.tr("Information") ,self.tr("Please specify the filename to save to"))
##                self.saveAs()
        #close buttion clicked
        else:
            print "cancel"
            return                      
            
    # FIXME the name is wrong, you are about to close not about to save. Jens
    def aboutToSave(self, main):
      # FIXME indentation! Jens    ---done         
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
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    fileaction = FileAction()   
    fileaction.show()
    sys.exit(app.exec_())
