#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is providing an setting path of translation memory dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_tmSetting import Ui_tmsetting
from pootling.modules import World
from pootling.modules import FileDialog

class tmSetting(QtGui.QDialog):
    """
    Code for setting path of translation memory dialog
    
    @signal poLookup(1): emitted when poLookup checkbox is changed
    @signal tmxLookup(2): emitted when tmxLookup checkbox is changed
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.subscan = None
        
    def showDialog(self):
        #lazy init
        if (not self.ui):
            self.ui = Ui_tmsetting()
            self.ui.setupUi(self)
            self.setWindowTitle("Setting Translation Memory")
            self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.showFileDialog)
            self.filedialog = FileDialog.fileDialog(self)
            self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
            self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
            self.connect(self.ui.btnRemove, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
            self.connect(self.ui.btnRemoveAll, QtCore.SIGNAL("clicked(bool)"), self.ui.listWidget.clear)
            self.connect(self.ui.btnMoveUp, QtCore.SIGNAL("clicked(bool)"), self.moveItem)
            self.connect(self.ui.btnMoveDown, QtCore.SIGNAL("clicked(bool)"), self.moveItem)
        self.show()
    
    def showFileDialog(self):
        self.filedialog.show()
    
    def addLocation(self, text):
        self.ui.listWidget.addItem(text)
    
    def removeLocation(self):
        self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
    
    def moveItem(self):
        if (self.sender() == self.ui.btnMoveUp):
            print 'hello'
        elif (self.sender() == self.ui.btnMoveDown):
            print 'hi'
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = tmSetting(None)
    tm.showDialog()
    sys.exit(tm.exec_())

