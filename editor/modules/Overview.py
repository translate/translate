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
##        self.ui.tableOverview.verticalHeader().hide()
##        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
        
##        self.headerFont = QtGui.QFont('Sans Serif', 10)
##        self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)
        self.applySettings()
        self.fuzzyIcon = QtGui.QIcon("../images/fuzzy.png")
        self.noteIcon = QtGui.QIcon("../images/note.png")
        self.approvedIcon = QtGui.QIcon("../images/approved.png")
        self.blankIcon = QtGui.QIcon()
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        self.currentIndexActive = False
        self.indexMaxLen = 0
        self.units = []
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentIndex)
        self.connect(self.ui.tableOverview.model(), QtCore.SIGNAL("layoutChanged()"), self.layoutChanged)
        #self.connect(self.ui.tableOverview, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.emitTargetChanged)
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Overview' before closing Overview
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        
    def slotNewUnits(self, units):
        self.ui.tableOverview.setEnabled(bool(units))
        self.indexMaxLen = len(str(len(units)))
        self.setUpdatesEnabled(False)
        self.filter = World.filterAll
        self.units = []
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tableOverview.setSortingEnabled(False)
        for unit in units:
            self.addUnit(unit)
        self.ui.tableOverview.setSortingEnabled(True)
        self.setUpdatesEnabled(True)
        self.units = units

    def filteredList(self, shownList, filter):
        """show the items which are in shownList.
        @param shownList: list of unit which allow to be visible in the table.
        @param filter: shownList's filter."""
        if (filter != self.filter):
            hiddenList = range(self.ui.tableOverview.rowCount())
            for i in hiddenList:
                self.ui.tableOverview.hideRow(i)
            for unit in shownList:
                self.ui.tableOverview.showRow(unit.x_editor_index)
            self.filter = filter
        self.shownList = shownList
        self.ui.tableOverview.sortItems(0)
        self.ui.tableOverview.resizeRowsToContents()
        
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
        item.setFlags(self.normalState)
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
            self.currentIndexActive = True
            self.emit(QtCore.SIGNAL("currentIndex"), index)

    def updateView(self, unit):
        """highlight the table's row at index.
        @param unit: """
        atFirst = (self.ui.tableOverview.currentRow() == 0)
        atLast = (self.ui.tableOverview.currentRow() >= self.ui.tableOverview.rowCount() - 1)
        self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), atFirst, atLast)
        if (self.currentIndexActive == True):
            self.currentIndexActive = False
            return
        if (not unit):
            return
        row = self.ui.tableOverview.row(unit.x_editor_tableItem)
        self.markComment(row, unit.getnotes())
        self.markState(row, unit.x_editor_state)
        self.ui.tableOverview.selectRow(row)
        self.ui.tableOverview.scrollToItem(unit.x_editor_tableItem)
        #self.filterUnit(row, unit.x_editor_state)
        
    def filterUnit(self, index, state):
        if (not self.filter & state):
            self.ui.tableOverview.hideRow(index)
        
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
        row = self.ui.tableOverview.currentRow()
        item = self.ui.tableOverview.item(row, 2)
        item.setText(text)
        self.ui.tableOverview.resizeRowToContents(row)
        if (text):
            state = World.translated
        else:
            state = World.untranslated
        self.markState(row, state)

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
        
    def layoutChanged(self):
        for unit in self.units:
            if (unit.x_editor_tableItem):
                row = self.ui.tableOverview.row(unit.x_editor_tableItem)
                if (unit.x_editor_state & self.filter):
                    self.ui.tableOverview.showRow(row)
                else:
                    self.ui.tableOverview.hideRow(row)
        self.ui.tableOverview.resizeRowsToContents()

    def indexString(self, index):
        return str(index).rjust(self.indexMaxLen) + "  "
        
    def updateComment(self, text):
        """change the tooltip in index column, and add an icon if there is text.
        @param text: text to set as tooltip in index field."""
        row = self.ui.tableOverview.currentRow()
        self.markComment(row, text)
        
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
        currentRow = self.ui.tableOverview.currentRow()
        if currentRow > 0:
            for i in range(currentRow - 1, -1, -1):
                if (not self.ui.tableOverview.isRowHidden(i)):
                    currentRow = i
                    break
            self.ui.tableOverview.selectRow(currentRow)
        
    def scrollNext(self):
        """move to next row inside the table."""
        currentRow = self.ui.tableOverview.currentRow()
        rowCount = self.ui.tableOverview.rowCount()
        if currentRow < rowCount:
            for i in range(currentRow + 1, rowCount):
                if (not self.ui.tableOverview.isRowHidden(i)):
                    currentRow = i
                    break
            self.ui.tableOverview.selectRow(currentRow)
        
    def scrollFirst(self):
        """move to first row of the table."""
        self.ui.tableOverview.selectRow(0)
        
    def scrollLast(self):
        """move to last row of the table."""
        self.ui.tableOverview.selectRow(self.ui.tableOverview.rowCount() - 1)

if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock(None)
    overview.show()
    sys.exit(app.exec_())
