#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on overview of source and target

import sys
from PyQt4 import QtCore, QtGui
from OverviewUI import Ui_Form

class OverviewDock(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Overview"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)        
        self.setWidget(self.form)                     
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowOverview")        
        self._actionShow.setText(self.tr("Hide Overview"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)
        
        # set column size
        self.ui.treeOverview.resizeColumnToContents(0)
        self.ui.treeOverview.header().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.treeOverview.header().setResizeMode(2, QtGui.QHeaderView.Stretch)

        self.lastItem = None
        self.id = None
        self.connect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)

    def closeEvent(self, event):            
        self._actionShow.setText(self.tr("Show Overview"))
        
    def actionShow(self):
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Overview"))    
        else:
            self._actionShow.setText(self.tr("Show Overview"))    
        self.setHidden(not self.isHidden())    

##    def getid(self, currentUnit):
##        """return id as integer.
##        If unit does not id, it return index of unit in list of units."""
##        try:
##            currentId = int(currentUnit.getid())
##            return currentId
##        except AttributeError:
##            return None

    def addItem(self, currentUnit, currentPointer):
        """Add one item to the list of source and target."""
        item = QtGui.QTreeWidgetItem(self.ui.treeOverview)
        self.items.append(item)
        #id = self.getid(currentUnit)
        #if (not id):
        #    id = currentPointer
        id = currentPointer
        item.setText(0, str(id))
        item.setText(1, currentUnit.source)
        item.setText(2, currentUnit.target)
        #item.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(id))
        
    def addItems(self, currentUnit, currentPointer):
        """Add an item or a list of items."""
        if isinstance(currentUnit, list):
            #for item in currentUnit:
            #    self.addItem(item, pointer)
            for i in range(len(currentUnit)):
                self.addItem(currentUnit[i], currentPointer[i])
        else:
            self.addItem(currentUnit)

    def slotNewUnits(self, units, unitsPointer):
        """Initialize the list, clear and fill with units"""
        if not units:
            self.ui.treeOverview.clear()
            return
        self.items = []
        self.ui.treeOverview.clear()
        self.addItems(units, unitsPointer)
        # select the first item in list
        self.ui.treeOverview.setCurrentItem(self.items[0])
    
    def updateItem(self, value):
        if (not self.items):
            return
        item = self.items[value]
        self.disconnect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)
        self.ui.treeOverview.setCurrentItem(item)
        self.connect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)
        
    def takeoutUnit(self, value):
        item = self.items[value]
        self.items.pop(value)
        self.ui.treeOverview.setItemHidden(item, True)

    def emitItemSelected(self):
        try:
            item = self.ui.treeOverview.selectedItems()[0]
        except IndexError:
            return
        self.id = int(item.text(0))
        ##self.id = item.data(0, QtCore.Qt.UserRole).toInt()[0]
        self.emit(QtCore.SIGNAL("itemSelected"), self.id)
        self.lastItem = item
        
    def setTarget(self, target):
        if (self.lastItem):
            self.lastItem.setText(2, target)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    overview = OverviewDock()
    overview.show()
    sys.exit(app.exec_())
