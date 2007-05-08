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
#This module is working on the display of TM in a talbe

from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_TableTM import Ui_Form
import sys, os


class tableTM(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("miscDock")
        self.setWindowTitle(self.tr("TM Lookup"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.ui.tblTM.setEnabled(False)
        self.headerLabels = [self.tr("Similarity"),self.tr("Source"), self.tr("Target"), self.tr("Location"), self.tr("Translator"), self.tr("Date"), self.tr("Index")]
        self.ui.tblTM.setColumnCount(len(self.headerLabels))
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        for i in range(len(self.headerLabels)):
            self.ui.tblTM.resizeColumnToContents(i)
            self.ui.tblTM.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
        self.ui.tblTM.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tblTM.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.ui.tblTM.selectRow(0)
        self.ui.tblTM.hideColumn(3)
        self.ui.tblTM.hideColumn(4)
        self.ui.tblTM.hideColumn(5)
        self.ui.tblTM.hideColumn(6)
        self.filepath = " "
        self.target = ""
        
        self.connect(self.ui.tblTM, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.getCurrentTarget)
        self.connect(self.ui.tblTM, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.emitTarget)
        self.createContextMenu()
        
    def createContextMenu(self):
        # context menu of items
        self.menu = QtGui.QMenu()
        actionCopyResult = self.menu.addAction(QtGui.QIcon("../images/source.png"), self.tr("Copy search result to target"))
        actionEditFile = self.menu.addAction(QtGui.QIcon("../images/open.png"),self.tr("Edit file"))
        self.connect(actionCopyResult, QtCore.SIGNAL("triggered()"), self.emitTarget)
        self.connect(actionEditFile, QtCore.SIGNAL("triggered()"), self.emitOpenFile)
        
    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())
        
    def fillTable(self, candidates):
        '''fill each found unit into table
        @param candidates:list of pofile object'''
        
        self.ui.tblTM.setEnabled(True)
        self.ui.tblTM.clear()
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblTM.setSortingEnabled(False)
        self.ui.tblTM.setRowCount(0)
        
        if (not candidates):
            return
        for unit in candidates:
            row = self.ui.tblTM.rowCount()
            self.ui.tblTM.setRowCount(row + 1)
            
            item = QtGui.QTableWidgetItem(unit.getnotes("translator"))
            item.setFlags(self.normalState)
            self.ui.tblTM.setItem(row, 0, item)
            
            item = QtGui.QTableWidgetItem(unit.source)
            item.setFlags(self.normalState)
            self.ui.tblTM.setItem(row, 1, item)
            
            item = QtGui.QTableWidgetItem(unit.target)
            item.setFlags(self.normalState)
            self.ui.tblTM.setItem(row, 2, item)
          
            
            item = QtGui.QTableWidgetItem(unit.filepath)
            self.ui.tblTM.setItem(row, 3, item)
            
            item = QtGui.QTableWidgetItem(unit.translator)
            self.ui.tblTM.setItem(row, 4, item)
            
            item = QtGui.QTableWidgetItem(unit.date)
            self.ui.tblTM.setItem(row, 5, item)
            
        self.ui.tblTM.setSortingEnabled(True)
        self.ui.tblTM.sortItems(0)
        self.ui.tblTM.resizeRowsToContents()
        self.show()
        self.createContextMenu()
        self.ui.tblTM.setCurrentCell(0,0)
        self.getCurrentTarget(0,0,0,0)

    def clearInfo(self):
        self.ui.lblPath.clear()
        self.ui.lblTranslator.clear()
        self.ui.lblDate.clear()
        self.ui.tblTM.clear()
        self.ui.tblTM.setRowCount(0)
        self.target = ""
        self.filepath = ""
        
    def getCurrentTarget(self, row, col, preRow, preCol):
        """Slot to get info from the current found unit."""
        if (row < 0):
            self.clearInfo()
        source = self.ui.tblTM.item(row, 1)
        if (source):
            self.source = source.text()
        target = self.ui.tblTM.item(row, 2)
        if (target):
            self.target = target.text()
        filepath = self.ui.tblTM.item(row, 3)
        if (filepath):
            self.filepath = filepath.text()
            self.ui.lblPath.setText(self.filepath)
        translator = self.ui.tblTM.item(row, 4)
        if (translator):
            self.ui.lblTranslator.setText(translator.text())
        date = self.ui.tblTM.item(row, 5)
        if (date):
            self.ui.lblDate.setText(date.text())
    
    def emitTarget(self):
        self.emitIsCopyResult(True)
        self.emit(QtCore.SIGNAL("targetChanged"), unicode(self.target))
        
    def emitIsCopyResult(self, bool = False):
        self.emit(QtCore.SIGNAL("isCopyResult"), bool)
        
    
    def emitOpenFile(self):
        """
        Send "openFile" signal with filename.
        """
        source = str(self.source)
        self.emit(QtCore.SIGNAL("openFile"), str(self.filepath))
        self.emit(QtCore.SIGNAL("findUnit"), source)
        
        
    def filterChanged(self, filter, lenFilter):
        if (not lenFilter):
            self.ui.tblTM.setRowCount(0)
            self.ui.tblTM.clear()
            self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblTM.setEnabled(not(lenFilter) and False or True)
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    table = tableTM(None)
    table.show()
    sys.exit(table.exec_())

