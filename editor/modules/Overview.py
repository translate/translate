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

from PyQt4 import QtCore, QtGui
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
        self.applySettings()
        self.fuzzyIcon = QtGui.QIcon("../images/fuzzy.png")
        self.noteIcon = QtGui.QIcon("../images/note.png")
        self.approvedIcon = QtGui.QIcon("../images/approved.png")
        self.blankIcon = QtGui.QIcon()
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.indexMaxLen = 0
        self.units = []
        self.selectedIndex = 0
        self.visibleRow = []
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        self.connect(self.ui.tableOverview.model(), QtCore.SIGNAL("layoutChanged()"), self.showFilteredItems)
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Overview' before closing Overview
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        
    def slotNewUnits(self, units):
        self.disconnect(self.ui.tableOverview, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.emitTargetChanged)
        self.ui.tableOverview.setEnabled(bool(units))
        self.indexMaxLen = len(str(len(units)))
        self.setUpdatesEnabled(False)
        self.filter = World.filterAll
        self.units = []
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSortingEnabled(False)
        self.ui.tableOverview.setRowCount(0)
        for unit in units:
            self.addUnit(unit)
        self.ui.tableOverview.setSortingEnabled(True)
        self.setUpdatesEnabled(True)
        self.ui.tableOverview.sortItems(0)
        self.ui.tableOverview.resizeRowsToContents()
        self.units = units
        self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), True, False)
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.emitTargetChanged)

    def filterChanged(self, filter, lenFilter):
        """show the items which are in filter.
        @param filter: helper constants for filtering
        @param lenFilter: len of filtered items."""
        if (filter == self.filter):
            return
        if (lenFilter == 0):
            self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), True, True)
        self.filter = filter
        self.showFilteredItems()
        
    def addUnit(self, unit):
        """add unit to row.
        @param unit: unit class."""
        row = self.ui.tableOverview.rowCount()
        self.ui.tableOverview.setRowCount(row + 1)
        item = QtGui.QTableWidgetItem(self.indexString(unit.x_editor_index))
        item.setTextAlignment(QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter)
        item.setFlags(self.normalState)
        unit.x_editor_tableItem = item
        self.ui.tableOverview.setItem(row, 0, item)
        self.markComment(row, unit.getnotes())
        
        item = QtGui.QTableWidgetItem(unit.source)
        item.setFlags(self.normalState)
        self.ui.tableOverview.setItem(row, 1, item)
        
        item = QtGui.QTableWidgetItem(unit.target)
        self.ui.tableOverview.setItem(row, 2, item)
        
        item = QtGui.QTableWidgetItem()
        item.setFlags(self.normalState)
        self.ui.tableOverview.setItem(row, 3, item)
        self.markState(row, unit.x_editor_state)
    
    def emitCurrentIndex(self):
        """send the selected unit index."""
        selectedItems = self.ui.tableOverview.selectedItems()
        if (len(selectedItems) > 0):
            index = int(selectedItems[0].text())
            self.disconnect(self.ui.tableOverview, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.emitTargetChanged)
            self.emit(QtCore.SIGNAL("currentIndex"), index)
            self.connect(self.ui.tableOverview, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.emitTargetChanged)

    def updateView(self, unit):
        """highlight the table's row at index.
        @param unit: """
        if (not unit) or (not hasattr(unit, "x_editor_tableItem")):
            return
        row = self.ui.tableOverview.row(unit.x_editor_tableItem)
        self.lastRow = row
        self.markComment(row, unit.getnotes())
        self.markState(row, unit.x_editor_state)
        self.disconnect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        self.ui.tableOverview.selectRow(row)
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        self.ui.tableOverview.scrollToItem(unit.x_editor_tableItem)
        
        if (self.visibleRow):
            self.selectedIndex = self.visibleRow.index(row)
        firstUnit = (self.selectedIndex == 0)
        lastUnit = (self.selectedIndex >= len(self.visibleRow) -1)
        self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), firstUnit, lastUnit)
        
    def markState(self, index, state):
        """display unit status on note column, and hide if unit is not in filter.
        @param index: row in table to set property.
        @param state: state of unit defined in world.py."""
        item = self.ui.tableOverview.item(index, 3)
        if (state & World.fuzzy):
            item.setIcon(self.fuzzyIcon)
            item.setToolTip("fuzzy")
        else:
            item.setIcon(self.blankIcon)
            item.setToolTip("")
    
    def updateTarget(self, text):
        """change the text in target column.
        @param text: text to set into target field."""
        row = self.lastRow
        item = self.ui.tableOverview.item(row, 2)
        item.setText(text)
        self.ui.tableOverview.resizeRowToContents(row)
        if (text):
            state = World.translated
        else:
            state = World.untranslated
        self.markState(row, state)

    def applySettings(self):
        """ set color and font to the tableOverview"""
        overviewColor = World.settings.value("overviewColor")
        if (overviewColor.isValid()):
            colorObj = QtGui.QColor(overviewColor.toString())
            palette = self.ui.tableOverview.palette()
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.tableOverview.setPalette(palette)

        font = World.settings.value("overviewFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
              self.ui.tableOverview.setFont(fontObj)
              
        font = World.settings.value("overviewHeaderFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
              self.ui.tableOverview.horizontalHeader().setFont(fontObj)
              
        self.ui.tableOverview.resizeRowsToContents()
        
    def showFilteredItems(self):
        for unit in self.units:
            if hasattr(unit, "x_editor_tableItem"):
                row = self.ui.tableOverview.row(unit.x_editor_tableItem)
                if (unit.x_editor_state & self.filter):
                    self.ui.tableOverview.showRow(row)
                else:
                    self.ui.tableOverview.hideRow(row)
        self.ui.tableOverview.resizeRowsToContents()
        
        self.visibleRow = []
        for i in range(self.ui.tableOverview.rowCount()):
            if (not self.ui.tableOverview.isRowHidden(i)):
                self.visibleRow.append(i)
        if (self.visibleRow) and (len(self.ui.tableOverview.selectedItems()) > 0):
            row = self.ui.tableOverview.row(self.ui.tableOverview.selectedItems()[0])
            self.selectedIndex = self.visibleRow.index(row)
        
    def indexString(self, index):
        return str(index).rjust(self.indexMaxLen) + "  "
        
    def updateComment(self, text):
        """change the tooltip in index column, and add an icon if there is text.
        @param text: text to set as tooltip in index field."""
        self.markComment(self.lastRow, text)
        
    def markComment(self, index, note):
        item = self.ui.tableOverview.item(index, 0)
        if (note):
            item.setIcon(self.noteIcon)
            item.setToolTip(unicode(note))
        else:
            item.setIcon(self.blankIcon)
            item.setToolTip("")
    
    def scrollPrevious(self):
        """move to previous row inside the table."""
        if (self.selectedIndex > 0):
            self.selectedIndex -= 1
            self.ui.tableOverview.selectRow(self.visibleRow[self.selectedIndex])
    
    def scrollNext(self):
        """move to next row inside the table."""
        if (self.selectedIndex < len(self.visibleRow) - 1):
            self.selectedIndex += 1
            self.ui.tableOverview.selectRow(self.visibleRow[self.selectedIndex])
    
    def scrollFirst(self):
        """move to first row of the table."""
        self.selectedIndex = 0
        self.ui.tableOverview.selectRow(self.visibleRow[self.selectedIndex])
    
    def scrollLast(self):
        """move to last row of the table."""
        self.selectedIndex = len(self.visibleRow) - 1
        self.ui.tableOverview.selectRow(self.visibleRow[self.selectedIndex])
    
    def emitTargetChanged(self, cRow, cColumn, lRow, lColumn):
        """Send target as string and signal targetChanged."""
        if (lRow >= 0):
            item = self.ui.tableOverview.item(lRow, 2)
            self.emit(QtCore.SIGNAL("targetChanged"), unicode(item.text()))
    
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock(None)
    overview.show()
    sys.exit(app.exec_())
