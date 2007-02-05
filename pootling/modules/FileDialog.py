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
# This module is providing a selecting-file/folder dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_FileDialog import Ui_Dialog

class fileDialog(QtGui.QDialog):
    """
    Code for choosing path of translation memory
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Choosing file or a directory")
        
        self.dir = QtGui.QDirModel()
        self.dir.setReadOnly(True)
        self.ui.treeView.setModel(self.dir)
        self.setModal(True)
        
        self.connect(self.ui.treeView, QtCore.SIGNAL("doubleClicked ( const QModelIndex &)"), self.addLocation)
        self.connect(self.ui.treeView, QtCore.SIGNAL("clicked ( const QModelIndex &)"), self.addLocation)
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.emitLocation)
        self.connect(self.ui.btnQuit, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
        
    def addLocation(self):
        self.ui.lineLocation.setText(self.dir.filePath(self.ui.treeView.currentIndex()))
    
    def emitLocation(self):
        self.emit(QtCore.SIGNAL("location"), self.ui.lineLocation.text())
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    filedialog = fileDialog(None)
    filedialog.show()
    sys.exit(filedialog.exec_())
    
