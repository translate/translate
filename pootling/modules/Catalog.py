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
from pootling.modules import tmSetting
from pootling.modules.AboutEditor import AboutEditor
from translate.storage import factory
import pootling.modules.World as World
from pootling.modules.FindInCatalog import FindInCatalog
from pootling.ui.Ui_tmSetting import Ui_tmsetting
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
        self.autoRefresh = True

        self.ui.toolBar.toggleViewAction()
        self.ui.toolBar.setWindowTitle("ToolBar View")
        self.ui.toolBar.setStatusTip("Toggle ToolBar View")
        
        self.folderIcon = QtGui.QIcon("../images/open.png")
        self.iconFile = QtGui.QIcon("../images/iconfile.png")
        
        # set up table appearance and behavior
        self.headerLabels = [self.tr("Name"),
                            self.tr("Translated"),
                            self.tr("Fuzzy"),
                            self.tr("Untranslated"),
                            self.tr("Total"),
                            self.tr("CVS/SVN Status"),
                            self.tr("Last Revision"),
                            self.tr("Last Translator")]
        self.ui.treeCatalog.setColumnCount(len(self.headerLabels))
        self.ui.treeCatalog.setHeaderLabels(self.headerLabels)
        self.ui.treeCatalog.hideColumn(5)
        self.ui.treeCatalog.header().setResizeMode(QtGui.QHeaderView.Interactive)
        self.ui.treeCatalog.setWhatsThis("The catalog manager merges all files and folders enter one treewidget and displays all po, xlf... files. the way you can easily see if a template has been added or removed. Also some information about the files is displayed.")
        
        # File menu action
        self.connect(self.ui.actionQuit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        self.ui.actionQuit.setWhatsThis("<h3>Quit</h3>Quit Catalog")
        self.ui.actionQuit.setStatusTip("Quit application")

        # Edit menu action
        self.connect(self.ui.actionReload, QtCore.SIGNAL("triggered()"), self.refresh)
        self.ui.actionReload.setWhatsThis("<h3>Reload</h3>Set the current files or folders to get the most up-to-date version.")
        self.ui.actionReload.setStatusTip("Reload the current files")

        # create statistics action
        self.connect(self.ui.actionStatistics, QtCore.SIGNAL("triggered()"), self.showStatistic)
        self.ui.actionStatistics.setWhatsThis("<h3>Statistics</h3>Show status of files that have filename, fuzzy, untranslated,translated and total of strings.")
        self.ui.actionStatistics.setStatusTip("Show status of files")

        # Catalog setting's checkboxes action.
        self.catSetting = CatalogSetting(self)
        self.connect(self.ui.actionConfigure, QtCore.SIGNAL("triggered()"), self.catSetting.show)
        self.connect(self.ui.actionBuildTM, QtCore.SIGNAL("triggered()"), self.buildTM)
        self.ui.actionConfigure.setWhatsThis("<h3>Configure...</h3>Set the configuration items with your prefered values.")
        self.ui.actionConfigure.setStatusTip("Set the prefered configuration")
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
        self.ui.actionFind_in_Files.setStatusTip("Search for a text")
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

        # timer..
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateStatistic)
        self.lastFoundNumber = 0
        
        # context menu of items
        self.menu = QtGui.QMenu()
        self.actionOpen = self.menu.addAction(QtGui.QIcon("../images/open.png"), self.tr("Open"))
        self.actionFind = self.menu.addAction(QtGui.QIcon("../images/find.png"), self.tr("Find"))
        self.actionShowStat = self.menu.addAction(QtGui.QIcon("../images/statistic.png"), self.tr("Show statistic"))
        if (self.autoRefresh):
            self.actionOpen.setEnabled(False)
            self.actionFind.setEnabled(False)
            self.actionShowStat.setEnabled(False)

        self.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.emitOpenFile)
        self.connect(self.actionFind, QtCore.SIGNAL("triggered()"), self.findBar.showFind)
        self.connect(self.actionShowStat, QtCore.SIGNAL("triggered()"), self.showStatistic)

    def find(self, searchString, searchOptions):
        if (not (searchString and searchOptions)):
            return
        
        for i in range(self.lastFoundNumber, len(self.fileItems)):
            item = self.fileItems[i]
            filename = self.getFilename(item)
            found = self.searchInString(searchString, filename, searchOptions)
            if (found):
                self.ui.treeCatalog.setCurrentItem(item)
                self.emit(QtCore.SIGNAL("openFile"), filename)
                self.emit(QtCore.SIGNAL("goto"), found)
                self.lastFoundNumber = i+1
                break
        else:
            QtGui.QMessageBox.information(self, self.tr("Search"), 
                    self.tr("Search has reached the end of catalog."))
            self.lastFoundNumber = 0
    
    def searchInString(self, searchString, filename, searchOptions):
          found = False
          if (not os.path.isfile(filename)):
              return False
          store = factory.getobject(filename)
          if (not store):
              return False
          unitIndex = 0
          for unit in store.units:
              searchableText = ""
              if (searchOptions == World.source):
                  searchableText = unit.source
              elif (searchOptions == World.target):
                  searchableText = unit.target
              elif (searchOptions == (World.source + World.target)):
                  searchableText = unit.source + unit.target
              if (searchableText.find(searchString) != -1 ):
                  found = unitIndex
                  break
              unitIndex += 1
          return found

    def showStatistic(self):
        item = self.ui.treeCatalog.currentItem()
        if (not item):
            return
        
        filename = self.getFilename(item)
        title = unicode(os.path.basename(filename))
        
        self.numOfFiles = 0
        stats = self.getStatsFromItem(item)
        translated = stats["translated"]
        fuzzy = stats["fuzzy"]
        untranslated = stats["untranslated"]
        total = float(translated + fuzzy + untranslated)
        
        if (total > 0):
            perTranslated = str((translated/total) * 100)
            perTranslated = perTranslated[0:perTranslated.find(".")+3] + "%"
            perFuzzy = str((fuzzy/total) * 100)
            perFuzzy = perFuzzy[0:perFuzzy.find(".")+3] + "%"
            perUntranslated = str((untranslated/total) * 100)
            perUntranslated = perUntranslated[0:perUntranslated.find(".")+3] + "%"
        else:
            perTranslated = "0%"
            perFuzzy = "0%"
            perUntranslated = "0%"
        
        message = "Statistic of "+ title + ":\n\n" + \
                "Number of files: " + str(self.numOfFiles) + \
                "\nTranslated:\t" + str(translated) + "\t" + perTranslated + \
                "\nFuzzy:\t" + str(fuzzy) + "\t" + perFuzzy + \
                "\nUntranslated:\t" + str(untranslated) + "\t" + perUntranslated + \
                "\nTotal:\t" + str(int(total))
            
        QtGui.QMessageBox.information(self, self.tr("Statistic"), message , "OK")

    def toggleHeaderItem(self):
        if (isinstance(self.sender(), QtGui.QCheckBox)):
            text = self.sender().text()
            if text in self.headerLabels:
                checked = self.sender().isChecked()
                if (checked):
                    self.ui.treeCatalog.showColumn(self.headerLabels.index(text))
                    self.ui.treeCatalog.hideColumn(5)
                else:
                    self.ui.treeCatalog.hideColumn(self.headerLabels.index(text))
                    self.ui.treeCatalog.hideColumn(5)
                World.settings.setValue("Catalog." + text, QtCore.QVariant(checked))

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
        # Icon enabled when toolBar not files into treeCatalog
        self.ui.actionFind_in_Files.setEnabled(True)
        self.ui.actionStatistics.setEnabled(True)
        self.ui.actionReload.setEnabled(True)
        # Icon enabled when context menu not files into treeCatalog
        self.actionOpen.setEnabled(True)
        self.actionFind.setEnabled(True)
        self.actionShowStat.setEnabled(True)
        self.ui.treeCatalog.clear()
        cats = World.settings.value("CatalogPath").toStringList()
        includeSub = World.settings.value("diveIntoSubCatalog").toBool()
        
        self.fileItems = []
        self.itemNumber = 0
        
        for catalogFile in cats:
            catalogFile = unicode(catalogFile)
            self.addCatalogFile(catalogFile, includeSub, None)
        
        self.ui.treeCatalog.resizeColumnToContents(0)
        self.timer.start(10)
    
    def addCatalogFile(self, path, includeSub, item):
        """
        add path to catalog tree view if it's file, if it's directory then
        dive into it and add files.
        """
        if (os.path.isfile(path)):
            existedItem = self.getExistedItem(os.path.dirname(path))
            if (existedItem):
                item = existedItem
            elif (item == None):
                item = QtGui.QTreeWidgetItem(item)
                self.ui.treeCatalog.addTopLevelItem(item)
                self.ui.treeCatalog.expandItem(item)
                item.setText(0, os.path.dirname(path))
  
            # if file is already existed in the item's child... skip.
            noSupportedFile = True
            if (path.endswith(".po") or path.endswith(".pot") or path.endswith(".xlf") or path.endswith(".xliff")) and (not self.ifFileExisted(path, item)):
                childItem = QtGui.QTreeWidgetItem(item)
                childItem.setText(0, os.path.basename(path))
                childItem.setIcon(0, self.iconFile)
                self.fileItems.append(childItem)
            # check extension of file if not have .po or .pot or xlf and xliff files. hide folder
                noSupportedFile = False
            if noSupportedFile:
                item.setHidden(True)

        if (os.path.isdir(path)) and (not path.endswith(".svn")):
            existedItem = self.getExistedItem(path)
            if (existedItem):
                # it's already existed, so use the existed one
                childItem = existedItem
            else:
                # it does not exist in tree yet, create new one
                if (item == None):
                    childItem = QtGui.QTreeWidgetItem(item)
                    self.ui.treeCatalog.addTopLevelItem(childItem)
                    self.ui.treeCatalog.expandItem(childItem)
                    childItem.setText(0, path)
                # it's existed in tree but it is the sub directory
                elif hasattr(item, "parent"):
##                    childItem = QtGui.QTreeWidgetItem()
##                    item.insertChild(0, childItem)
                    childItem = QtGui.QTreeWidgetItem(item)
                    childItem.setText(0, os.path.basename(path))
                childItem.setIcon(0, self.folderIcon)

            for root, dirs, files in os.walk(path):
                for file in files:
                    path = os.path.join(root + os.path.sep + file)
                    self.addCatalogFile(path, includeSub, childItem)
                # whether dive into subfolder
                if (includeSub):
                    for folder in dirs:
                        path = os.path.join(root + os.path.sep + folder)
                        self.addCatalogFile(path, includeSub, childItem)

                break
    
    def getExistedItem(self, path):
        """
        Get existed item in the tree's top level. If the item existed, it returns
        the item, otherwise returns False.
        """
        for i in range(self.ui.treeCatalog.topLevelItemCount()):
            item = self.ui.treeCatalog.topLevelItem(i)
            if (hasattr(item, "text")) and (item.text(0) == path):
                return item
        return False
    
    def ifFileExisted(self, path, item):
        """
        Get existed item in the tree's top level. If the item existed, it returns
        the item, otherwise returns False.
        """
        if (not hasattr(item, "childCount")):
            return False
        for i in range(item.childCount()):
            it = item.child(i)
            if (hasattr(it, "text")) and (it.text(0) == os.path.basename(path)):
                return it
        return False
    
    def getStats(self, filename):
        """
        return a dictionary which consist of basename, translatedCount, fuzzyCount,
        untranslatedCount, totalCount, subVersionState, revisionDate, lastTranslator
        or return False when error.
        @param filename: path and file name.
        """
        try:
            store = factory.getobject(filename)
        except:
            return False
        
        if (not os.path.isfile(filename)):
            return False
        
        basename = os.path.basename(filename)
        numTranslated = store.translated_unitcount()
        numFuzzy = store.fuzzy_unitcount()
        numUntranslated = store.untranslated_unitcount()
    
        numTotal = numTranslated + numUntranslated + numFuzzy
        subVersionState = ""
        
        revisionDate = ""
        lastTranslator = ""
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
        
        return {"basename":basename, "numTranslated":numTranslated, "numFuzzy":numFuzzy, 
                "numUntranslated":numUntranslated, "numTotal":numTotal, 
                "subVersionState":subVersionState, "revisionDate":revisionDate, 
                "lastTranslator":lastTranslator}
    
    def getStatsFromItem(self, item):
        """
        get number of translated, untranslated, and fuzzy units from item.
        @param item: treewidget item which has at least those four fields.
        @return dictionary of stats.
        """
        try:
            translated = int(item.text(1))
            fuzzy = int(item.text(2))
            untranslated = int(item.text(3))
            self.numOfFiles += 1
        except:
            translated = 0
            fuzzy = 0
            untranslated = 0
        
        for i in range(item.childCount()):
            child = item.child(i)
            stats = self.getStatsFromItem(child)
            translated += stats["translated"]
            fuzzy += stats["fuzzy"]
            untranslated += stats["untranslated"]
        
        
        return {"translated": translated, "fuzzy":fuzzy, "untranslated":untranslated}
    
    def setupCheckbox(self):
        value = World.settings.value("Catalog.Name")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            # on fresh start of program, if the value is not in setting yet
            # make it True by default.
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbname.setCheckState(checkState)
        
        value = World.settings.value("Catalog.Translated")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbtranslated.setCheckState(checkState)
        
        value = World.settings.value("Catalog.Fuzzy")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbfuzzy.setCheckState(checkState)
        
        value = World.settings.value("Catalog.Untranslated")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbuntranslated.setCheckState(checkState)
        
        value = World.settings.value("Catalog.Total")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbtotal.setCheckState(checkState)
        
        value = World.settings.value("Catalog.CVS/SVN Status")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbSVN.setCheckState(checkState)
        self.catSetting.ui.chbSVN.setVisible(False)
        
        value = World.settings.value("Catalog.Last Revision")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chblastrevision.setCheckState(checkState)
        
        value = World.settings.value("Catalog.Last Translator")
        if (value.isValid()):
            if not (value.toBool()):
                checkState = QtCore.Qt.Unchecked
            else:
                checkState = QtCore.Qt.Checked
        else:
            checkState = QtCore.Qt.Checked
        self.catSetting.ui.chbtranslator.setCheckState(checkState)
        
    def emitOpenFile(self, item=None, col=None):
        """
        Send "openFile" signal with filename.
        """
        if (not item):
            try:
                item = self.ui.treeCatalog.selectedItems()[0]
            except:
                return
        
        filename = self.getFilename(item)
        if (os.path.isfile(filename)): 
            self.emit(QtCore.SIGNAL("openFile"), filename)
        
    def getFilename(self, item):
        """
        return filename join from item.text(0) to its parent.
        """
        if (not item):
            return None
        
        filename = unicode(item.text(0))
        if (item.parent()):
            filename = os.path.join(self.getFilename(item.parent()) + os.path.sep + filename)
        return filename
    
    def refresh(self):
        self.settings = QtCore.QSettings()
        if self.autoRefresh:
            self.updateCatalog()
        else:
            self.settings.sync()

    def buildTM(self):
        """Build Translation Memory"""
        cats = self.ui.treeCatalog.topLevelItem(0)
        if cats:
            catalogPath = cats.text(0)
            self.tmSetting = tmSetting.tmSetting(None)
            self.tmSetting.showDialog()
            self.tmSetting.addLocation(catalogPath)
            self.tmSetting.createTM()
        else:
            return
    
    def updateStatistic(self):
        if (len(self.fileItems) <= 0):
            self.timer.stop()
            self.itemNumber = 0
            return

        self.timer.stop()
        
        item = self.fileItems[self.itemNumber]
        path = self.getFilename(item)
        childStats = self.getStats(path)
  
        if (childStats):
            item.setText(1, str(childStats["numTranslated"]))
            item.setText(2, str(childStats["numFuzzy"]))
            item.setText(3, str(childStats["numUntranslated"]))
            item.setText(4, str(childStats["numTotal"]))
            item.setText(5, childStats["subVersionState"])
            item.setText(6, childStats["revisionDate"])
            item.setText(7, childStats["lastTranslator"])

        self.itemNumber += 1
        
        perc = int((float(self.itemNumber) / len(self.fileItems)) * 100)
        self.updateProgress(perc)
        
        # start getting statistic
        self.timer.start(10)
        if (self.itemNumber == len(self.fileItems)):
            self.timer.stop()
            self.itemNumber = 0
    
    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())

def main(self):
    # set the path for QT in order to find the icons
    if __name__ == "__main__":
        QtCore.QDir.setCurrent(os.path.join(sys.path[0], "../ui"))
        app = QtGui.QApplication(sys.argv)
        catalog = Catalog()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
