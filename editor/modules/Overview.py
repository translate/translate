#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on overview of source and target

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_Overview import Ui_Form
from modules.World import World

class OverviewDock(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Overview"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)        
        self.setWidget(self.form)
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowOverview")        
        self._actionShow.setText(self.tr("Hide Overview"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)
        
        # set up table appearance and behavior
        
        self.headerLabels = [self.tr("Index"), self.tr("Source"), self.tr("Target"), self.tr("Note")]
        self.ui.tableOverview.setColumnCount(4)
        self.ui.tableOverview.setRowCount(0)
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableOverview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.tableOverview.horizontalHeader().setSortIndicatorShown(True)
        self.ui.tableOverview.resizeColumnToContents(0)
        self.ui.tableOverview.resizeColumnToContents(3)
        self.ui.tableOverview.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setHighlightSections(False)        
        #self.ui.tableOverview.verticalHeader().hide()
        
        self.headerFont = QtGui.QFont('Sans Serif', 10)
        self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)
        self.applySettings()
        
        # indexToUpdate holds the last item selected
        self.indexToUpdate = None
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        #self.connect(self.ui.tableOverview, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.emitTargetChanged)

    def actionShow(self):
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Overview"))    
        else:
            self._actionShow.setText(self.tr("Show Overview"))    
        self.setHidden(not self.isHidden())    

    def slotNewUnits(self, units, unitsStatus):
        """Initialize the list, clear and fill with units."""
        self.ui.tableOverview.setEnabled(True)
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setRowCount(len(units))
        i = 0
        normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.setUpdatesEnabled(False)
        for unit in units:
            item0 = QtGui.QTableWidgetItem(str(i).rjust(4))
            item1 = QtGui.QTableWidgetItem(unit.source)
            item2 = QtGui.QTableWidgetItem(unit.target)
            item3 = QtGui.QTableWidgetItem(self.stateString(unitsStatus[i]))
            item0.setTextAlignment(QtCore.Qt.AlignCenter)
            item0.setFlags(normalState)
            item1.setFlags(normalState)
            item2.setFlags(normalState)
            item3.setFlags(normalState)
            self.ui.tableOverview.setItem(i, 0, item0)
            self.ui.tableOverview.setItem(i, 1, item1)
            self.ui.tableOverview.setItem(i, 2, item2)
            self.ui.tableOverview.setItem(i, 3, item3)
            i += 1
        self.ui.tableOverview.resizeRowsToContents()
        self.setUpdatesEnabled(True)

    def filteredList(self, shownList):
        """Show the items that are in filtered list."""
        self.setUpdatesEnabled(False)
        hiddenList = range(self.ui.tableOverview.rowCount())
        for i in shownList:
            self.ui.tableOverview.showRow(i)
            hiddenList.remove(i)
        for i in hiddenList:
            self.ui.tableOverview.hideRow(i)
        self.setUpdatesEnabled(True)

    def emitCurrentIndex(self):
        """Send current row's index."""
        row = self.ui.tableOverview.currentRow()
        index = int(self.ui.tableOverview.item(row, 0).text())
        # send the signal only row is new
        if (self.indexToUpdate != index):
            self.emit(QtCore.SIGNAL("currentIndex"), index)

    def updateView(self, unit, index, state):
        """Highlight the row of current unit index."""
        # TODO: must convert index to row in order to highlight the correct unit.
        # (Not done)
        #self.indexToUpdate = index
        #self.ui.tableOverview.selectRow(index)
##        # display unit status on note column.
##        if (state):
##            noteItem = self.ui.tableOverview.item(row, 3)
##            item = QtGui.QTableWidgetItem(self.stateString(state))
##            self.ui.tableOverview.setItem(self.indexToUpdate, 3, item)
    
    def stateString(self, state):
        status = ""
        if (state & self.world.fuzzy):
            status += " F"
        #if (state & self.world.translated):
        #    status += " T"
        if (state & self.world.untranslated):
            status += " U"
        return status
        
    def updateTarget(self, target):
        """Update the text in target column."""
        if (self.indexToUpdate):
            item = QtGui.QTableWidgetItem(target)
            self.ui.tableOverview.setItem(self.indexToUpdate, 2, item)
            #item = self.ui.tableOverview.item(self.ui.tableOverview.currentRow(), 0)
            #index = int(item.text())
            #self.ui.tableOverview.resizeRowToContents(index)
        
    def hideUnit(self, index):
        """Hide row at index."""
        self.ui.tableOverview.hideRow(index)

##    def emitTargetChanged(self):
##        """Send target as string and signal targetChanged."""
##        item = self.ui.tableOverview.item(self.ui.tableOverview.currentRow(), 0)
##        index = int(item.text())
##        if (index >= 0):
##            target = unicode(self.ui.tableOverview.item(index, 2).text())
##            self.emit(QtCore.SIGNAL("targetChanged"), target)
        
    def applySettings(self):
        font = self.settings.value("overviewFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.tableOverview.setFont(fontObj)
                self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock()
    overview.show()
    sys.exit(app.exec_())
