#!/usr/bin/python
# -*- coding: utf-8 -*-
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
        self.filename = None
        self.fileExtension = ""
        self.fileDescription = ""
        self.MaxRecentHistory = 10
        
        self.directory = World.settings.value("workingDir").toString()
        if (not self.directory) or (not os.path.exists(self.directory)):
            self.directory = QtCore.QDir.homePath()
        
    def openFile(self):
        """
        Open an OpenFile dialog.
        @return: Returns True if ok button is click.
        """
        #TODO: open one or more existing files selected
        newFileName = QtGui.QFileDialog.getOpenFileName(self.parentWidget, self.tr("Open File"),
                        self.directory,
                        self.tr("All Supported Files (*.po *.pot *.xliff *.xlf *.tmx *.tbx);;PO Files and PO Template Files (*.po *.pot);;XLIFF Files (*.xliff *.xlf);;Translation Memory eXchange (TMX) Files (*.tmx);;TermBase eXchange (TBX) Files (*.tbx);;All Files (*)"))
        if not newFileName.isEmpty():
            # remember last open file's directory.
            self.directory = os.path.dirname(str(newFileName))
            self.filename = newFileName
            self.emitFileOpened()
            return True
        else:
            return False

    def save(self):
        self.emitFileToSave(self.filename)
        
    def saveAs(self):
        """
        Open an SaveAs File dialog.
        """
        # TODO: think about export in different formats
        labelSaveAs = self.tr("Save As")
        self.fileExtension = self.fileExtension
        fileDialog = QtGui.QFileDialog(self.parentWidget, labelSaveAs, self.directory, self.fileDescription + " (*" + str(self.fileExtension) + ")" )

        fileDialog.setHistory(World.settings.value("SaveAsHistory").toStringList())
        fileDialog.setDirectory(self.directory)
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
                self.filename = fileForSave
                self.emitFileToSave(self.filename)
                
                history = fileDialog.history()
                newHistory = QtCore.QStringList()
                while (not history.isEmpty() and newHistory.count() < self.MaxRecentHistory):
                    newHistory.append(history.first())
                    history.removeAll(history.first())
                World.settings.setValue("SaveAsHistory", QtCore.QVariant(newHistory))
                
            else:
                QtGui.QMessageBox.information(self.parentWidget, self.tr("Information") , self.tr("Please specify the filename to save to"))
                self.saveAs()
                
    def clearedModified(self, parent):
        """
        Return bool indicates it has cleared the content modified.
        """
        ret = QtGui.QMessageBox.question(parent, self.tr("File Modified"),
                    self.tr("The file has been modified.\n"
                            "Do you want to save your changes?"),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
        
        if (ret == QtGui.QMessageBox.Yes):
            self.save()
            return True
        elif (ret == QtGui.QMessageBox.No):
            # reset file name
            self.filename = ""
            return True
        elif (ret == QtGui.QMessageBox.Cancel):
            return False
    
    def setFileName(self, filename):
        """
        Assign the name of an opened file to a local variable.
        @param filename: file's name as QString
        """
        self.filename = filename
        # remember last open file's directory.
        self.directory = os.path.dirname(unicode(filename))
        World.settings.setValue("workingDir", QtCore.QVariant(self.directory))
    
    def emitFileToSave(self, filename):
        """
        Send "fileToSave" signal with a file name.
        @param filename: file's name as QString.
        """
        self.emit(QtCore.SIGNAL("fileToSave"), unicode(filename)) 
        
    def emitFileOpened(self):
        """emit signal fileOpened, with a filename as string"""
        # get default file extension and description
        (path, filename) = os.path.split(str(self.filename).lower())
        extension = {"po": "PO Files", "pot": "PO Template Files", 
            "xliff": "XLIFF Files", "xlf": "XLIFF Files", 
            "tmx": "Translation Memory eXchange (TMX) Files", "tbx": "TermBase eXchange (TBX) Files"}
        filename, ext = os.path.splitext(filename)
        ext = ext[len(os.path.extsep):].lower()
        self.fileExtension = "." + ext
        self.fileDescription = extension.get(ext) 
        self.emit(QtCore.SIGNAL("fileOpened"), str(self.filename))
    
if __name__ == "__main__":
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    fileaction = FileAction(None)
    sys.exit(app.exec_())
