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
            self.setModal(True)
            self.connect(self.ui.btnClose, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
            self.connect(self.ui.btnPOfile, QtCore.SIGNAL("clicked(bool)"), self.setPOPath)
            self.connect(self.ui.btnTMXfile, QtCore.SIGNAL("clicked(bool)"), self.setTMXPath)
            self.connect(self.ui.btnXLiffFile, QtCore.SIGNAL("clicked(bool)"), self.setXliffPath)
            self.connect(self.ui.poLookup, QtCore.SIGNAL("stateChanged(int)"), self.setPOLookup)
            self.connect(self.ui.tmxLookup, QtCore.SIGNAL("stateChanged(int)"), self.setTMXLookup)
            self.connect(self.ui.xliffLookup, QtCore.SIGNAL("stateChanged(int)"), self.setXliffLookup)
        self.ui.linePOfile.setText(World.settings.value("PODictionary").toString())
        self.ui.lineTMXfile.setText(World.settings.value("TMXDictionary").toString())
        self.ui.lineXliffFile.setText(World.settings.value("XLIFFDictionary").toString())
        if (self.ui.linePOfile.text()):
            self.ui.poLookup.setChecked(True)
        if (self.ui.lineTMXfile.text()):
            self.ui.tmxLookup.setChecked(True)
        if (self.ui.lineXliffFile.text()):
            self.ui.xliffLookup.setChecked(True)
        self.show()
        
    def setPOPath(self):
        '''set path of translated PO file(s) '''
        path = QtGui.QFileDialog.getOpenFileName(
                         self,
                         "Select a PO file to set as dictionary",
                         QtCore.QDir.homePath(),
                         "PO file (*.po)")
        self.ui.linePOfile.setText(path)
        World.settings.setValue("PODictionary", QtCore.QVariant(path))

    def setTMXPath(self):
        '''set path of translated TMX file(s) '''
        path = QtGui.QFileDialog.getOpenFileName(
                         self,
                         "Select a TMX file to set as dictionary",
                         QtCore.QDir.homePath(),
                         "TMX file (*.tmx)")
        self.ui.lineTMXfile.setText(path)
        World.settings.setValue("TMXDictionary", QtCore.QVariant(path))
    
    def setXliffPath(self):
        '''set path of translated Xliff file(s) '''
        path = QtGui.QFileDialog.getOpenFileName(
                         self,
                         "Select a TMX file to set as dictionary",
                         QtCore.QDir.homePath(),
                         "Xliff file (*.xlf, *.xliff)")
        self.ui.lineTMXfile.setText(path)
        World.settings.setValue("XLIFFDictionary", QtCore.QVariant(path))
    
    def setPOLookup(self):
        World.settings.setValue("POLookup", QtCore.QVariant(self.ui.poLookup.isChecked()))
    
    def setTMXLookup(self):
        World.settings.setValue("TMXLookup", QtCore.QVariant(self.ui.tmxLookup.isChecked()))
    
    def setXliffLookup(self):
        World.settings.setValue("XLIFFLookup", QtCore.QVariant(self.ui.xliffLookup.isChecked()))
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = tmSetting(None)
    tm.showDialog()
    sys.exit(tm.exec_())

