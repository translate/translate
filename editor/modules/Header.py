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
#
# This module is working on any Headers of current TU.

import sys
from PyQt4 import QtCore, QtGui
from HeaderUI import Ui_frmHeader
from modules.Operator import Operator

class Header(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(self.tr("Header Editor"))
        self.ui = Ui_frmHeader()
        self.ui.setupUi(self)
        self.setModal(True)
        QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QObject.connect(self.ui.cancelButton,QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
        
        
    def updateHeader(self, header):
        self.ui.txtHeader.setPlainText(unicode(header))
    
    def checkModified(self):
        if self.ui.txtHeader.document().isModified():
            self.emit(QtCore.SIGNAL("HeaderChanged"), self.ui.txtHeader.toPlainText())
            
    def applySettings(self):
        self.ui.txtHeader.setPlainText(unicode("header"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
