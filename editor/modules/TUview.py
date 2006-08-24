#!/usr/bin/python
# -*- coding: utf8 -*-

# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
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
        self._actionShow.setText(self.tr("Show Detail"))
        
    def actionShow(self):  
        return self._actionShow        
        
    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Detail"))    
        else:
            self._actionShow.setText(self.tr("Show Detail"))    
        self.setHidden(not self.isHidden())

    @QtCore.pyqtSignature("int")
    def emitScrollbarPosition(self, value):
        self.emit(QtCore.SIGNAL("scrollbarPosition"), value)

    def updateScrollbar(self, value):
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitScrollbarPosition)
        self.ui.fileScrollBar.setValue(value)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitScrollbarPosition)

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
        self.units = units
        self.ui.fileScrollBar.setMaximum(len(units) - 1)
        self.ui.fileScrollBar.setEnabled(True)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitScrollbarPosition)
        
    def updateTUview(self, currentUnit):
        """ Update TUview """
        self.ui.txtSource.setPlainText(currentUnit.source)
        self.ui.txtTarget.setPlainText(currentUnit.target)
    
    def checkModified(self):
        if self.ui.txtTarget.document().isModified():
            self.emit(QtCore.SIGNAL("targetChanged"), self.ui.txtTarget.toPlainText())   
            
    def source2target(self):
        """copy source to target"""
        self.ui.txtTarget.setPlainText(self.ui.txtSource.toPlainText())
        self.ui.txtTarget.document().setModified()
    
  
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = TUview()
    Form.show()
    sys.exit(app.exec_())
