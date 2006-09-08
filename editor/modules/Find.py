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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)
#
# This module is working on source and target of current TU.

import sys
from PyQt4 import QtCore, QtGui
from FindUI import Ui_Form

class Find(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)        
        self.form = QtGui.QWidget(self)             
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)  
        self.setWidget(self.form)        
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowOverview")        
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)        
        self.connect(self.ui.findNext, QtCore.SIGNAL("clicked()"), self.findNext)
        self.connect(self.ui.findPrevious, QtCore.SIGNAL("clicked()"), self.findPrevious)        
        self.connect(self.ui.insource, QtCore.SIGNAL("stateChanged(int)"), self.emitSeachInSource)
        self.connect(self.ui.intarget, QtCore.SIGNAL("stateChanged(int)"), self.emitSearchInTarget)
        self.connect(self.ui.incomment, QtCore.SIGNAL("stateChanged(int)"), self.emitSeachInComment)
        self.connect(self.ui.matchcase, QtCore.SIGNAL("stateChanged(int)"), self.emitMatchCase)

    def actionShow(self):  
        return self._actionShow        
        
    def show(self):
        self.setHidden(not self.isHidden())                                     
    
    def keyReleaseEvent(self, event):                
        if (self.ui.lineEdit.text() != ''):
            self.ui.findNext.setEnabled(True)
            self.ui.findPrevious.setEnabled(True)            
        else:
            self.ui.findNext.setDisabled(True)
            self.ui.findPrevious.setDisabled(True)             
        self.emitSeachInSource()               
        self.emitSearchInTarget()      
        self.emitSeachInComment()                
        self.emitMatchCase()
        self.emit(QtCore.SIGNAL("textInputed"), self.ui.lineEdit.text())                   
        
    def emitSeachInSource(self):        
        if (not self.checkBoxCheckedStatus()):
            self.ui.insource.setChecked(True)
            return
        if (self.ui.insource.isChecked()):
            self.emit(QtCore.SIGNAL("seachInSource"), True)    
        else:
            self.emit(QtCore.SIGNAL("seachInSource"), False)    
    
    def emitSearchInTarget(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.intarget.setChecked(True)
            return
        if (self.ui.intarget.isChecked()):
            self.emit(QtCore.SIGNAL("seachInTarget"), True)    
        else:
            self.emit(QtCore.SIGNAL("seachInTarget"), False)    
    
    def emitSeachInComment(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.incomment.setChecked(True)
            return
        if (self.ui.incomment.isChecked()):
            self.emit(QtCore.SIGNAL("seachInComment"), True)    
        else:
            self.emit(QtCore.SIGNAL("seachInComment"), False)    
        
    def emitMatchCase(self):
        if (self.ui.matchcase.isChecked()):
            self.emit(QtCore.SIGNAL("matchCase"), True)    
        else:
            self.emit(QtCore.SIGNAL("matchCase"), False)    
    
    def checkBoxCheckedStatus(self):
        if ((not self.ui.insource.isChecked()) and (not self.ui.intarget.isChecked()) and (not self.ui.incomment.isChecked())):
            ret = QtGui.QMessageBox.warning(self, self.tr("No CheckBox Selected"), 
                            self.tr("You have to select at least one checkbox\n in order to search."), 
                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
            return False
        else:
            return True
    
    def findNext(self):        
        self.emit(QtCore.SIGNAL("findNext"), self.ui.lineEdit.text())
        self.ui.lineEdit.setFocus()
    
    def findPrevious(self):        
        self.emit(QtCore.SIGNAL("findPrevious"), self.ui.lineEdit.text())    
        self.ui.lineEdit.setFocus()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = Find()
    Form.show()
    sys.exit(app.exec_())
