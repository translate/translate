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
from pootling.ui.Ui_TableGlossary import Ui_Form
import sys, os


class TableGlossary(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("glossaryDock")
        self.setWindowTitle(self.tr("Glossary Lookup"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.ui.tblGlossary.setEnabled(False)
        self.headerLabels = [self.tr("Term"),self.tr("Definition")]
        self.ui.tblGlossary.setColumnCount(len(self.headerLabels))
        self.ui.tblGlossary.setHorizontalHeaderLabels(self.headerLabels)
        for i in range(len(self.headerLabels)):
            self.ui.tblGlossary.resizeColumnToContents(i)
            self.ui.tblGlossary.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
        self.ui.tblGlossary.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tblGlossary.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.toggleViewAction().setVisible(True)

    def newUnit(self):
        self.ui.tblGlossary.clear()
        self.ui.tblGlossary.setEnabled(True)
        self.ui.tblGlossary.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblGlossary.setRowCount(0)
                
    def fillTable(self, candidates):
        '''fill each found unit into table
        @param candidates:list of pofile object'''
        for unit in candidates:
            row = self.ui.tblGlossary.rowCount()
            self.ui.tblGlossary.setRowCount(row + 1)
            
            item = QtGui.QTableWidgetItem(unit.source)
            item.setFlags(self.normalState)
            self.ui.tblGlossary.setItem(row, 0, item)
            
            item = QtGui.QTableWidgetItem(unit.target)
            item.setFlags(self.normalState)
            self.ui.tblGlossary.setItem(row, 1, item)
        
    def closeEvent(self, event):
        """
        set text of action object to 'show table TM' before closing table TM
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    table = TableGlossary(None)
    table.show()
    sys.exit(table.exec_())

