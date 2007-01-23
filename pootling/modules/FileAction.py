#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details.
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on FileAction.

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.modules import World

class FileAction(QtCore.QObject):
    """
    Code for the actions in File menu.
    
    @signal fileSaved(string): emitted when a file is saved. 'string' is the filename as QString.
    @signal fileOpened(string): emitted when a file is opened. 'string' is the filename as QString.
    """

    def __init__(self, parent):
        """ 
        init the class.
        @param parent a QWidget to center the dialogs 
        """
        QtCore.QObject.__init__(self)
        self.parentWidget = parent
        self.fileName = None
        self.fileExtension = ""
        self.fileDescription = ""
        self.MaxRecentHistory = 10
        self.directory = sys.path[0]
        
    def openFile(self):
        #TODO: open one or more existing files selected
        newFileName = QtGui.QFileDialog.getOpenFileName(self.parentWidget, self.tr("Open File"),
                        self.directory,
                        self.tr("All Supported Files (*.po *.pot *.xliff *.xlf);;PO Files (*.po *.pot);;XLIFF Files (*.xliff *.xlf);;All Files (*)"))
        if not newFileName.isEmpty():
            # remember last open file's directory.
            self.directory = os.path.dirname(str(newFileName))
            self.fileName = newFileName
            self.emitFileOpened()
            return True
        else:
            return False

    def save(self):
        self.emitFileSaved(self.fileName)
        
    def saveAs(self):
        # TODO: think about export in different formats
        labelSaveAs = self.tr("Save As")
        labelAllFiles = self.tr("All Files")
        fileDialog = QtGui.QFileDialog(self.parentWidget, labelSaveAs, QtCore.QDir.homePath(), self.fileDescription + " (*" + self.fileExtension + ");;" + labelAllFiles + " (*.*)")

        fileDialog.setHistory(World.settings.value("SaveAsHistory").toStringList())
        fileDialog.setDirectory(QtCore.QDir(World.settings.value("SaveAsDirectory").toString()))
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
                self.emitFileSaved(fileForSave)
                history = fileDialog.history()
                newHistory = QtCore.QStringList()
                while (not history.isEmpty() and newHistory.count() < self.MaxRecentHistory):
                    newHistory.append(history.first())
                    history.removeAll(history.first())
                World.settings.setValue("SaveAsHistory", QtCore.QVariant(newHistory))
                World.settings.setValue("SaveAsDirectory", QtCore.QVariant(fileDialog.directory().path()))
            else:
                QtGui.QMessageBox.information(self.parentWidget, self.tr("Information") , self.tr("Please specify the filename to save to"))
                self.saveAs()
                
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
        if ret == QtGui.QMessageBox.No:
            self.fileName = ""
        self.save()
        return True
         
    def setFileName(self, filename):
        """
        Assign the name of an opened file to a local variable.
        @param filename: file's name as QString
        """
        self.fileName = filename
        self.emitFileOpened()
        # remember last open file's directory.
        self.directory = os.path.dirname(str(filename))
    
    def emitFileSaved(self, filename):
        """emit signal fileSaved when a file is saved
        
        @param filename: file's name as QString
        """
        self.fileName = filename
        self.emit(QtCore.SIGNAL("fileSaved"), str(self.fileName)) 
    
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
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    fileaction = FileAction(None)
    sys.exit(app.exec_())
