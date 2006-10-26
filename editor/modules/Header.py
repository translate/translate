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
                        
##    def getHeaderInfo(self, otherComments, header):
##        """slot for getting otherComments and header from doc then set to textbox"""
##        otherCommentsStr = " "
##        for i in range(len(otherComments)):
##            otherCommentsStr += otherComments[i].lstrip("# ")
##        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
##        #remember old settings
##        self.oldOtherComments = self.ui.txtOtherComments.toPlainText()
##        self.ui.txtHeader.setPlainText(unicode(header))
##            
    def showDialog(self, otherComments, header):
        """ make the dialog visible with otherComments and header filled in"""
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Header Editor"))
            self.setModal(True)                  
            
            self.ui = Ui_frmHeader()
            self.ui.setupUi(self)
            otherCommentsStr = " "
            for i in range(len(otherComments)):
                otherCommentsStr += otherComments[i].lstrip("# ")
            self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
            #remember old settings
            self.oldOtherComments = self.ui.txtOtherComments.toPlainText()
            self.ui.txtHeader.setPlainText(unicode(header))
            
            #connect signals
            QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accepted)
            QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
            QtCore.QObject.connect(self.ui.resetButton,QtCore.SIGNAL("clicked()"), self.reset)

        self.show()
        
    def reset(self):
        """Reset back the original header"""
        if self.ui.txtHeader.document().isModified():
            self.ui.txtHeader.setPlainText(self.oldHeader)
        if self.ui.txtOtherComments.document().isModified():
            self.ui.txtOtherComments.setPlainText(self.oldOtherComments)
        
    def applySettings(self):    
        """set user profile from Qsettings into the txtHeader, all infomation need filling in"""     
        userProfile = []
        userName = self.settings.value("UserName")        
        userProfile.append(userName.toString())        
        if (userName.isValid()):
            emailAddress = self.settings.value("EmailAddress")
            if (emailAddress.isValid()):
                FullLanguage = self.settings.value("FullLanguage")
                if (FullLanguage.isValid()):
                    Code = self.settings.value("Code")
                    if (Code.isValid()):
                        SupportTeam = self.settings.value("SupportTeam")
                        if (SupportTeam.isValid()):
                            TimeZone = self.settings.value("TimeZone")
                            if (TimeZone.isValid()):
##                                userProfile.append   
                                pass
        self.oldHeader = self.ui.txtHeader.toPlainText()
        self.ui.txtHeader.setPlainText(userProfile[0])
        self.ui.txtHeader.document().setModified(True)
        return userProfile

    def accepted(self):
        """add header to document"""
        userProfile = self.applySettings()           
##        userProfile = {"charset":"CHARSET", "encoding":"ENCODING", "project_id_version":None, "pot_creation_date":None, "po_revision_date":None, "last_translator":"hokkakada<hokkakada@khmeros.info", "language_team":"Khmer", "mime_version":None, "plural_forms":None, "report_msgid_bugs_to":None}
        self.emit(QtCore.SIGNAL("updateHeader"), userProfile)
        pass

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
