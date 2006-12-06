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
if __name__ == "__main__":
    import os.path
    sys.path.append(os.path.join(sys.path[0], ".."))
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))

from ui.Ui_Overview import Ui_Form
import modules.World as World

class OverviewDock(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("overviewDock")
        self.setWindowTitle(self.tr("Overview"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        
        # set up table appearance and behavior
        self.headerLabels = [self.tr("Index"), self.tr("Source"), self.tr("Target"), self.tr("Status")]
        self.ui.tableOverview.setColumnCount(len(self.headerLabels))
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
        self.ui.tableOverview.verticalHeader().hide()
        
        self.headerFont = QtGui.QFont('Sans Serif', 10)
        self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)
        self.applySettings()
        self.fuzzyIcon = QtGui.QIcon("../images/fuzzy.png")
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        #self.connect(self.ui.tableOverview, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.emitTargetChanged)
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Overview' before closing Overview
        @param QCloseEvent Object: received close event when closing widget
        """        
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)

    def slotNewUnits(self, units, unitsStatus):
        """initialize the list, clear and fill with units.
        @param units: list of unit to add into table.
        @param unitsStatus: list of unit's status."""
        self.filter = World.filterAll
        self.ui.tableOverview.setEnabled(True)
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setColumnCount(len(self.headerLabels))
        self.ui.tableOverview.setRowCount(len(units))
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.setUpdatesEnabled(False)
        self.indexMaxLen = len(str(len(units)))
        self.units = units
        self.unitsStatus = unitsStatus
        self.ui.tableOverview.setSortingEnabled(False)
        i = 0
        for unit in units:
            item0 = QtGui.QTableWidgetItem(str(i).rjust(self.indexMaxLen))
            item1 = QtGui.QTableWidgetItem(unit.source)
            item2 = QtGui.QTableWidgetItem(unit.target)
            item0.setTextAlignment(QtCore.Qt.AlignCenter)
            item0.setFlags(self.normalState)
            item1.setFlags(self.normalState)
            item2.setFlags(self.normalState)
            self.ui.tableOverview.setItem(i, 0, item0)
            self.ui.tableOverview.setItem(i, 1, item1)
            self.ui.tableOverview.setItem(i, 2, item2)
            self.setUnitProperty(i, self.unitsStatus[i])
            i += 1
        self.ui.tableOverview.setSortingEnabled(True)
        self.ui.tableOverview.sortItems(0)
        self.ui.tableOverview.resizeRowsToContents()
        self.setUpdatesEnabled(True)
        

    def filteredList(self, shownList, filter):
        """show the items which are in shownList.
        @param shownList: list of unit which allow to be visible in the table.
        @param filter: shownList's filter."""
        self.setUpdatesEnabled(False)
        self.filter = filter
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setColumnCount(len(self.headerLabels))
        self.ui.tableOverview.setRowCount(len(shownList))
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSortingEnabled(False)
        j = 0
        for i in shownList:
            item0 = QtGui.QTableWidgetItem(str(i).rjust(self.indexMaxLen))
            item1 = QtGui.QTableWidgetItem(self.units[i].source)
            item2 = QtGui.QTableWidgetItem(self.units[i].target)
            item0.setTextAlignment(QtCore.Qt.AlignCenter)
            item0.setFlags(self.normalState)
            item1.setFlags(self.normalState)
            item2.setFlags(self.normalState)
            self.ui.tableOverview.setItem(j, 0, item0)
            self.ui.tableOverview.setItem(j, 1, item1)
            self.ui.tableOverview.setItem(j, 2, item2)
            self.setUnitProperty(j, self.unitsStatus[i])
            j += 1
        self.ui.tableOverview.setSortingEnabled(True)
        self.ui.tableOverview.sortItems(0)
        self.ui.tableOverview.resizeRowsToContents()
        self.setUpdatesEnabled(True)

    def emitCurrentIndex(self):
        """send the selected unit index."""
        row = self.ui.tableOverview.currentRow()
        indexToUpdate = int(self.ui.tableOverview.item(row, 0).text())
        indexOfSelectedRow = int(self.ui.tableOverview.selectedItems()[0].text())
        if (indexToUpdate != indexOfSelectedRow):
            self.emit(QtCore.SIGNAL("currentIndex"), indexOfSelectedRow)

    def updateView(self, unit, index, state):
        """highlight the table's row at index.
        @param unit: (not needed in this function).
        @param index: table's row to highlight.
        @param state: unit's state shown in table."""
        # TODO: improve conversion of index to row number.
        if (index < 0):
            return
        item = self.ui.tableOverview.findItems(str(index).rjust(self.indexMaxLen), QtCore.Qt.MatchExactly)[0]
        if (not item):
            return
        row = self.ui.tableOverview.row(item)
        self.setUnitProperty(row, state)
        self.ui.tableOverview.selectRow(row)
        self.ui.tableOverview.scrollToItem(item)

    def setUnitProperty(self, index, state):
        """display unit status on note column, and hide if unit is not in filter.
        @param index: row in table to set property.
        @param state: state of unit defined in world.py."""
        if (state & World.fuzzy):
            fuzzyItem = QtGui.QTableWidgetItem()
            fuzzyItem.setIcon(self.fuzzyIcon)
            fuzzyItem.setTextAlignment(QtCore.Qt.AlignVCenter)
            fuzzyItem.setToolTip("fuzzy")
            fuzzyItem.setFlags(self.normalState)
            self.ui.tableOverview.setItem(index, 3, fuzzyItem)
        else:
            self.ui.tableOverview.takeItem(index, 3)
##        if (not self.filter & state):
##            self.ui.tableOverview.hideRow(index)

    def updateTarget(self, text):
        """change the text in target column (indexToUpdate).
        @param text: text to set into target field."""
        row = self.ui.tableOverview.currentRow()
        indexToUpdate = int(self.ui.tableOverview.item(row, 0).text())
        if (indexToUpdate >= 0):
            item = QtGui.QTableWidgetItem(text)
            self.ui.tableOverview.setItem(indexToUpdate, 2, item)
            self.ui.tableOverview.resizeRowToContents(indexToUpdate)

##    def emitTargetChanged(self):
##        """Send target as string and signal targetChanged."""
##        item = self.ui.tableOverview.item(self.ui.tableOverview.currentRow(), 0)
##        index = int(item.text())
##        if (index >= 0):
##            target = unicode(self.ui.tableOverview.item(index, 2).text())
##            self.emit(QtCore.SIGNAL("targetChanged"), target)

    def applySettings(self):
        """ set color and font to the tableOverview"""
        overviewColor = World.settings.value("overviewColor")
        if (overviewColor.isValid()):
            colorObj = QtGui.QColor(overviewColor.toString())
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(6),colorObj)
            self.ui.tableOverview.setPalette(palette)
        
        font = World.settings.value("overviewFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
              self.ui.tableOverview.setFont(fontObj)
              self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock(None)
    overview.show()
    sys.exit(app.exec_())
