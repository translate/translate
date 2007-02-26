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
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.setInterval(2000)
        self.autoRefresh = True

        # set up table appearance and behavior
        self.headerLabels = [self.tr("Name"),
                            self.tr("Fuzzy"),
                            self.tr("Untranslated"),
                            self.tr("Total"),
                            self.tr("CVS/SVN Status"),
                            self.tr("Last Revision"),
                            self.tr("Last Translator")]
        self.ui.treeCatalog.setColumnCount(len(self.headerLabels))
        self.ui.treeCatalog.setHeaderLabels(self.headerLabels)
        self.ui.treeCatalog.header().setResizeMode(QtGui.QHeaderView.Interactive)
        
        # File menu action
        self.connect(self.ui.actionQuit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        
        # Edit menu action
        self.ui.actionReload.setEnabled(True)
        self.connect(self.ui.actionReload, QtCore.SIGNAL("triggered()"), self.refresh)
        
        # Catalog setting's checkboxes action.
        self.catSetting = CatalogSetting(self)
        self.connect(self.ui.actionConfigure, QtCore.SIGNAL("triggered()"), self.catSetting.show)
        self.connect(self.catSetting.ui.chbname, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbfuzzy, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chblastrevision, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbtranslator, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbuntranslated, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbtotal, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)
        self.connect(self.catSetting.ui.chbSVN, QtCore.SIGNAL("stateChanged(int)"), self.toggleHeaderItem)

##        # progress bar
##        self.progressBar = QtGui.QProgressBar()
##        self.progressBar.setEnabled(True)
##        self.progressBar.setProperty("value",QtCore.QVariant(0))
##        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
##        self.progressBar.setObjectName("progressBar")
##        self.progressBar.setVisible(False)
##        self.ui.statusbar.addPermanentWidget(self.progressBar)
##
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

##    def updateProgress(self, value):
##        if (not self.progressBar.isVisible()):
##            self.progressBar.setVisible(True)
##        elif (value == 100):
##            self.progressBar.setVisible(False)
##        self.progressBar.setValue(value)
##        
    def showDialog(self):
        self.lazyInit()
        self.show()
        
        cats = World.settings.value("CatalogPath").toStringList()
        if (cats) and (self.ui.treeCatalog.topLevelItemCount() == 0):
            self.updateCatalog()
        
        return
        
        cats = World.settings.value("CatalogPath").toStringList()
        if (cats) and (self.ui.treeCatalog.rowCount() == 0):
            self.updateCatalog()
    
    def updateCatalog(self):
        """
        Read data from world's "CatalogPath" and display statistic of files
        in tree view.
        """
        self.ui.treeCatalog.clear()
        cats = World.settings.value("CatalogPath").toStringList()
        includeSub = World.settings.value("diveIntoSubCatalog").toBool()
        
        for path in cats:
            path = str(path)
            item = QtGui.QTreeWidgetItem()
            item.setText(0, path)
            if (os.path.isdir(path)):
                if (not path.endswith("/")):
                    path += "/"
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (not root.endswith("/")):
                            root += "/"
                        childState = self.getState(root + file)
                        childItem = QtGui.QTreeWidgetItem()
                        childItem.setText(0, childState[0])
                        childItem.setText(1, childState[1])
                        childItem.setText(2, childState[2])
                        childItem.setText(3, childState[3])
                        childItem.setText(4, childState[4])
                        childItem.setText(5, childState[5])
                        childItem.setText(6, childState[6])
                        item.addChild(childItem)
##                        currentFileNum += 1
##                        self.updateProgress(int((currentFileNum / maxFilesNum) * 100))
                    if (not includeSub):
                        break
            self.ui.treeCatalog.addTopLevelItem(item)
        
    def getState(self, filename):
        """
        return stats as list of text of current file name.
        @param filename: path and file name.
        """
        try:
            store = factory.getobject(filename)
        except:
            return ["", "", "", "", "", "", ""]
        
        name = os.path.basename(filename)
        fuzzyUnitCount = store.fuzzy_units()
        untranslatedUnitCount = store.untranslated_unitcount()
        totalUnitCount = fuzzyUnitCount + untranslatedUnitCount + store.translated_unitcount()
        
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
        
        return [name, str(fuzzyUnitCount), str(untranslatedUnitCount), str(totalUnitCount), cvsSvn, revisionDate, lastTranslator]

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
        
    def emitOpenFile(self, item, col):
        """
        Send "openFile" signal with filename.
        """
        if (not hasattr(item.parent(), "text")):
            return
        
        path = str(item.parent().text(0))
        filename = str(item.text(0))
        
        if (not path.endswith("/")):
            path += "/"
        elif (not path.endswith("\\")):
            path += "\\"
        
        self.emit(QtCore.SIGNAL("openFile"), path + filename)
        

    def refresh(self):
        self.settings = QtCore.QSettings()
        if self.autoRefresh:
            self.refreshTimer.start()
            self.updateCatalog()
        else:
            self.settings.sync()
            self.refreshTimer.stop() 

##if __name__ == "__main__":
##    import sys, os
##    app = QtGui.QApplication(sys.argv)
##    catalog = Catalog(None)
##    catalog.showDialog()
##    sys.exit(catalog.exec_())
