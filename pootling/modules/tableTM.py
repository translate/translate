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

from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_TableTM import Ui_Form
import sys, os

class tableTM(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("miscDock")
        self.setWindowTitle(self.tr("TM &Lookup"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.ui.tblTM.setEnabled(False)
        self.headerLabels = [self.tr("Similarity"),self.tr("Source"), self.tr("Target")]
        self.ui.tblTM.setColumnCount(len(self.headerLabels))
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        for i in range(len(self.headerLabels)):
            self.ui.tblTM.resizeColumnToContents(i)
            self.ui.tblTM.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
        self.ui.tblTM.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
        self.connect(self.ui.tblTM, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.getCurrentTarget)
        self.connect(self.ui.tblTM, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.emitTarget)
        
    def fillTable(self, candidates):
        '''fill each found unit into table
        @param candidateslist:list of pofile object'''
        
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
            self.ui.tblTM.setItem(row, 2, item)
                
        self.ui.tblTM.setSortingEnabled(True)
        self.ui.tblTM.sortItems(0)
        self.ui.tblTM.resizeRowsToContents()
        self.show()
    
    def getCurrentTarget(self, row, col, preRow, preCol):
        item = self.ui.tblTM.item(row, 2)
        if (item):
            self.target = item.text()
    
    def emitTarget(self):
        self.emit(QtCore.SIGNAL("targetChanged"), self.target)
    
    def filterChanged(self, filter, lenFilter):
        if (not lenFilter):
            self.ui.tblTM.setRowCount(0)
            self.ui.tblTM.clear()
        self.ui.tblTM.setEnabled(not(lenFilter) and False or True)
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    table = tableTM(None)
    table.show()
    sys.exit(table.exec_())

