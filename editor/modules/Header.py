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
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on any Headers of current TU.

import sys
from PyQt4 import QtCore, QtGui
from ui.HeaderUI import Ui_frmHeader
from modules.Operator import Operator
from modules.World import World

class Header(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)        
        self.ui = None
        
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)

    def showDialog(self, otherComments, header):
        """ make the dialog visible with otherComments and header filled in"""
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Header Editor"))
            self.setModal(True)                  
            
            self.ui = Ui_frmHeader()
            self.ui.setupUi(self)           
            
            #connect signals
            QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accepted)
            QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
            QtCore.QObject.connect(self.ui.resetButton,QtCore.SIGNAL("clicked()"), self.reset)
        otherCommentsStr = " "
        for i in range(len(otherComments)):
            otherCommentsStr += otherComments[i].lstrip("# ")
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        #remember old settings
        self.oldOtherComments = self.ui.txtOtherComments.toPlainText()
        self.ui.txtHeader.setPlainText(unicode(header))
        self.show()
        
    def reset(self):
        """Reset back the original header"""
        if self.ui.txtHeader.document().isModified():
            self.ui.txtHeader.setPlainText(self.oldHeader)
        if self.ui.txtOtherComments.document().isModified():
            self.ui.txtOtherComments.setPlainText(self.oldOtherComments)
        
    def applySettings(self):    
        """set user profile from Qsettings into the txtHeader, all information need filling in"""     
        userProfile = []
        userName = self.settings.value("UserName")        
        if (userName.isValid()):
            userProfile.append(userName.toString())
            emailAddress = self.settings.value("EmailAddress")
            if (emailAddress.isValid()):
               userProfile.append(emailAddress.toString())
               FullLanguage = self.settings.value("FullLanguage")
               if (FullLanguage.isValid()):
                  userProfile.append(FullLanguage.toString())
                  Code = self.settings.value("Code")
                  if (Code.isValid()):
                      userProfile.append(Code.toString())
                      SupportTeam = self.settings.value("SupportTeam")
                      if (SupportTeam.isValid()):
                          userProfile.append(SupportTeam.toString())
                          TimeZone = self.settings.value("TimeZone")
                          if (TimeZone.isValid()):
                              userProfile.append(TimeZone.toString())
                              
        self.oldHeader = self.ui.txtHeader.toPlainText()
        header = 'Project-Id-Version:' + 'fileName' + \
        '\nPOT-Creation-Date: 2005-10-15 02:46+0200\n\
PO-Revision-Date: 2006-03-10 11:29+0700\n' + \
        'Last-Translator:' + userProfile[0] + '<' + userProfile[1] + '>' + \
        '\nLanguage-Team:' + userProfile[2]+ '<' + userProfile[4] + '>' +\
        '\nMIME-Version: 1.0\n\
Content-Type: text/plain; charset=UTF-8\n\
Content-Transfer-Encoding: 8bit\n\
X-Generator: KBabel 1.11\n'
 
        self.ui.txtHeader.setPlainText(header)
        self.ui.txtHeader.document().setModified(True)
        return userProfile

    def accepted(self):
        """send header information"""
        #header as list
        self.emit(QtCore.SIGNAL("updateHeader"), self.ui.txtOtherComments.toPlainText(), self.ui.txtHeader.toPlainText())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
