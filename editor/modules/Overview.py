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
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on overview of source and target

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_Overview import Ui_Form

class OverviewDock(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Overview"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)        
        self.setWidget(self.form)
        self.settings = QtCore.QSettings("WordForge", "Translation Editor")        
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowOverview")        
        self._actionShow.setText(self.tr("Hide Overview"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)
        
        # set up table appearance and behavior
        self.ui.tableOverview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableOverview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.tableOverview.horizontalHeader().setSortIndicatorShown(True)
        self.ui.tableOverview.resizeColumnToContents(0)
        self.ui.tableOverview.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.ui.tableOverview.horizontalHeader().setHighlightSections(False)        
        self.ui.tableOverview.verticalHeader().hide()
        
        
        self.headerFont = QtGui.QFont('Sans Serif', 10)
        self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)
        self.applySettings()

        # filter flags
        self.FUZZY = 2
        self.TRANSLATED = 4
        self.UNTRANSLATED = 8
        
        # colorize item
        self.DEFAULTCOLOR = QtGui.QColor(255,255,255,0)
        self.FUZZYCOLOR = QtGui.QColor(235,235,160,128)
        self.TRANSLATEDCOLOR = QtGui.QColor(190,255,165,128)
        self.UNTRANSLATEDCOLOR = QtGui.QColor(228,228,228,128)
        
        # idToUpdate holds the last item selected
        self.idToUpdate = None
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("cellChanged(int, int)"), self.emitTargetChanged)

    def actionShow(self):
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Overview"))    
        else:
            self._actionShow.setText(self.tr("Show Overview"))    
        self.setHidden(not self.isHidden())    

    def slotNewUnits(self, units):
        """Initialize the list, clear and fill with units."""
        self.ui.tableOverview.setEnabled(True)
        self.ui.tableOverview.clear()
        self.ui.tableOverview.setHorizontalHeaderLabels([self.tr("Index"), self.tr("Source"), self.tr("Target")])
        self.ui.tableOverview.setRowCount(len(units))
        i = 0
        normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
        for unit in units:
            item = QtGui.QTableWidgetItem(str(i).rjust(4) + '  ')
            item.setTextAlignment(QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter)
            item.setFlags(normalState)
            self.ui.tableOverview.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem(unit.source)
            item.setFlags(normalState)
            self.ui.tableOverview.setItem(i, 1, item)
            item = QtGui.QTableWidgetItem(unit.target)
            self.ui.tableOverview.setItem(i, 2, item)
            i += 1

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
   
    def highlightItem(self, id):
        """Highlight row according to id."""
        self.disconnect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentId)
        self.ui.tableOverview.selectRow(id)
        self.connect(self.ui.tableOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitCurrentId)
        self.idToUpdate = id

    def hideUnit(self, value):
        """Hide row at value."""
        self.ui.tableOverview.hideRow(value)

    def emitCurrentId(self):
        """Send ID according to selected row."""
        id = self.ui.tableOverview.currentRow()
        self.emit(QtCore.SIGNAL("currentId"), id)

    def emitTargetChanged(self):
        """Send target as string and signal targetChanged."""
        id = self.ui.tableOverview.currentRow()
        if (id >= 0):
            target = unicode(self.ui.tableOverview.item(id, 2).text())
            self.emit(QtCore.SIGNAL("targetChanged"), target)
        
    def updateTarget(self, target):
        """Update the text in target column."""
        item = QtGui.QTableWidgetItem(target)
        self.ui.tableOverview.setItem(self.idToUpdate, 2, item)
        
    def applySettings(self):
        font = self.settings.value("overviewFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.tableOverview.setFont(fontObj)
                self.ui.tableOverview.horizontalHeader().setFont(self.headerFont)
        
    def setColor(self, value, state):
        return
        item = self.ui.tableOverview.topLevelItem(value)
        if (state & self.FUZZY):
            color = self.FUZZYCOLOR
##        elif (state & self.TRANSLATED):
##            color = self.TRANSLATEDCOLOR
##        elif (state & self.UNTRANSLATED):
##            color = self.UNTRANSLATEDCOLOR
        else:
            color = self.DEFAULTCOLOR        
        if (item):
            item.setBackgroundColor(0, color)
            item.setBackgroundColor(1, color)
            item.setBackgroundColor(2, color)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock()
    overview.show()
    sys.exit(app.exec_())
