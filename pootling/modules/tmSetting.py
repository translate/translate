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
import tempfile
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_tmSetting import Ui_tmsetting
from pootling.modules import World
from pootling.modules import FileDialog
from pootling.modules.pickleTM import pickleTM
from translate.storage import factory
from translate.storage import poheader
from translate.search import match

class globalSetting(QtGui.QDialog):
    """Code for setting path of translation memory dialog."""
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.title = None
        self.section = None
    
    def lazyInit(self):
        if (self.ui):
            # already has ui
            return
            
        self.ui = Ui_tmsetting()
        self.ui.setupUi(self)
        self.setModal(True)
        self.filedialog = FileDialog.fileDialog(self)
        self.setWindowTitle(self.title)
        self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
        self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), self.buildMatcher)
        self.connect(self.ui.btnCancel, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.filedialog.show)
        self.connect(self.ui.btnRemove, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
        self.connect(self.ui.btnRemoveAll, QtCore.SIGNAL("clicked(bool)"), self.ui.listWidget.clear)
        self.ui.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        if (self.section == "TM"):
            self.setToolWhatsThis("Translation Memory")
        elif (self.section == "Glossary"):
            self.setToolWhatsThis("Glossary")
        
        # timer for extend tm
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.extendMatcher)
        
    
    def setToolWhatsThis(self, tool):
        """
        Set what's this for TM or glossary dialog.
        @param tool: whether it is a TM or Glossary as type string.
        """
        list = "<h3>Path for " + tool + "</h3>List of path to scan for " + tool + ". Paths which are checked will be used. "
        self.ui.listWidget.setWhatsThis(self.tr(list))
        dive = "<h3>Dive into subfolders</h3>Check this option, " + tool + " will include subfolders of the above path(s)."
        self.ui.checkBox.setWhatsThis(self.tr(dive))
        sim = "<h3>Minimum similarity</h3>Minimum similarity of source string to be include in " + tool
        self.ui.spinSimilarity.setWhatsThis(self.tr(sim))
        candidate = "<h3>Maximum search result</h3>Number of result that will be shown in the " + tool +" lookup view."
        self.ui.spinMaxCandidate.setWhatsThis(self.tr(candidate))
        self.ui.spinMaxLen.setWhatsThis(self.tr("<h3>Maximum string length</h3>Maximum number of source string to search from."))
        progress = "<h3>Build " + tool + "Process</h3>This bar shows the progression of building a " + tool + " from the above select path(s)."
        self.ui.progressBar.setWhatsThis(self.tr(progress))
    
    def showDialog(self):
        """Make the Translation Memory Setting dialog visible."""
        self.lazyInit()
        self.ui.progressBar.setValue(0)
        
        # get application setting file, and parse it.
        self.loadSettings()
        self.show()
        
    def loadSettings(self):
        """
        Load settings of TM/Glossary
        """
        World.settings.beginGroup(self.section)
        self.ui.listWidget.clear()
        enabledPath = World.settings.value("enabledpath").toStringList()
        disabledPath = World.settings.value("disabledpath").toStringList()
        for path in enabledPath:
            self.addLocation(path)
        for path in disabledPath:
            self.addLocation(path, QtCore.Qt.Unchecked)
        
        includeSub = World.settings.value("diveintosub").toBool()
        minSim = World.settings.value("similarity", QtCore.QVariant(75)).toInt()[0]
        maxCan = World.settings.value("max_candidates", QtCore.QVariant(10)).toInt()[0]
        
        if (self.section == "TM"):
            maxLen = World.settings.value("max_string_len", QtCore.QVariant(70)).toInt()[0]
        elif (self.section == "Glossary"):
            maxLen = World.settings.value(self.section + "/" + "max_string_len", QtCore.QVariant(100)).toInt()[0]
        
        self.ui.checkBox.setChecked(includeSub)
        self.ui.spinSimilarity.setValue(minSim)
        self.ui.spinMaxCandidate.setValue(maxCan)
        self.ui.spinMaxLen.setValue(maxLen)
        
        self.pickleFile = World.settings.value("pickleFile").toString()
        if (not self.pickleFile):
            handle, self.pickleFile = tempfile.mkstemp('','PKL')
        World.settings.endGroup()
    
    def addLocation(self, TMpath, checked = QtCore.Qt.Checked):
        """
        Add TMpath to TM list.
        @param TMpath: Filename as string
        """
        items = self.ui.listWidget.findItems(TMpath, QtCore.Qt.MatchCaseSensitive)
        if (not items):
            item = QtGui.QListWidgetItem(TMpath)
            item.setCheckState(checked and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
            self.ui.listWidget.addItem(item)
    
    def removeLocation(self):
        """
        Remove selected path TM list.
        """
        items = self.ui.listWidget.selectedItems()
        for item in items:
            self.ui.listWidget.setCurrentItem(item)
            self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
    
    def closeEvent(self, event):
        """
        @param event: CloseEvent Object
        """
    
    def buildMatcher(self):
        """
        Collect filename into self.filenames, create matcher, start a
        timer for extend tm, dump matcher, save settings.
        """
        paths = self.getPathList(QtCore.Qt.Checked)
        self.matcher = None
        self.filenames = []
        includeSub = self.ui.checkBox.isChecked()
        for path in paths:
            self.getFiles(path, includeSub)
        
        maxCan = self.ui.spinMaxCandidate.value()
        minSim = self.ui.spinSimilarity.value()
        maxLen = self.ui.spinMaxLen.value()

        disabledPath = self.getPathList(QtCore.Qt.Unchecked)
        World.settings.beginGroup(self.section)
        World.settings.setValue("enabledpath", QtCore.QVariant(paths))
        World.settings.setValue("disabledpath", QtCore.QVariant(disabledPath))
        World.settings.setValue("pickleFile", QtCore.QVariant(self.pickleFile))
        World.settings.setValue("diveintosub", QtCore.QVariant(includeSub))
        World.settings.setValue("similarity", QtCore.QVariant(minSim))
        World.settings.setValue("max_candidates", QtCore.QVariant(maxCan))
        World.settings.setValue("max_string_len", QtCore.QVariant(maxLen))
        World.settings.endGroup()
        if (len(self.filenames) <= 0):
            self.close()
            return
        
        store = self.createStore(self.filenames[0])
        if (self.section == "TM"):
            self.matcher = match.matcher(store, maxCan, minSim, maxLen)
        else:
            self.matcher = match.terminologymatcher(store, maxCan, minSim, maxLen)
        
        # then extendTN start with self.filenames[1]
        self.iterNumber = 1
        self.timer.start(10)
        
    def getFiles(self, path, includeSub): 
        """
        add path to catalog tree view if it's file, if it's directory then
        dive into it and add files.
        """
        path = unicode(path)
        if (os.path.isfile(path)):
            # if file is already existed in the item's child... skip.
            if (path.endswith(".po") or path.endswith(".pot") or path.endswith(".xlf") or path.endswith(".xliff")):
                self.filenames.append(path)
        
        if (os.path.isdir(path)) and (not path.endswith(".svn")):
            for root, dirs, files in os.walk(path):
                for file in files:
                    path = os.path.join(root + os.path.sep + file)
                    self.getFiles(path, includeSub)
                    
                # whether dive into subfolder
                if (includeSub):
                    for folder in dirs:
                        path = os.path.join(root + os.path.sep + folder)
                        self.getFiles(path, includeSub)
                break
    
    def extendMatcher(self):
        """
        extend TM to self.matcher through self.filenames with self.iterNumber as
        iterator.
        @signal matcher: This signal is emitted when the timer finishes the last
        filename in self.filenames
        """
        if (len(self.filenames) <= 1):
            self.timer.stop()
            self.iterNumber = 1
            self.dumpMatcher()
            self.emitMatcher()
            self.close()
            return
        
        # stop the timer for processing the extendMatcher()
        self.timer.stop()
        
        filename = self.filenames[self.iterNumber]
        store = self.createStore(filename)
        self.matcher.extendtm(store.units, store)
        self.iterNumber += 1
        perc = int((float(self.iterNumber) / len(self.filenames)) * 100)
        self.ui.progressBar.setValue(perc)
        
        # resume timer
        self.timer.start(10)
        
        if (self.iterNumber == len(self.filenames)):
            self.timer.stop()
            self.iterNumber = 1
            self.dumpMatcher()
            self.emitMatcher()
            self.close()
    
    def emitMatcher(self):
        """
        emit "matcher" with self.matcher, self.section
        """
        self.emit(QtCore.SIGNAL("matcher"), self.matcher, self.section)
    
    def dumpMatcher(self):
        """
        call pickleTM.dumpMatcher()
        """
        p = pickleTM()
        p.dumpMatcher(self.matcher, self.pickleFile)
    
    def createStore(self, file):
        """
        Create a store object from file.
        add translator, date, and filepath properties to store object.
        
        @param file: as a file path or object
        @return: store as a base object
        """
        try:
            store = factory.getobject(file)
        except:
            store = None
        store.filepath = file
        if (isinstance(store, poheader.poheader)):
            headerDic = store.parseheader()
            store.translator = headerDic.get('Last-Translator') 
            store.date = headerDic.get('PO-Revision-Date') 
            if (store.translator == None):
                store.translator = ""
            if (store.date == None):
                store.date = ""
        else:
            store.translator = ""
            store.date = ""
        return store
    
    def getPathList(self, isChecked):
        """
        Return list of path according to the parameter isChecked or unChecked
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

