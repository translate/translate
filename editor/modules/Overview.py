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
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on overview of source and target

import sys
from PyQt4 import QtCore, QtGui
from ui.OverviewUI import Ui_Form

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
        
        # filter flags
        self.FUZZY = 2
        self.TRANSLATED = 4
        self.UNTRANSLATED = 8
        
        # colorize item
        self.DEFAULTCOLOR = QtGui.QColor(255,255,255,0)
        self.FUZZYCOLOR = QtGui.QColor(235,235,160,128)
        self.TRANSLATEDCOLOR = QtGui.QColor(190,255,165,128)
        self.UNTRANSLATEDCOLOR = QtGui.QColor(228,228,228,128)
        
        # TODO do you really need this, maybe it is enough to just use the current item? Jens
        self.lastItem = None
        self.connect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)

    def closeEvent(self, event):            
        self._actionShow.setText(self.tr("Show Overview"))
        # FIXME you need to call the parents implementation here. Jens
        
    def actionShow(self):
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Overview"))    
        else:
            self._actionShow.setText(self.tr("Show Overview"))    
        self.setHidden(not self.isHidden())    

    def slotNewUnits(self, units):
        """Initialize the list, clear and fill with units"""
        self.lastItem = None
        self.ui.treeOverview.clear()
        ids = range(len(units))
        items = []
        for i in ids:
            item = QtGui.QTreeWidgetItem()
            item.setTextAlignment(0, QtCore.Qt.AlignRight)
            # sorting needs leading space: '   1', '   2', '  10'.. rather than '1', '10', '2'
            item.setText(0, str(i).rjust(4) + '  ')
            item.setText(1, units[i].source)
            item.setText(2, units[i].target)
            # add item to children, in reverse mode because addTopLevelItems do the opposite
            items.insert(0,item)
            #items.append(item)
        # add children to tree widget
        self.ui.treeOverview.addTopLevelItems(items)

    def filteredList(self, fList):
        """ Show only items that are in filtered list """
        self.setUpdatesEnabled(False)
        j = 0
        numItems = self.ui.treeOverview.topLevelItemCount()
        for i in range(numItems):
            item = self.ui.treeOverview.topLevelItem(i)
            if (j < len(fList)) and (i == fList[j]):
                j += 1
                self.ui.treeOverview.setItemHidden(item, False)
            else:
                pass
                self.ui.treeOverview.setItemHidden(item, True)

        self.setUpdatesEnabled(True)

   
    def highLightItem(self, value):
        #print 'highLight',value
        numItems = self.ui.treeOverview.topLevelItemCount()
        if (not numItems) or (value < 0) or (value >= numItems):
            return
        item = self.ui.treeOverview.topLevelItem(value)
        if (self.lastItem != item):
            self.disconnect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)
            self.ui.treeOverview.setCurrentItem(item)
            self.connect(self.ui.treeOverview, QtCore.SIGNAL("itemSelectionChanged()"), self.emitItemSelected)
            self.lastItem = item
    
    def hideUnit(self, value):
        item = self.ui.treeOverview.topLevelItem(value)
        self.ui.treeOverview.setItemHidden(item, True)

    def emitItemSelected(self):
        try:
            item = self.ui.treeOverview.selectedItems()[0]
        except IndexError:
            return
        try:
            id = int(item.text(0))
            self.emit(QtCore.SIGNAL("currentId"), id)
        except:
            pass
        
    def setTarget(self, target):
        if (self.lastItem):
            self.lastItem.setText(2, target)
            
    def setFontOverView(self, font):
        self.ui.treeOverview.setFont(font)
        font = QtGui.QFont('serif', 9)
        self.ui.treeOverview.header().setFont(font)
        
    def setColor(self, value, state):
        item = self.ui.treeOverview.topLevelItem(value)
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
