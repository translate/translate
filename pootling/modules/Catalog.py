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
# This module is working on Catalog Manager of translation files

from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_Catalog import Ui_Catalog
from pootling.modules.CatalogSetting import CatalogSetting
from pootling.modules.AboutEditor import AboutEditor
from translate.storage import factory
from Pootle import versioncontrol
import pootling.modules.World as World
from pootling.modules.FindInCatalog import FindInCatalog
import os

class Catalog(QtGui.QMainWindow):
    """
    The Catalog Manager which holds the toolviews.
    """
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = None
    
    def lazyInit(self):
        """
        Initialize only at time of calling Catalog.
        """
        if (self.ui):
            return
        
        self.ui = Ui_Catalog()
        self.ui.setupUi(self)
        self.resize(720,400)

        self.ui.toolBar.toggleViewAction()
        self.ui.toolBar.setWindowTitle("ToolBar View")
        self.ui.toolBar.setStatusTip("Toggle ToolBar View")
    
        # set up table appearance and behavior
        self.headerLabels = [self.tr("Name"),
                            self.tr("Fuzzy"),
                            self.tr("Untranslated"),
                            self.tr("Total"),
                            self.tr("CVS/SVN Status"),
                            self.tr("Last Revision"),
                            self.tr("Last Translator"),
                            self.tr("Translated")]
        self.ui.treeCatalog.setColumnCount(len(self.headerLabels))
        self.ui.treeCatalog.setHeaderLabels(self.headerLabels)
        self.ui.treeCatalog.header().setResizeMode(QtGui.QHeaderView.Interactive)
        self.ui.treeCatalog.setWhatsThis("The catalog manager merges all files and folders enter one treewidget and displays all po, xlf... files. the way you can easily see if a template has been added or removed. Also some information about the files is displayed.")
        
        # File menu action
        self.connect(self.ui.actionQuit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        self.ui.actionQuit.setWhatsThis("<h3>Quit</h3>Quit Catalog")
        
        # Edit menu action
        self.ui.actionReload.setEnabled(True)
        self.connect(self.ui.actionReload, QtCore.SIGNAL("triggered()"), self.refresh)
        self.ui.actionReload.setWhatsThis("<h3>Reload</h3>Set the current files or folders to get the most up-to-date version.")
        
        # Catalog setting's checkboxes action.
        self.catSetting = CatalogSetting(self)
        self.connect(self.ui.actionConfigure, QtCore.SIGNAL("triggered()"), self.catSetting.show)
        self.ui.actionConfigure.setWhatsThis("<h3>Configure...</h3>Set the configuration items with your prefered values.")
        self.connect(self.catSetting.ui.chbname, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbfuzzy, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chblastrevision, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbtranslator, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbuntranslated, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbtotal, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbSVN, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbtranslated, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)

        # Create Find String in Catalog
        self.findBar = FindInCatalog(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.findBar)
        self.findBar.setHidden(True)

        self.connect(self.ui.actionFind_in_Files, QtCore.SIGNAL("triggered()"), self.findBar.showFind)
        self.ui.actionFind_in_Files.setWhatsThis("<h3>Find</h3>You can find string ever you want in Catalog")
        # emit findfiles signal from FindInCatalog file
        self.connect(self.findBar, QtCore.SIGNAL("initSearch"), self.find)

        # progress bar
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.progressBar)

        # Help menu of aboutQt
        self.ui.menuHelp.addSeparator()
        action = QtGui.QWhatsThis.createAction(self)
        self.ui.menuHelp.addAction(action)
        self.aboutDialog = AboutEditor(self)
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog.showDialog)
        self.connect(self.ui.actionAboutQt, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
        
        self.connect(self.catSetting, QtCore.SIGNAL("updateCatalog"), self.updateCatalog)
        self.connect(self.ui.treeCatalog, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.emitOpenFile)
        self.setupCheckbox()

    def find(self, searchString, searchOptions):
            if (not (searchString and searchOptions)):
                return
            for i in range(self.ui.treeCatalog.topLevelItemCount()):
                 item = self.ui.treeCatalog.topLevelItem(i)
                 for j in range(item.childCount()):
                      childItem = item.child(j)
                      filename = self.getFilename(childItem)
                      self.searchInString(searchString, filename, searchOptions)
                      break
                 break

    def searchInString(self, searchString, filename, searchOptions):
        if (not os.path.isfile(filename)):
            return
        store = factory.getobject(filename)
        if (not store):
            return
        unitIndex = 0
        for unit in store.units:
            searchableText = None
            if (searchOptions == World.source):
                searchableText = unit.source
            elif (searchOptions == World.target):
                searchableText = unit.target
            elif (searchOptions == (World.source + World.target)):
                searchableText = unit.source + unit.target
            if (searchableText.find(searchString) != -1 ):
                self.emit(QtCore.SIGNAL("openFile"), filename)
                self.emit(QtCore.SIGNAL("goto"), unitIndex)
                break
            unitIndex += 1

    def toggleHeaderItem(self):
        if (isinstance(self.sender(), QtGui.QCheckBox)):
            text = self.sender().text()
            if text in self.headerLabels:
                if (self.sender().isChecked()):
                    self.ui.treeCatalog.showColumn(self.headerLabels.index(text))
                    World.settings.setValue("Catalog." + text, QtCore.QVariant(True))
                else:
                    self.ui.treeCatalog.hideColumn(self.headerLabels.index(text))
                    World.settings.setValue("Catalog." + text, QtCore.QVariant(False))

    def updateProgress(self, value):
        if (not self.progressBar.isVisible()):
            self.progressBar.setVisible(True)
        elif (value == 100):
            self.progressBar.setVisible(False)
        self.progressBar.setValue(value)
        
    def showDialog(self):
        self.lazyInit()
        self.show()
        
        cats = World.settings.value("CatalogPath").toStringList()
        if (cats) and (self.ui.treeCatalog.topLevelItemCount() == 0):
            self.updateCatalog()
    
    def updateCatalog(self):
        """
        Read data from world's "CatalogPath" and display statistic of files
        in tree view.
        """
        self.ui.treeCatalog.clear()
        cats = World.settings.value("CatalogPath").toStringList()
        includeSub = World.settings.value("diveIntoSubCatalog").toBool()
        
        # TODO: calculate number of maximum files in directory.
        maxFilesNum = 0.1       # avoid devision by zero.
        currentFileNum = 0.0
        
        for catalogFile in cats:
            catalogFile = str(catalogFile)
            
            topItem = QtGui.QTreeWidgetItem()
            self.addCatalogFile(catalogFile, includeSub, topItem)
            self.ui.treeCatalog.addTopLevelItem(topItem)
            self.ui.treeCatalog.expandItem(topItem)
        
        self.ui.treeCatalog.resizeColumnToContents(0)
            #currentFileNum += 1
            #self.updateProgress(int((currentFileNum / maxFilesNum) * 100))
    
    def addCatalogFile(self, path, includeSub, item):
        """
        add path to catalog tree view if it's file, if it's directory then
        dive into it and add files.
        """
        
        if (os.path.isfile(path)):
            if (not item.text(0)):
                item.setText(0, os.path.dirname(path))
            childStats = self.getStats(path)
            item1 = QtGui.QTreeWidgetItem(item)
            item1.setText(0, childStats[0])
            item1.setText(1, childStats[1])
            item1.setText(2, childStats[2])
            item1.setText(3, childStats[3])
            item1.setText(4, childStats[4])
            item1.setText(5, childStats[5])
            item1.setText(6, childStats[6])
            item1.setText(7, childStats[7])

        if (os.path.isdir(path)):
            if (not item.parent()):
                pathName = path
            else:
                pathName = os.path.basename(path)
            item.setText(0, pathName)
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    path = os.path.join(root + '/' + file)
                    self.addCatalogFile(path, includeSub, item)
                    
                # whether dive into subfolder
                if (includeSub):
                    for folder in dirs:
                        path = os.path.join(root + '/' + folder)
                        subItem = QtGui.QTreeWidgetItem(item)
                        self.addCatalogFile(path, includeSub, subItem)
                
                break
    
    def getStats(self, filename):
        """
        return stats as list of text of current file name.
        @param filename: path and file name.
        """
        try:
            store = factory.getobject(filename)
        except:
            return ["", "", "", "", "", "", "",""]
        
        name = os.path.basename(filename)
        fuzzyUnitCount = store.fuzzy_units()
        translated = store.translated_unitcount()
        untranslatedUnitCount = store.untranslated_unitcount()
        totalUnitCount = fuzzyUnitCount + untranslatedUnitCount + translated
        
        cvsSvn = "?"
        
        if hasattr(store, "parseheader"):
            headerDic = store.parseheader()
            try:
                revisionDate = str(headerDic["PO-Revision-Date"])
            except:
                pass
            try:
                lastTranslator = str(headerDic["Last-Translator"])
            except:
                pass
        else:
            revisionDate = ""
            lastTranslator = ""
        
        return [name, str(fuzzyUnitCount), str(untranslatedUnitCount), str(totalUnitCount), cvsSvn, revisionDate, lastTranslator, str(translated)]

    def setupCheckbox(self):
        if not (World.settings.value("Catalog.Name").toBool()):
            self.catSetting.ui.chbname.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbname.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Fuzzy").toBool()):
            self.catSetting.ui.chbfuzzy.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbfuzzy.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Untranslated").toBool()):
            self.catSetting.ui.chbuntranslated.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbuntranslated.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Total").toBool()):
            self.catSetting.ui.chbtotal.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbtotal.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.CVS/SVN Status").toBool()):
            self.catSetting.ui.chbSVN.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbSVN.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Last Revision").toBool()):
            self.catSetting.ui.chblastrevision.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chblastrevision.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Last Translator").toBool()):
            self.catSetting.ui.chbtranslator.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbtranslator.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Translated").toBool()):
            self.catSetting.ui.chbtranslated.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.catSetting.ui.chbtranslated.setCheckState(QtCore.Qt.Checked)

    def emitOpenFile(self, item, col):
        """
        Send "openFile" signal with filename.
        """
        filename = self.getFilename(item)
        if (os.path.isfile(filename)): 
            self.emit(QtCore.SIGNAL("openFile"), filename)
    
    def getFilename(self, item):
        """
        return filename join from item.text(0) to its parent.
        """
        filename = str(item.text(0))
        if (item.parent()):
            filename = os.path.join(self.getFilename(item.parent()) + '/' + filename)
        return filename
    
    def refresh(self):
        self.settings = QtCore.QSettings()
        if self.autoRefresh:
            self.updateCatalog()
        else:
            self.settings.sync()


##if __name__ == "__main__":
##    import sys, os
##    app = QtGui.QApplication(sys.argv)
##    catalog = Catalog(None)
##    catalog.showDialog()
##    sys.exit(catalog.exec_())
