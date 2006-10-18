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
from ui.HeaderUI import Ui_frmHeader
from modules.Operator import Operator

class Header(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(self.tr("Header Editor"))
        self.ui = Ui_frmHeader()
        self.ui.setupUi(self)
        self.setModal(True)
        
        QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accepted)
        QtCore.QObject.connect(self.ui.cancelButton,QtCore.SIGNAL("clicked()"), self.rejected)
        QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
        QtCore.QObject.connect(self.ui.resetButton,QtCore.SIGNAL("clicked()"), self.reset)
                        
    def updateOtherComments(self, otherComments):
        """slot for getting otherComments and set into txtOtherComments"""
        otherCommentsStr = " "
        for i in range(len(otherComments)):
            otherCommentsStr += otherComments[i]
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        
    def updateHeader(self, header):
        """slot for getting Header and set into txtHeader"""
##        settings = QtCore.QSettings("WordForge", "Translation Editor")
##        header = settings.value("OldHeader").toString()        
        self.ui.txtHeader.setPlainText(unicode(header))
    
    def checkModified(self):
        if self.ui.txtHeader.document().isModified():
            self.emit(QtCore.SIGNAL("HeaderChanged"), self.ui.txtHeader.toPlainText())
            
    def reset(self):
        """Reset back the original header"""
        if self.ui.txtHeader.document().isModified():
            self.ui.txtHeader.setPlainText(self.oldHeader)
        
    def applySettings(self):
        """set user profile from preference into the txtHeader"""
##        settings = QtCore.QSettings("WordForge", "Translation Editor")
##        self.headerString = settings.value("userProfile").toString()
        self.oldHeader = self.ui.txtHeader.toPlainText()
        self.updateHeader(self.userProfile)
        self.ui.txtHeader.document().setModified(True)       
    
    def updateProfile(self, userProfile):
        """receive userProfile from Preference as a dictionary and remember for other files"""
        self.userProfile = userProfile
##        settings = QtCore.QSettings("WordForge", "Translation Editor")
##        settings.setValue("userProfile", QtCore.QVariant(self.userProfile))

    def accepted(self):
        """add header to document"""
        self.emit(QtCore.SIGNAL("addHeader"), self.userProfile)
        
    def rejected(self):
        """noting changed if the cancel button is clicked """
        pass
##        self.emit(QtCore.SIGNAL("nothingChanged"), self.oldHeader)
##        settings = QtCore.QSettings("WordForge", "Translation Editor")
##        settings.setValue("OldHeader", QtCore.QVariant(self.oldHeader))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
