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
# This module is providing an setting path of catalog dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_CatalogSetting import Ui_catalogSetting
from pootling.modules import World
from pootling.modules import FileDialog

class CatalogSetting(QtGui.QDialog):
    """
    Code for setting path of translation memory dialog
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.subscan = None
        self.catalogModified = False
        self.ui = Ui_catalogSetting()
        self.ui.setupUi(self)
        self.setWindowTitle("Setting Catalog Manager")
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.showFileDialog)
        self.filedialog = FileDialog.fileDialog(self)
        self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
        self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
        self.connect(self.ui.btnDelete, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
        self.connect(self.ui.btnClear, QtCore.SIGNAL("clicked(bool)"), self.clearLocation)
        self.connect(self.ui.btnMoveUp, QtCore.SIGNAL("clicked(bool)"), self.moveUp)
        self.connect(self.ui.btnMoveDown, QtCore.SIGNAL("clicked(bool)"), self.moveDown)
        self.connect(self.ui.chbDiveIntoSubfolders, QtCore.SIGNAL("stateChanged(int)"), self.rememberDive)
        self.ui.listWidget.addItems(World.settings.value("CatalogPath").toStringList())
        self.setModal(True)
        self.ui.chbDiveIntoSubfolders.setChecked(World.settings.value("diveIntoSubCatalog").toBool())

    def showFileDialog(self):
        self.filedialog.show()
    
    def addLocation(self, text):
        items = self.ui.listWidget.findItems(text, QtCore.Qt.MatchCaseSensitive)
        if (not items):
            item = QtGui.QListWidgetItem(text)
            self.ui.listWidget.addItem(item)
            self.catalogModified = True
    
    def clearLocation(self):
        self.ui.listWidget.clear()
        self.catalogModified = True
        self.ui.chbDiveIntoSubfolders.setChecked(False)
    
    def removeLocation(self):
        self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
        self.catalogModified = True
    
    def moveItem(self, distance):
        '''move an item up or down depending on distance
        @param distance: int'''
        currentrow = self.ui.listWidget.currentRow()
        currentItem = self.ui.listWidget.item(currentrow)
        distanceItem = self.ui.listWidget.item(currentrow + distance)
        if (distanceItem):
            temp = distanceItem.text()
            distanceItem.setText(currentItem.text())
            currentItem.setText(temp)
            self.ui.listWidget.setCurrentRow(currentrow + distance)
        
    def moveUp(self):
        '''move item up'''
        self.moveItem(-1)
    
    def moveDown(self):
        '''move item down'''
        self.moveItem(1)
    
    def rememberDive(self):
        World.settings.setValue("diveIntoSubCatalog", QtCore.QVariant(self.ui.chbDiveIntoSubfolders.isChecked()))
        self.catalogModified = True

    def closeEvent(self, event):
        stringlist = QtCore.QStringList()
        for i in range(self.ui.listWidget.count()):
            stringlist.append(self.ui.listWidget.item(i).text())
        World.settings.setValue("CatalogPath", QtCore.QVariant(stringlist))
        QtGui.QDialog.closeEvent(self, event)
        
        if (self.catalogModified):
            self.emit(QtCore.SIGNAL("updateCatalog"))
            self.catalogModified = False
    stringlist = QtCore.QStringList()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = CatalogSetting(None)
    tm.show()
    sys.exit(tm.exec_())

