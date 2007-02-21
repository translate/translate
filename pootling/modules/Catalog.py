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
##from pootling.modules.Operator import Operator
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
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.setInterval(2000)
        self.ui = Ui_Catalog()
        self.ui.setupUi(self)
        self.resize(720,400)
        
        # set up table appearance and behavior
        self.headerLabels = [self.tr("Name"), self.tr("Fuzzy"), self.tr("Untranslated"), self.tr("Total"), self.tr("CVS/SVN Status"), self.tr("Last Revision"), self.tr("Last Translator")]
        self.ui.tableCatalog.setColumnCount(len(self.headerLabels))
        self.ui.tableCatalog.setRowCount(0)
        self.ui.tableCatalog.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableCatalog.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableCatalog.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.tableCatalog.horizontalHeader().setSortIndicatorShown(True)
        self.ui.tableCatalog.horizontalHeader().setHighlightSections(False)
        self.ui.tableCatalog.verticalHeader().hide()

        # File menu action
        self.connect(self.ui.actionQuit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))

        # Project menu action
        self.Catalog = CatalogSetting(self)
        self.connect(self.ui.actionConfigure, QtCore.SIGNAL("triggered()"), self.Catalog.show)
        self.connect(self.Catalog.ui.chbname, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chbfuzzy, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chblastrevision, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chbtranslator, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chbuntranslated, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chbtotal, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)
        self.connect(self.Catalog.ui.chbSVN, QtCore.SIGNAL("stateChanged(int)"), self.setHeaderLabel)

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
        
        self.connect(self.Catalog, QtCore.SIGNAL("updateCatalog"), self.updateCatalog)
        
        self.setupCheckbox()

    def setHeaderLabel(self):
        if (isinstance(self.sender(), QtGui.QCheckBox)):
            text = self.sender().text()
            if text in self.headerLabels:
                if (self.sender().isChecked()):
                    self.ui.tableCatalog.showColumn(self.headerLabels.index(text))
                    World.settings.setValue("Catalog." + text, QtCore.QVariant(True))
                else:
                    self.ui.tableCatalog.hideColumn(self.headerLabels.index(text))
                    World.settings.setValue("Catalog." + text, QtCore.QVariant(False))
                    
##            World.settings.setValue("rememberHeader", QtCore.QVariant(self.headerLabels))

    def updateProgress(self, value):
        if (not self.progressBar.isVisible()):
            self.progressBar.setVisible(True)
        elif (value == 100):
            self.progressBar.setVisible(False)
        self.progressBar.setValue(value)
        
    def showDialog(self):
        self.show()
        cats = World.settings.value("CatalogPath").toStringList()
        if (cats) and (self.ui.tableCatalog.rowCount() == 0):
            self.updateCatalog()
    
    def updateCatalog(self):
        self.ui.tableCatalog.clear()
        self.ui.tableCatalog.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableCatalog.setRowCount(0)
        self.ui.tableCatalog.setSortingEnabled(False)
        
        cats = World.settings.value("CatalogPath").toStringList()
        includeSub = World.settings.value("diveIntoSubCatalog").toBool()
        
        maxFilesNum = 0.0
        for path in cats:
            path = str(path)
            if (os.path.isdir(path)):
                if (not path.endswith("/")):
                    path = path + "/"
                for root, dirs, files in os.walk(path):
                    for file in files:
                        maxFilesNum += 1
                    if (not includeSub):
                        break
        
        currentFileNum = 0.0
        for path in cats:
            path = str(path)
            if (os.path.isdir(path)):
                if (not path.endswith("/")):
                    path = path + "/"
                for root, dirs, files in os.walk(path):
                    for file in files:
                        self.addUnit(root + file)
                        currentFileNum += 1
                        self.updateProgress(int((currentFileNum / maxFilesNum) * 100))
                    if (not includeSub):
                        break
        self.ui.tableCatalog.setSortingEnabled(False)
    
    def addUnit(self, filename):
        """
        add the unit to table.
        @param filename: path and file name.
        """
##        try:
##            print versioncontrol.getcleanfile(filename)
##        except:
##            pass
##        
        try:
            store = factory.getobject(filename)
        except:
            return
        row = self.ui.tableCatalog.rowCount()
        self.ui.tableCatalog.setRowCount(row + 1)
        
        item = QtGui.QTableWidgetItem(filename)
        self.ui.tableCatalog.setItem(row, 0, item)
        item = QtGui.QTableWidgetItem(str(store.fuzzy_units()))
        self.ui.tableCatalog.setItem(row, 1, item)
        item = QtGui.QTableWidgetItem(str(store.untranslated_unitcount()))
        self.ui.tableCatalog.setItem(row, 2, item)
        totalUnitCount = store.fuzzy_units() + store.untranslated_unitcount() + store.translated_unitcount()
        item = QtGui.QTableWidgetItem(str(totalUnitCount))
        self.ui.tableCatalog.setItem(row, 3, item)
        
        if hasattr(store, "parseheader"):
            headerDic = store.parseheader()
            try:
                item = QtGui.QTableWidgetItem(str(headerDic["Last-Translator"]))
                self.ui.tableCatalog.setItem(row, 6, item)
            except:
                pass
            try:
                item = QtGui.QTableWidgetItem(str(headerDic["PO-Revision-Date"]))
                self.ui.tableCatalog.setItem(row, 5, item)
            except:
                pass
    
    def setupCheckbox(self):
        if not (World.settings.value("Catalog.Name").toBool()):
            self.Catalog.ui.chbname.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbname.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Fuzzy").toBool()):
            self.Catalog.ui.chbfuzzy.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbfuzzy.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Untranslated").toBool()):
            self.Catalog.ui.chbuntranslated.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbuntranslated.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Total").toBool()):
            self.Catalog.ui.chbtotal.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbtotal.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.CVS/SVN Status").toBool()):
            self.Catalog.ui.chbSVN.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbSVN.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Last Revision").toBool()):
            self.Catalog.ui.chblastrevision.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chblastrevision.setCheckState(QtCore.Qt.Checked)
        
        if not (World.settings.value("Catalog.Last Translator").toBool()):
            self.Catalog.ui.chbtranslator.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.Catalog.ui.chbtranslator.setCheckState(QtCore.Qt.Checked)

if __name__ == "__main__":
    import sys, os
    app = QtGui.QApplication(sys.argv)
    catalog = Catalog(None)
    catalog.showDialog()
    sys.exit(catalog.exec_())
