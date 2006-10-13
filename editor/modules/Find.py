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
        self.matchcase = False
        self.forward = True        
        self.setVisible(False)
        
        
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
   
        self.searchinsource = False
        self.searchintarget = False
        self.searchincomment = False   

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
        
        if self.ui.lineEdit.isModified():        
            self.emit(QtCore.SIGNAL("startSearch"), self.getOptions())
            self.ui.lineEdit.setModified(False)        
        
    def emitSeachInSource(self):        
        if (not self.checkBoxCheckedStatus()):
            self.ui.insource.setChecked(True)
            return
        if (self.ui.insource.isChecked()): 
            self.searchinsource = True
        else:
            self.searchinsource = False
            
    def emitSearchInTarget(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.intarget.setChecked(True)
            return
        if (self.ui.intarget.isChecked()): 
            self.searchintarget = True
        else:
            self.searchintarget = False
            
    def emitSeachInComment(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.incomment.setChecked(True)
            return
        if (self.ui.incomment.isChecked()): 
            self.searchincomment = True
        else:
            self.searchincomment = False
        
    def emitMatchCase(self):
        if (self.ui.matchcase.isChecked()): 
            self.matchcase = True
        else:
            self.matchcase = False
    
    def checkBoxCheckedStatus(self):
        if ((not self.ui.insource.isChecked()) and (not self.ui.intarget.isChecked()) and (not self.ui.incomment.isChecked())):
            ret = QtGui.QMessageBox.warning(self, self.tr("No Searching Location Selected"), 
                            self.tr("You have to specify at least one location to search in."), 
                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
            return False
        else:
            return True
    
    def findNext(self):            
        self.forward = True        
        self.emit(QtCore.SIGNAL("findNext"), self.getOptions())
        self.ui.lineEdit.setFocus()        
    
    def findPrevious(self):                
        self.forward = False        
        self.emit(QtCore.SIGNAL("findPrevious"), self.getOptions())    
        self.ui.lineEdit.setFocus()
    
    def getOptions(self):
        return [self.searchinsource, self.searchintarget, self.searchincomment, self.matchcase, self.forward, self.ui.lineEdit.text()]
    
    def showFind(self):
        self.ui.insource.setChecked(True)
        self.ui.insource.setEnabled(True)
        self.ui.incomment.setChecked(False)
        self.ui.intarget.setChecked(False)
        self.searchinsource = True
        self.searchintarget = False
        self.searchincomment = False
        self.ui.lineEdit_2.setEnabled(False)
        self.ui.replace.setEnabled(False)
        self.ui.replaceAll.setEnabled(False)
        if (not self.isVisible()):
            self.show()
    
    def showReplace(self):
        self.ui.incomment.setChecked(True)
        self.ui.insource.setChecked(False)        
        self.ui.intarget.setChecked(False)
        self.searchinsource = False
        self.searchincomment = True
        self.searchintarget = False
        self.ui.insource.setEnabled(False)
        self.ui.lineEdit_2.setEnabled(True)        
        self.ui.replace.setEnabled(False)
        self.ui.replaceAll.setEnabled(False)
        if (not self.isVisible()):
            self.show()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = Find()
    Form.show()
    sys.exit(app.exec_())
