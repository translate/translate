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
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on source and target of current TU.

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_Find import Ui_Form
from modules.World import World

class Find(QtGui.QDockWidget):
    # FIXME: comment this and list the signals

    def __init__(self):
        # FIXME: change this to lazy init so that the startup is faster
        QtGui.QDockWidget.__init__(self)        
        self.form = QtGui.QWidget(self)             
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)  
        self.setWidget(self.form)        
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)        
        self.matchcase = False
        self.forward = True        
        self.setVisible(False)
        
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.world = World()
        
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
   
        self.searchinsource = 0
        self.searchintarget = 0
        self.searchincomment = 0
        self.filter = 0
        self.ui.findNext.setEnabled(False)
        self.ui.findPrevious.setEnabled(False)
        self.ui.insource.setChecked(True)
        
    def actionShow(self):  
        return self._actionShow
        
    def show(self):
        self.setHidden(not self.isHidden())
    
    def keyReleaseEvent(self, event):                
        if (self.ui.lineEdit.text() != ''):
            self.ui.findNext.setEnabled(True)
            self.ui.findPrevious.setEnabled(True)            
        else:
            self.ui.findNext.setEnabled(False)
            self.ui.findPrevious.setEnabled(False)          
        
        if self.ui.lineEdit.isModified():        
            searchString = self.ui.lineEdit.text()
            self.emit(QtCore.SIGNAL("initSearch"), searchString, self.world.source, self.matchcase)
            #self.emit(QtCore.SIGNAL("searchString"), searchString, self.matchcase, self.world.searchStatic, self.filter)
            self.ui.lineEdit.setModified(False)        
        
    def emitSeachInSource(self):        
        if (not self.checkBoxCheckedStatus()):
            self.ui.insource.setChecked(True)
            return
        if (self.ui.insource.isChecked()): 
            self.searchinsource = self.world.source
        else:
            self.searchinsource = 0
        self.filter = self.searchinsource + self.searchintarget + self.searchincomment
            
    def emitSearchInTarget(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.intarget.setChecked(True)
            return
        if (self.ui.intarget.isChecked()): 
            self.searchintarget = self.world.target
        else:
            self.searchintarget = 0
        self.filter = self.searchinsource + self.searchintarget + self.searchincomment
            
    def emitSeachInComment(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.incomment.setChecked(True)
            return
        if (self.ui.incomment.isChecked()): 
            self.searchincomment = self.world.comment
        else:
            self.searchincomment = 0
        self.filter = self.searchinsource + self.searchintarget + self.searchincomment
        
    def emitMatchCase(self):
        if (self.ui.matchcase.isChecked()): 
            self.matchcase = True
        else:
            self.matchcase = False
    
    def checkBoxCheckedStatus(self):
        # FIXME: comment this there is a return value
        if ((not self.ui.insource.isChecked()) and \
            (not self.ui.intarget.isChecked()) and \
            (not self.ui.incomment.isChecked())):
            ret = QtGui.QMessageBox.warning(self, self.tr("No Searching Location Selected"), 
                self.tr("You have to specify at least one location to search in."), 
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
            return False
        else:
            return True
    
    def findNext(self):
        #searchStr = self.ui.lineEdit.text()
        self.emit(QtCore.SIGNAL("searchNext"))
        #self.emit(QtCore.SIGNAL("searchString"), searchStr, self.matchcase, self.world.searchForward, self.filter)
        self.ui.lineEdit.setFocus()
    
    def findPrevious(self):
        searchStr = self.ui.lineEdit.text()
        self.emit(QtCore.SIGNAL("searchPrevious"))
        #self.emit(QtCore.SIGNAL("searchString"), searchStr, self.matchcase, self.world.searchBackward, self.filter)
        self.ui.lineEdit.setFocus()
    
    def showFind(self):
        self.ui.lineEdit.setEnabled(True)
        self.ui.lineEdit_2.setEnabled(False)
        self.ui.replace.setEnabled(False)
        self.ui.replaceAll.setEnabled(False)
        self.ui.lineEdit.setFocus()
        if (not self.isVisible()):
            self.show()
    
    def showReplace(self):
        self.ui.lineEdit.setEnabled(True)
        self.ui.lineEdit_2.setEnabled(True)
        self.ui.replace.setEnabled(True)
        self.ui.replaceAll.setEnabled(True)
        self.ui.lineEdit.setFocus()
        if (not self.isVisible()):
            self.show()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = Find()
    Form.show()
    sys.exit(app.exec_())
