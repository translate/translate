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
        #TODO: path history
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Choosing file or a directory")
        
        self.dir = QtGui.QDirModel()
        self.dir.setReadOnly(True)
        self.ui.treeView.setModel(self.dir)
        self.goHome()
        self.setModal(True)
        
        self.connect(self.ui.treeView, QtCore.SIGNAL("doubleClicked ( const QModelIndex &)"), self.addLocation)
        self.connect(self.ui.treeView, QtCore.SIGNAL("clicked ( const QModelIndex &)"), self.addLocation)
        self.connect(self.ui.btnHome, QtCore.SIGNAL("clicked(bool)"), self.goHome)
        self.connect(self.ui.btnDesktop, QtCore.SIGNAL("clicked(bool)"), self.goDesktop)
        self.connect(self.ui.btnDoc, QtCore.SIGNAL("clicked(bool)"), self.goDocument)
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.emitLocation)
        self.connect(self.ui.btnOK, QtCore.SIGNAL("clicked(bool)"), self.OK)
    
    def OK(self):
        self.emitLocation()
        self.close()
        
    def addLocation(self):
        self.ui.treeView.scrollTo(self.ui.treeView.currentIndex())
        self.ui.treeView.expand(self.ui.treeView.currentIndex())
        self.ui.treeView.resizeColumnToContents(0)
        self.ui.lineLocation.setText(self.dir.filePath(self.ui.treeView.currentIndex()))
    
    def emitLocation(self):
        self.emit(QtCore.SIGNAL("location"), self.ui.lineLocation.text())
    
    def goHome(self):
        self.ui.treeView.setCurrentIndex(self.dir.index(QtCore.QDir.homePath()))
        self.addLocation()
    
    def goDesktop(self):
        self.ui.treeView.setCurrentIndex(self.dir.index(QtCore.QDir.homePath() + '/Desktop'))
        self.addLocation()
    
    def goDocument(self):
        self.ui.treeView.setCurrentIndex(self.dir.index(QtCore.QDir.homePath() + '/Documents'))
        self.addLocation()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    filedialog = fileDialog(None)
    filedialog.show()
    sys.exit(filedialog.exec_())
    
