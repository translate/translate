#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
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
# This module is providing an setting path of translation memory dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_tmSetting import Ui_tmsetting
from pootling.modules import World
from pootling.modules import FileDialog
from pootling.modules.pickleTM import pickleTM

class tmSetting(QtGui.QDialog):
    """Code for setting path of translation memory dialog."""
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.subscan = None
        self.tempoRemember = {}
        
    def showDialog(self):
        """Make the Translation Memory Setting dialog visible."""
        #lazy init
        if (not self.ui):
            self.ui = Ui_tmsetting()
            self.ui.setupUi(self)
            self.setWindowTitle("Configure Translation Memory")
            self.setModal(True)
            self.filedialog = FileDialog.fileDialog(self)
            
            self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
            self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.filedialog.show)
            self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), self.createTM)
            self.connect(self.ui.btnCancel, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
            self.connect(self.ui.btnRemove, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
            self.connect(self.ui.btnRemoveAll, QtCore.SIGNAL("clicked(bool)"), self.ui.listWidget.clear)
            self.connect(self.ui.btnEnable, QtCore.SIGNAL("clicked(bool)"), self.setChecked)
            self.connect(self.ui.btnDisable, QtCore.SIGNAL("clicked(bool)"), self.setUnchecked)
            self.ui.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.loadItemToList()
        self.ui.checkBox.setChecked(World.settings.value("diveIntoSub").toBool())
        self.tempoRemember["diveIntoSub"] = self.ui.checkBox.isChecked()
        self.ui.progressBar.setValue(0)
        self.show()
        #TODO: It should be a way to use relative path for platform independent.
        confFile = str(QtCore.QDir.homePath()) + '/.config/WordForge/Pootling.conf'
        self.pickleTMObj = pickleTM(confFile)
    
    def loadItemToList(self):
        """Load remembered item to list."""
        self.ui.listWidget.clear()
        enabledTM = World.settings.value("enabledTM").toStringList()
        disableTM = World.settings.value("disabledTM").toStringList()
        for path in enabledTM:
            self.addLocation(path)
        for path in disableTM:
            self.addLocation(path, QtCore.Qt.Unchecked)
        
        self.ui.spinSimilarity.setValue(World.settings.value("Similarity", QtCore.QVariant(75)).toInt()[0])
        self.ui.spinMaxCandidate.setValue(World.settings.value("Max_Candidates", QtCore.QVariant(10)).toInt()[0])
        self.ui.spinMaxLen.setValue(World.settings.value("Max_String_len", QtCore.QVariant(70)).toInt()[0])
        self.tempoRemember["enabledTM"] = enabledTM
        self.tempoRemember["disabledTM"] = disableTM
        self.tempoRemember["Similarity"] = self.ui.spinSimilarity.value()
        self.tempoRemember["Max_Candidates"] = self.ui.spinMaxCandidate.value()
        self.tempoRemember["Max_String_len"] = self.ui.spinMaxLen.value()
    
    def addLocation(self, TMpath, checked = QtCore.Qt.Checked):
        """Add TMpath to TM list.
        
        @param TMpath: Filename as string
        
        """
        items = self.ui.listWidget.findItems(TMpath, QtCore.Qt.MatchCaseSensitive)
        if (not items):
            item = QtGui.QListWidgetItem(TMpath)
            item.setCheckState(checked and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
            self.ui.listWidget.addItem(item)
    
    def removeLocation(self):
        """Remove selected path TM list."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            self.ui.listWidget.setCurrentItem(item)
            self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
    
    def closeEvent(self, event):
        """Rememer TMpath before closing.
        
        @param event: CloseEvent Object
        
        """
        
        World.settings.setValue("enabledTM", QtCore.QVariant(self.tempoRemember["enabledTM"]))
        World.settings.setValue("disabledTM", QtCore.QVariant(self.tempoRemember["disabledTM"]))
        World.settings.setValue("diveIntoSub", QtCore.QVariant(self.tempoRemember["diveIntoSub"]))
        World.settings.setValue("Similarity", QtCore.QVariant(self.tempoRemember["Similarity"]))
        World.settings.setValue("Max_Candidates", QtCore.QVariant(self.tempoRemember["Max_Candidates"]))
        World.settings.setValue("Max_String_len", QtCore.QVariant(self.tempoRemember["Max_String_len"]))
        QtGui.QDialog.closeEvent(self, event)
        
    def createTM(self):
        """Build base object of checked files in lists.
        
        @signal matcher: This signal is emitted when there is matcher
        
        """
        checkedItemList = self.getPathList(QtCore.Qt.Checked)
        matcher = None
        if (not checkedItemList):
            self.pickleTMObj.removeFile()
            QtGui.QMessageBox.critical(None, 'No translated file path specified', 'No translated file for building Translation Memory.')
        else:
            try:
                matcher = self.pickleTMObj.buildMatcher(checkedItemList, self.ui.spinMaxCandidate.value(), self.ui.spinSimilarity.value(),  self.ui.spinMaxLen.value())
            except Exception, e:
                self.pickleTMObj.removeFile()
                QtGui.QMessageBox.critical(None, 'Error', str(e))
        
        self.emit(QtCore.SIGNAL("matcher"), matcher)
        
        self.tempoRemember["enabledTM"] = self.getPathList(QtCore.Qt.Checked)
        self.tempoRemember["disabledTM"] = self.getPathList(QtCore.Qt.Unchecked)
        self.tempoRemember["diveIntoSub"] = self.ui.checkBox.isChecked()
        self.tempoRemember["Similarity"] = self.ui.spinSimilarity.value()
        self.tempoRemember["Max_Candidates"] = self.ui.spinMaxCandidate.value()
        self.tempoRemember["Max_String_len"] = self.ui.spinMaxLen.value()
        self.close()
        
    def setChecked(self):
        """Set state of selectedItems as checked."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Checked)

    def setUnchecked(self):
        """Set state of selectedItems as unchecked."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Unchecked)
    
    def getPathList(self, isChecked):
        """Return list of path according to the parameter isChecked or unChecked
        
        @return: itemList as list of unchecked or checked path
        """
        itemList = QtCore.QStringList()
        count = self.ui.listWidget.count()
        for i in range(count):
            item = self.ui.listWidget.item(i)
            if (not (item.checkState() ^ isChecked)):
                itemList.append(item.text())
        return itemList
    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = tmSetting(None)
    tm.showDialog()
    sys.exit(tm.exec_())

