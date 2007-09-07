#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2006 - 2007 by The WordForge Foundation
# www.wordforge.org
#
# Version 0.1 (29 December 2006)
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
# This module is working on Project of Catatog File.


from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_NewProject import Ui_NewProject
from pootling.modules import FileDialog
import translate.lang.data as data
import pootling.modules.World as World
import os

class newProject(QtGui.QDialog):
    """
    This module implementation with newProject, openProject and openrecentProject
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_NewProject()
        self.ui.setupUi(self)
        self.ui.entryName.setFocus()
        self.ui.btnOK.setEnabled(False)
        self.ui.lblprojecttype.hide()
        self.ui.comboProject.hide()
        self.fileExtension = ".ini"
        
        self.connect(self.ui.btnOK, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.btnCancel, QtCore.SIGNAL("clicked()"), QtCore.SLOT("close()"))
        
        # call dialog box of FileDialog
        self.connect(self.ui.btnBrowse, QtCore.SIGNAL("clicked()"), self.showDirDialog)
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked()"), self.showFileDialog)
        self.connect(self.ui.btnDelete, QtCore.SIGNAL("clicked()"), self.removeLocation)
        self.connect(self.ui.btnClear, QtCore.SIGNAL("clicked()"), self.clearLocation)
        self.connect(self.ui.btnMoveUp, QtCore.SIGNAL("clicked(bool)"), self.moveUp)
        self.connect(self.ui.btnMoveDown, QtCore.SIGNAL("clicked(bool)"), self.moveDown)
        
        # enable/diable ok button
        self.connect(self.ui.entryName, QtCore.SIGNAL("textChanged(QString)"), self.enableOkButton)
        self.connect(self.ui.entryPath, QtCore.SIGNAL("textChanged(QString)"), self.enableOkButton)
        
        # add item to project type
        self.ui.comboProject.addItem(self.tr("KDE"))
        self.ui.comboProject.addItem(self.tr("GNOME"))
        self.ui.comboProject.addItem(self.tr("Other"))
        
        # language code of the country
        language = []
        for langCode, langInfo in data.languages.iteritems():
            language.append(langInfo[0])
            language.sort()
        self.ui.comboLanguage.addItems(language)
        
        self.mode = World.projectNew
    
    def showFileDialog(self):
        """
        Open the file dialog where you can choose both file and directory.
        Add path to Catalog list.
        """
        directory = World.settings.value("workingDir").toString()
        filenames = FileDialog.fileDialog().getExistingPath(
                self,
                directory,
                World.fileFilters)
        if (filenames):
            for filename in filenames:
                self.addLocation(filename)
            directory = os.path.dirname(unicode(filenames[0]))
            World.settings.setValue("workingDir", QtCore.QVariant(directory))
    
    def showDirDialog(self):
        directory = World.settings.value("workingDir").toString()
        filenames = FileDialog.fileDialog().getExistingPath(self, directory, self.tr("Directory"))
        
        if (filenames and len(filenames) >= 1):
            self.ui.entryPath.setText(filenames[0])
            
            directory = os.path.dirname(unicode(filenames[0]))
            World.settings.setValue("workingDir", QtCore.QVariant(directory))
    
    def addLocation(self, text):
        items = self.ui.listLocation.findItems(text, QtCore.Qt.MatchCaseSensitive)
        if (not items):
            item = QtGui.QListWidgetItem(text)
            self.ui.listLocation.addItem(item)
    
    def clearLocation(self):
        """
        Clear all paths from the Catalog List, uncheck checkIncludeSub.
        """
        self.ui.listLocation.clear()
        self.ui.checkIncludeSub.setChecked(False)
    
    def removeLocation(self):
        """
        Remove the selected path from the Catalog list.
        """
        self.ui.listLocation.takeItem(self.ui.listLocation.currentRow())
    
    def moveItem(self, distance):
        """
        move an item up or down depending on distance
        @param distance: int
        """
        currentrow = self.ui.listLocation.currentRow()
        currentItem = self.ui.listLocation.item(currentrow)
        distanceItem = self.ui.listLocation.item(currentrow + distance)
        if (distanceItem):
            temp = distanceItem.text()
            distanceItem.setText(currentItem.text())
            currentItem.setText(temp)
            self.ui.listLocation.setCurrentRow(currentrow + distance)
    
    def moveUp(self):
        """
        move item up
        """
        self.moveItem(-1)
    
    def moveDown(self):
        """
        move item down
        """
        self.moveItem(1)
    
    def accept(self):
        """
        Save project or close dialog according to self.mode.
        """
        
        if (self.mode == World.projectNew):
            filename = self.ui.entryPath.text()
            if (filename):
                self.saveProject(filename)
        
        elif (self.mode == World.projectProperty):
            self.close()
            includeSub = self.ui.checkIncludeSub.isChecked()
            paths = []
            for i in range(self.ui.listLocation.count()):
                paths.append(self.ui.listLocation.item(i).text())
            
            name = self.ui.entryName.text()
            path = self.ui.entryPath.text()
            lang = self.ui.comboLanguage.currentText()
            
            self.emit(QtCore.SIGNAL("NewProperty"), 
                    name,
                    path,
                    lang,
                    paths,
                    includeSub
                    )
    
    def saveProject(self, filename):
        """
        Save  as ini file.
        
        @param filename: file name to save.
        """
        paths = QtCore.QStringList()
        for i in range(self.ui.listLocation.count()):
            paths.append(self.ui.listLocation.item(i).text())
        
        name = self.ui.entryName.text()
        language = self.ui.comboLanguage.currentText()
        includeSub = self.ui.checkIncludeSub.isChecked()
        
        proSettings = QtCore.QSettings(filename, QtCore.QSettings.IniFormat)
        proSettings.setValue("path", QtCore.QVariant(paths))
        proSettings.setValue("name", QtCore.QVariant(name))
        proSettings.setValue("language", QtCore.QVariant(language))
        proSettings.setValue("includeSub", QtCore.QVariant(includeSub))
    
    def openProject(self):
        """
        Open a file dialog for choosing project file as .ini format
        """
        directory = World.settings.value("workingDir").toString()
        
        fileOpen = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                    directory,
                    self.tr("Ini file fomat (*.ini)"))
        if not fileOpen.isEmpty():
            self.emit(QtCore.SIGNAL("openProject"), fileOpen)
            directory = os.path.dirname(unicode(fileOpen))
            World.settings.setValue("workingDir", QtCore.QVariant(directory))
    
    def showProject(self, mode):
        """
        Show project according to mode.
        """
        self.mode = mode
        if (mode == World.projectNew):
            self.setWindowTitle(self.tr("New Project"))
            self.ui.btnOK.setText(self.tr("Save"))
        elif (mode == World.projectProperty):
            self.setWindowTitle(self.tr("Project Properties"))
            self.ui.btnOK.setText(self.tr("OK"))
        self.show()
    
    def setProperty(self, name, path, lang, locations, includeSub):
        """
        Set catalog path and include sub directories flag.
        """
        
        self.ui.entryName.setText(name)
        self.ui.entryPath.setText(path)
        
        langIndex = self.ui.comboLanguage.findText(lang)
        self.ui.comboLanguage.setCurrentIndex(langIndex)
        
        self.clearLocation()
        for location in locations:
            self.addLocation(location)
        
        self.ui.checkIncludeSub.setChecked(includeSub)
        
        self.catalogPath = locations
        self.includeSub = includeSub
    
    def enableOkButton(self):
        """
        Enable or disable ok button.
        """
        name = self.ui.entryName.text()
        filePath = self.ui.entryPath.text()
        if (name and filePath):
            self.ui.btnOK.setEnabled(True)
        else:
            self.ui.btnOK.setEnabled(False)
    
if __name__ == "__main__":
    import os, sys
    import pootling.modules.World as World
    app = QtGui.QApplication(sys.argv)
    Newpro = newProject(None)
    Newpro.showProject(World.projectNew)
    sys.exit(Newpro.exec_())
