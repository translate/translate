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
#from ConfigParser import *

class globalSetting(QtGui.QDialog):
    """Code for setting path of translation memory dialog."""
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.subscan = None
        self.title = None
        self.section = None
        self.tempoRemember = {}
        
    def showDialog(self):
        """Make the Translation Memory Setting dialog visible."""
        #lazy init
        if (not self.ui):
            self.ui = Ui_tmsetting()
            self.ui.setupUi(self)
            self.setModal(True)
            self.filedialog = FileDialog.fileDialog(self)
            self.setWindowTitle(self.title)
            self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
            self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), self.createTM)
            self.connect(self.ui.btnCancel, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
            self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.filedialog.show)
            self.connect(self.ui.btnRemove, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
            self.connect(self.ui.btnRemoveAll, QtCore.SIGNAL("clicked(bool)"), self.ui.listWidget.clear)
            self.ui.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        # get application setting file, and parse it.
        filename = World.settings.fileName()
        self.loadItemToList()
        self.show()
        
        # create pickleMatcher objectr
        self.pickleTM = pickleTM(str(filename), self.section)
    
    def loadItemToList(self):
        """Load remembered item to list."""
        self.ui.listWidget.clear()
        World.settings.beginGroup(self.section)
        enabledPath = World.settings.value("enabledpath").toStringList()
        disabledPath = World.settings.value("disabledpath").toStringList()
        for path in enabledPath:
            self.addLocation(path)
        for path in disabledPath:
            self.addLocation(path, QtCore.Qt.Unchecked)
        
        self.ui.checkBox.setChecked(World.settings.value("diveintosub").toBool())
        self.ui.spinSimilarity.setValue(World.settings.value("similarity", QtCore.QVariant(75)).toInt()[0])
        self.ui.spinMaxCandidate.setValue(World.settings.value("max_candidates", QtCore.QVariant(10)).toInt()[0])
        
        if (self.section == "TM"):
            self.ui.spinMaxLen.setValue(World.settings.value("max_string_len", QtCore.QVariant(70)).toInt()[0])
        elif (self.section == "Glossary"):
            self.ui.spinMaxLen.setMaximum(500)
            self.ui.spinMaxLen.setValue(World.settings.value(self.section + "/" + "max_string_len", QtCore.QVariant(500)).toInt()[0])
        
        # temporary remember in order to clear changing when clicking cancel button
        self.tempoRemember["enabledpath"] = enabledPath
        self.tempoRemember["disabledpath"] = disabledPath
        self.tempoRemember["diveintosub"] = self.ui.checkBox.isChecked()
        self.tempoRemember["similarity"] = self.ui.spinSimilarity.value()
        self.tempoRemember["max_candidates"] = self.ui.spinMaxCandidate.value()
        self.tempoRemember["max_string_len"] = self.ui.spinMaxLen.value()
        World.settings.endGroup()
    
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
        
        World.settings.beginGroup(self.section);
        World.settings.setValue("enabledpath", QtCore.QVariant(self.tempoRemember["enabledpath"]))
        World.settings.setValue("disabledpath", QtCore.QVariant(self.tempoRemember["disabledpath"]))
        World.settings.setValue("diveintosub", QtCore.QVariant(self.tempoRemember["diveintosub"]))
        World.settings.setValue("similarity", QtCore.QVariant(self.tempoRemember["similarity"]))
        World.settings.setValue( "max_candidates", QtCore.QVariant(self.tempoRemember["max_candidates"]))
        World.settings.setValue("max_string_len", QtCore.QVariant(self.tempoRemember["max_string_len"]))
        World.settings.endGroup();
        QtGui.QDialog.closeEvent(self, event)
        
    def createTM(self):
        """Build base object of checked files in lists.
        
        @signal matcher: This signal is emitted when there is matcher
        
        """
        checkedItemList = self.getPathList(QtCore.Qt.Checked)
        matcher = None
        if (not checkedItemList):
            self.pickleTM.removeFile()
            QtGui.QMessageBox.critical(None, 'No file specified', 'No file specified for building TM or glossary')
        else:
            try:
                #FIXME: do not hard code.
                if (self.section == "TM"):
                    matcher = self.pickleTM.buildTMMatcher(checkedItemList, self.ui.spinMaxCandidate.value(), self.ui.spinSimilarity.value(),  self.ui.spinMaxLen.value())
                elif (self.section == "Glossary"):
                    matcher = self.pickleTM.buildTermMatcher(checkedItemList, self.ui.spinMaxCandidate.value(), self.ui.spinSimilarity.value(),  self.ui.spinMaxLen.value())
            except Exception, e:
                self.pickleTM.removeFile()
                QtGui.QMessageBox.critical(None, 'Error', str(e))
        
        self.emit(QtCore.SIGNAL("matcher"), matcher)
        
        self.tempoRemember["enabledpath"] = self.getPathList(QtCore.Qt.Checked)
        self.tempoRemember["disabledpath"] = self.getPathList(QtCore.Qt.Unchecked)
        self.tempoRemember["diveintosub"] = self.ui.checkBox.isChecked()
        self.tempoRemember["similarity"] = self.ui.spinSimilarity.value()
        self.tempoRemember["max_candidates"] = self.ui.spinMaxCandidate.value()
        self.tempoRemember["max_string_len"] = self.ui.spinMaxLen.value()
        self.close()
    
    def getPathList(self, isChecked):
        """Return list of path according to the parameter isChecked or unChecked
        
        @return: itemList as list of unchecked or checked path
        """
        itemList = QtCore.QStringList()
        count = self.ui.listWidget.count()
        for i in range(count):
            item = self.ui.listWidget.item(i)
            if (not (item.checkState() ^ isChecked)):
                itemList.append(str(item.text()))
        return itemList

class tmSetting(globalSetting):
    def __init__(self, parent):
        globalSetting.__init__(self, parent)
        self.title = "Configure translation memory"
        self.section = "TM"

class glossarySetting(globalSetting):
    def __init__(self, parent):
        globalSetting.__init__(self, parent)
        self.title = "Configure glossary"
        self.section = "Glossary"

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = tmSetting(None)
    tm.showDialog()
    sys.exit(tm.exec_())

