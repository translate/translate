#!/usr/bin/python
# -*- coding: utf8 -*-

# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
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
#
# This module is working on source and target of current TU.

import sys
from PyQt4 import QtCore, QtGui
from TUviewUI import Ui_TUview

class TUview(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Detail"))
        self.form = QtGui.QWidget(self)        
        self.ui = Ui_TUview()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
                
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowDetail")        
        self._actionShow.setText(self.tr("Hide Detail"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)

    def closeEvent(self, event):
        """when close button is click, change caption to "Show Detail"""
        self._actionShow.setText(self.tr("Show Detail"))
        # FIXME you need to call the parents implementation here. Jens
        
    def actionShow(self):  
        return self._actionShow        
        
    def show(self):
        """toggle hide/show detail caption"""
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Detail"))    
        else:
            self._actionShow.setText(self.tr("Show Detail"))    
        self.setHidden(not self.isHidden())

    @QtCore.pyqtSignature("int")
    def emitCurrentId(self, value):
        id = self.ids[value]
        self.emit(QtCore.SIGNAL("currentId"), id)

    def highLightScrollbar(self, id):
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentId)
        value = self.ids.index(id)
        self.ui.fileScrollBar.setValue(value)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentId)

    def takeoutUnit(self, value):
        self.ui.fileScrollBar.setMaximum(self.ui.fileScrollBar.maximum() - 1)
        
    def slotNewUnits(self, units):
        """slot after new file was loaded"""
        if not units:
            self.ui.txtSource.setPlainText("")
            self.ui.txtTarget.setPlainText("")
            self.ui.fileScrollBar.setMaximum(0)
            return
        ## adjust the scrollbar
        self.ids = range(len(units))       
        self.ui.fileScrollBar.setMaximum(len(units) - 1)
        self.ui.fileScrollBar.setEnabled(True)
        self.ui.fileScrollBar.setSliderPosition(0)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentId)
    
    def filteredList(self, fList):
        # set maximum scrollbar value according to filter list
        self.ui.fileScrollBar.setMaximum(len(fList) - 1)
        self.ids = []
        for id in fList:
            self.ids.append(id)
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentId)
        self.ui.fileScrollBar.setValue(0)
        self.ui.fileScrollBar.setSliderPosition(0)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentId)
    
    def updateTUview(self, currentUnit):
        """ Update TUview """
        self.ui.txtSource.setPlainText(currentUnit.source)
        self.ui.txtTarget.setPlainText(currentUnit.target)
    
    def checkModified(self):
        if self.ui.txtTarget.document().isModified():
            self.emit(QtCore.SIGNAL("targetChanged"), self.ui.txtTarget.toPlainText())
            
    def source2target(self):
        """copy source to target"""
        self.ui.txtTarget.setFocus()
        self.ui.txtTarget.selectAll()
        self.ui.txtTarget.insertPlainText(self.ui.txtSource.toPlainText())
        self.ui.txtTarget.document().setModified()    

    def setHighLightSource(self, location):
        '''call setHighLight by passing source document and location (offset, length)'''                
        self.setHighLight(self.ui.txtSource.document(), location)
        
    def setHighLightTarget(self, location):
        '''call setHighLight by passing target document and location (offset, length)'''                
        self.setHighLight(self.ui.txtTarget.document(), location)
    
    def setHighLight(self, doc, location):
        '''HighLight on source or target depending on doc, and location (offset, and length)'''
        offsetindoc = location[0]
        length = location[1]        
        overrides = []        
        charformat = QtGui.QTextCharFormat()
        charformat.setFontWeight(QtGui.QFont.Bold)
        charformat.setForeground(QtCore.Qt.darkMagenta)                
        block = doc.findBlock(offsetindoc)        
        offsetinblock = offsetindoc - block.position()
        range = QtGui.QTextLayout.FormatRange()
        range.start = offsetinblock
        range.length = length
        range.format = charformat
        layout = block.layout()
        text = block.text()
        overrides.append(range)
        layout.setAdditionalFormats(overrides)
        block.document().markContentsDirty(block.position(), block.length())               
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = TUview()
    Form.show()
    sys.exit(app.exec_())
