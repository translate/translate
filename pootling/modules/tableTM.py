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
        self.headerLabels = [self.tr("Similarity"),self.tr("Source"), self.tr("Target")]
        self.ui.tblTM.setColumnCount(len(self.headerLabels))
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblTM.resizeColumnToContents(0)
        self.ui.tblTM.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.tblTM.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.tblTM.verticalHeader().hide()
        self.ui.tblTM.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tblTM.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.ui.tblTM.selectRow(0)
        self.infoIcon = QtGui.QIcon("../images/TM_info.png")
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
        """
        Fill table with candidates source and target.
        @param candidates: list of unit.
        """
        if (not self.isVisible()):
            return
            
        if (not candidates):
            return
        for unit in candidates:
            row = self.ui.tblTM.rowCount()
            self.ui.tblTM.setRowCount(row + 1)
            similarity = unit.getnotes("translator").rjust(4)
            item = QtGui.QTableWidgetItem(similarity)
            item.setFlags(self.normalState)
            item.setTextAlignment(QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter)
            self.ui.tblTM.setItem(row, 0, item)
            
            item = QtGui.QTableWidgetItem(unit.source)
            item.setFlags(self.normalState)
            self.ui.tblTM.setItem(row, 1, item)
            
            item = QtGui.QTableWidgetItem(unit.target)
            item.setFlags(self.normalState)
            self.ui.tblTM.setItem(row, 2, item)
            tooltips = "<h5>Found in: </h5>" + unit.filepath + "<h5> Translator: </h5>" + unit.translator + "<h5> Date: </h5>" + unit.date
            self.setToolTip(row, 0, tooltips, self.infoIcon)
            self.setToolTip(row, 1, unit.source )
            self.setToolTip(row, 2, unit.target)
            
        self.ui.tblTM.setSortingEnabled(True)
        self.ui.tblTM.horizontalHeader().setSortIndicatorShown(False)
        self.ui.tblTM.sortItems(0, QtCore.Qt.DescendingOrder)
        self.ui.tblTM.resizeRowsToContents()
        self.show()
        self.createContextMenu()
        self.ui.tblTM.setCurrentCell(0,0)
        self.getCurrentTarget(0,0,0,0)

    def clearInfo(self):
        """Clear all information in both table and labels."""
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

    def emitTarget(self):
        """@emit targetChanged signal and send the current target."""
        self.emit(QtCore.SIGNAL("targetChanged"), unicode(self.target))
    
    def emitOpenFile(self):
        """
        Send "openFile" signal with filename together with the findUnit signal with the current source.
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
        
    def setToolTip(self, index = None, col = 0, tooltips = "", icon = QtGui.QIcon()):
        """
        mark icon indicate unit has more info and add tooltips.
        @param index: row in table.
        @param col: column to set tooltips.
        @param tooltips: more info about candidates such as which file the candidate locates, who is the translator and when.
        @param icon: icon to set to col.
        """
        # get the current row
        if (not index):
            item = self.ui.tblTM.item(0, col)
        else:
            item = self.ui.tblTM.item(index, col)
        
        if (not item):
            return
        if (tooltips):
            item.setIcon(icon)
            item.setToolTip(unicode(tooltips))

    def closeEvent(self, event):
        """
        Unchecked the TM Lookup view action.
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        self.emit(QtCore.SIGNAL("visible"), False)
        
    def showEvent(self, event):
        """
        Checked the TM Lookup view action.
        @param QShowEvent Object: received show event when showing widget
        """
        QtGui.QDockWidget.showEvent(self, event)
        self.toggleViewAction().setChecked(True)
        self.emit(QtCore.SIGNAL("visible"), True)
    
    def newUnit(self):
        """
        Clear table to be filled by a new unit.
        """
        self.ui.tblTM.setEnabled(True)
        self.ui.tblTM.clear()
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblTM.setSortingEnabled(False)
        self.ui.tblTM.setRowCount(0)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    table = tableTM(None)
    table.show()
    sys.exit(table.exec_())

