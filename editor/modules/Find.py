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
from ui.Ui_Find import Ui_frmFind
import modules.World as World

class Find(QtGui.QDockWidget):
    # FIXME: comment this and list the signals
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Find"))
        self.ui = None
        
    def initUI(self):
        if (not self.ui):
            self.form = QtGui.QWidget(self)
            self.ui = Ui_frmFind()
            self.ui.setupUi(self.form)
            self.setWidget(self.form)
            self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
            self.matchcase = False
            self.forward = True
            self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
            
            self.connect(self.ui.findNext, QtCore.SIGNAL("clicked()"), self.findNext)
            self.connect(self.ui.findPrevious, QtCore.SIGNAL("clicked()"), self.findPrevious)
            self.connect(self.ui.replace, QtCore.SIGNAL("clicked()"), self.replace)
            self.connect(self.ui.replaceAll, QtCore.SIGNAL("clicked()"), self.replaceAll)
            self.connect(self.ui.insource, QtCore.SIGNAL("stateChanged(int)"), self.toggleSeachInSource)
            self.connect(self.ui.intarget, QtCore.SIGNAL("stateChanged(int)"), self.toggleSearchInTarget)
            self.connect(self.ui.incomment, QtCore.SIGNAL("stateChanged(int)"), self.toggleSeachInComment)
            self.connect(self.ui.matchcase, QtCore.SIGNAL("stateChanged(int)"), self.toggleMatchCase)
       
            self.searchinsource = []
            self.searchintarget = []
            self.searchincomment = []
            self.ui.findNext.setEnabled(False)
            self.ui.findPrevious.setEnabled(False)
            self.ui.insource.setChecked(True)
        
        self.ui.lineEdit.setEnabled(True)
        self.ui.lineEdit.setFocus()
        
    def keyReleaseEvent(self, event):
        if (self.ui.lineEdit.text() != ''):
            self.ui.findNext.setEnabled(True)
            self.ui.findPrevious.setEnabled(True)
        else:
            self.ui.findNext.setEnabled(False)
            self.ui.findPrevious.setEnabled(False)
        
        if self.ui.lineEdit.isModified():
            self.initSearch()
            self.emit(QtCore.SIGNAL("searchNext"))
            self.ui.lineEdit.setModified(False)
        
        if self.ui.lineEdit_2.isModified():
            self.ui.replace.setEnabled(True)
            self.ui.replaceAll.setEnabled(True)
    
    def initSearch(self):
        searchString = self.ui.lineEdit.text()
        filter = self.searchinsource + self.searchintarget + self.searchincomment
        if (filter):
            self.emit(QtCore.SIGNAL("initSearch"), searchString, filter, self.matchcase)
    
    def toggleSeachInSource(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.insource.setChecked(True)
            return
        if (self.ui.insource.isChecked()): 
            self.searchinsource = [World.source]
        else:
            self.searchinsource = []
        self.initSearch()
            
    def toggleSearchInTarget(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.intarget.setChecked(True)
            return
        if (self.ui.intarget.isChecked()): 
            self.searchintarget = [World.target]
        else:
            self.searchintarget = []
        self.initSearch()
            
    def toggleSeachInComment(self):
        if (not self.checkBoxCheckedStatus()):
            self.ui.incomment.setChecked(True)
            return
        if (self.ui.incomment.isChecked()): 
            self.searchincomment = [World.comment]
        else:
            self.searchincomment = []
        self.initSearch()
        
    def toggleMatchCase(self):
        if (self.ui.matchcase.isChecked()): 
            self.matchcase = True
        else:
            self.matchcase = False
        self.initSearch()
    
    def checkBoxCheckedStatus(self):
        '''It return False if there is no check box checked otherwise it will return True'''
        if ((not self.ui.insource.isChecked()) and \
            (not self.ui.intarget.isChecked()) and \
            (not self.ui.incomment.isChecked())):
            ret = QtGui.QMessageBox.warning(self, self.tr("No Searching Location Selected"), 
                self.tr("You have to specify at least one location to search in."), 
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
            return False
        else:
            return True
            
    def showFind(self):
        self.initUI()
        self.ui.insource.setEnabled(True)
        self.ui.insource.setChecked(True)
        self.ui.intarget.setChecked(False)
        self.ui.lineEdit_2.setHidden(True)
        self.ui.lblReplace.setHidden(True)
        self.ui.replace.setHidden(True)
        self.ui.replaceAll.setHidden(True)
        self.resize(self.width(), 15)
        self.setWindowTitle(self.tr("Find"))
        self.show()
        
    def showReplace(self):
        self.initUI()
        self.ui.lineEdit_2.setEnabled(True)
        self.ui.replace.setEnabled(False)
        self.ui.replaceAll.setEnabled(False)
        self.ui.lineEdit_2.setHidden(False)
        self.ui.lblReplace.setHidden(False)
        self.ui.replace.setHidden(False)
        self.ui.replaceAll.setHidden(False)
        self.ui.intarget.setChecked(True)
        self.ui.insource.setChecked(False)
        self.ui.insource.setEnabled(False)
        self.setWindowTitle(self.tr("Find-Replace"))
        self.show()

    def findNext(self):
        self.emit(QtCore.SIGNAL("searchNext"))
        self.ui.lineEdit.setFocus()
    
    def findPrevious(self):
        self.emit(QtCore.SIGNAL("searchPrevious"))
        self.ui.lineEdit.setFocus()
    
    def replace(self):
        self.emit(QtCore.SIGNAL("replace"), self.ui.lineEdit_2.text())
        self.ui.lineEdit_2.setFocus()
    
    def replaceAll(self):
        self.emit(QtCore.SIGNAL("replaceAll"), self.ui.lineEdit_2.text())
        self.ui.lineEdit_2.setFocus()
    
    def showEvent(self, event):
        QtGui.QDockWidget.showEvent(self, event)
        if (not self.ui):
            self.showFind()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = Find()
    Form.show()
    sys.exit(app.exec_())
