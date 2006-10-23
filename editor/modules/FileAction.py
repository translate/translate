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
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#

from PyQt4 import QtCore, QtGui
import sys, os

class FileAction(QtCore.QObject):
    def __init__(self, parent):
        """ parent: a QWidget to center the dialogs """
        QtCore.QObject.__init__(self)
        self.parentWidget = parent
        self.fileName = None
        self.fileExtension = ""
        self.fileDescription = ""        
        self.MaxRecentHistory = 10
        self.settings = QtCore.QSettings("WordForge", "Translation Editor")
        
    def openFile(self):    
        #TODO: open one or more existing files selected
        self.fileName = QtGui.QFileDialog.getOpenFileName(self.parentWidget, self.tr("Open File"),
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
            self.emitFileName(self.fileName)            

    def saveAs(self):      
        # TODO: think about export in different formats
        labelSaveAs = self.tr("Save As")
        labelAllFiles = self.tr("All Files")       
        fileDialog = QtGui.QFileDialog(self.parentWidget, labelSaveAs, QtCore.QDir.homePath(), self.fileDescription + " (*" + self.fileExtension + ");;" + labelAllFiles + " (*.*)")

        fileDialog.setHistory(self.settings.value("SaveAsHistory").toStringList())
        fileDialog.setDirectory(QtCore.QDir(self.settings.value("SaveAsDirectory").toString()))       
                
        fileDialog.setLabelText ( QtGui.QFileDialog.Accept, labelSaveAs)
        fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        fileDialog.setConfirmOverwrite(True)
        
        # perform save as only when there is filename        
        if (fileDialog.exec_()):
            files = fileDialog.selectedFiles()
            if (not files.isEmpty()):
                fileForSave = files.first()
                if (not fileForSave.endsWith(self.fileExtension,  QtCore.Qt.CaseInsensitive)):
                    # add extension according to existing open file
                    fileForSave.append(self.fileExtension)
                self.emitFileName(fileForSave)
                history = fileDialog.history()
                newHistory = QtCore.QStringList()
                while (not history.isEmpty() and newHistory.count() < self.MaxRecentHistory):       
                    print history.first()
                    newHistory.append(history.first())
                    history.removeAll(history.first())                    
                self.settings.setValue("SaveAsHistory", QtCore.QVariant(newHistory))
                self.settings.setValue("SaveAsDirectory", QtCore.QVariant(fileDialog.directory().path()))
            # FIXME add a return value here. Jens
            else:
                QtGui.QMessageBox.information(self.parentWidget, self.tr("Information") , self.tr("Please specify the filename to save to"))
                self.saveAs()
        
        
##

    def aboutToClose(self, main):
        """Action before closing the program when file has modified"""
        ret = QtGui.QMessageBox.question(main, self.tr("File Modified"),
                    self.tr("The file has been modified.\n"
                            "Do you want to save your changes?"),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
        if ret == QtGui.QMessageBox.Cancel:
            return False   
        if ret == QtGui.QMessageBox.Yes:
            self.save()
        return True
         
    def setFileName(self, filename):
        """ open a new file """
        self.fileName = filename
        self.emitFileOpened()
    
    def emitFileName(self, file):
        """emit signal fileName, with file as string"""
        self.fileName = file
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
