#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
# 
# This module is working on Preferences

import sys
from PyQt4 import QtCore, QtGui
from ui.PreferenceUI import Ui_frmPreference
from modules.World import World

class Preference(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = None

        #Personal Setting
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)

    def initUI(self):
        """ get values and display them """
        self.overviewFont = self.getFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        self.tuSourceFont = self.getFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        self.tuTargetFont = self.getFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont )
        self.commentFont = self.getFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
        
        self.ui.UserName.setPlainText(self.settings.value("UserName").toString())
        self.ui.EmailAddress.setPlainText(self.settings.value("EmailAddress").toString())
        self.ui.cbxFullLanguage.setEditText(self.settings.value("FullLanguage").toString())
        self.ui.cbxLanguageCode.setEditText(self.settings.value("Code").toString())
        self.ui.SupportTeam.setPlainText(self.settings.value("SupportTeam").toString())
        self.ui.cbxTimeZone.setEditText(self.settings.value("TimeZone").toString())      

    def accepted(self):
        """ slot ok pressed """
        self.rememberFont(self.widget[0], self.overviewFont)
        self.rememberFont(self.widget[1], self.tuSourceFont)
        self.rememberFont(self.widget[2], self.tuTargetFont)
        self.rememberFont(self.widget[3], self.commentFont)

        self.settings.setValue("UserName", QtCore.QVariant(self.ui.UserName.toPlainText()))
        self.settings.setValue("EmailAddress", QtCore.QVariant(self.ui.EmailAddress.toPlainText()))
# TODO
##        self.settings.setValue("FullLanguage", QtCore.QVariant(self.ui.cbxFullLanguage.toPlainText()))
##        self.settings.setValue("Code", QtCore.QVariant(self.ui.Code.toPlainText()))
        self.settings.setValue("SupportTeam", QtCore.QVariant(self.ui.SupportTeam.toPlainText()))
##        self.settings.setValue("TimeZone", QtCore.QVariant(self.ui.TimeZone.toPlainText()))
        self.emit(QtCore.SIGNAL("settingsChanged"))
   
    def rememberFont(self, obj, fontObj):
        """input obj as string"""        
        # store font settings
        if (fontObj != None):    # TODO do we need this ???
            self.settings.setValue(str(obj + "Font"), QtCore.QVariant(fontObj.toString()))            
        
    def fontOverview(self):
        """ slot to open font selection dialog """
        self.overviewFont = self.setFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        
    def fontSource(self):
        """ slot to open font selection dialog """
        self.tuSourceFont = self.setFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        
    def fontTarget(self):
        """ slot to open font selection dialog """
        self.tuTargetFont = self.setFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont)
        
    def fontComment(self):
        """ slot to open font selection dialog """
        self.commentFont = self.setFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
    
    def getFont(self, obj):
        """ return font object created from settings"""
        font = self.settings.value(str(obj + "Font"), QtCore.QVariant(self.defaultFont.toString()))
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                return fontObj
        return self.defaultFont
    
    def defaultFonts(self):
        """slot Set default fonts"""
        self.setCaption(self.ui.lblOverView, self.defaultFont)
        self.overviewFont = self.defaultFont
        self.setCaption(self.ui.lblSource, self.defaultFont)
        self.tuSourceFont = self.defaultFont
        self.setCaption(self.ui.lblTarget, self.defaultFont)
        self.tuTargetFont = self.defaultFont
        self.setCaption(self.ui.lblComment, self.defaultFont)
        self.commentFont = self.defaultFont

        
    def setCaption(self, lable, fontObj):
        """ create the text from the font object and set the widget lable"""
        newText = fontObj.family() +",  "+ str(fontObj.pointSize())
        if (fontObj.bold()):
            newText.append(", " + self.tr("bold"))
        if (fontObj.italic()):
            newText.append(", " + self.tr("italic"))
        if (fontObj.underline()):
            newText.append(", " + self.tr("underline"))
        lable.setText(newText)
        
    def setFont(self, obj):
        """ open font dialog 
            return selected new font object or the old one if cancel was pressed """
        #get font settings
        oldFont = self.getFont(obj)
        newFont, okPressed = QtGui.QFontDialog.getFont(oldFont)
        if (okPressed):
            self.rememberFont(obj, newFont)
            return newFont
        return oldFont
      
    def showDialog(self):
        """ make the dialog visible """
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Preferences"))
            self.setModal(True)        
            self.defaultFont = QtGui.QFont("Serif", 10)
            self.ui = Ui_frmPreference()
            self.ui.setupUi(self)  
            # connect signals
            self.connect(self.ui.chkHeaderAuto, QtCore.SIGNAL("stateChanged(int)"), self.ui.chkHeaderAuto.checkState) 
            self.connect(self.ui.bntOverview, QtCore.SIGNAL("clicked()"), self.fontOverview) 
            self.connect(self.ui.bntSource, QtCore.SIGNAL("clicked()"), self.fontSource) 
            self.connect(self.ui.bntTarget, QtCore.SIGNAL("clicked()"), self.fontTarget) 
            self.connect(self.ui.bntComment, QtCore.SIGNAL("clicked()"), self.fontComment) 
            self.connect(self.ui.bntDefaults, QtCore.SIGNAL("clicked()"), self.defaultFonts) 
            self.connect(self.ui.okButton, QtCore.SIGNAL("clicked()"), self.accepted)
            self.widget = ["overview","tuSource","tuTarget","comment"]

        self.initUI()
        self.show()
        
##    def getUserProfile(self):  
##        """emit updateProfile signal and return userprofile as dictionary"""
##        UserName = str(self.ui.UserName.toPlainText())
##        EmailAddress = str(self.ui.EmailAddress.toPlainText())
####        FullLanguage = str(self.ui.FullLanguage.toPlainText())
##        Code = str(self.ui.Code.toPlainText())
##        SupportTeam = str(self.ui.SupportTeam.toPlainText())
##        TimeZone = str(self.ui.TimeZone.toPlainText())
##        
##        settings = QtCore.QSettings("WordForge", "Translation Editor")
##        settings.setValue("UserName",QtCore.QVariant(UserName))
##        settings.setValue("EmailAddress",QtCore.QVariant(EmailAddress))
##        settings.setValue("FullLanguage",QtCore.QVariant(FullLanguage))
##        settings.setValue("Code",QtCore.QVariant(Code))
##        settings.setValue("SupportTeam",QtCore.QVariant(SupportTeam))
##        settings.setValue("TimeZone",QtCore.QVariant(TimeZone))
        
##        userprofile = "UserName:" + UserName + "\nEmailAddress:" + EmailAddress + "\nFullLanguage:" + FullLanguage + "\nCode:" + Code + "\nSupportTeam:" + SupportTeam + "\nTimeZone:" + TimeZone +"\n"
##        userprofile = dictutils.cidict()
##        userprofile = {"charset":"CHARSET", "encoding":"ENCODING", "project_id_version":None, "pot_creation_date":None, "po_revision_date":None, "last_translator":UserName, "language_team":Code, "mime_version":None, "plural_forms":None, "report_msgid_bugs_to":SupportTeam}
##        userprofile = {"charset":"CHARSET", "encoding":"ENCODING", "project_id_version":None, "pot_creation_date":None, "po_revision_date":None, "last_translator":"Hok Kakada", "language_team":"Khmer", "mime_version":None, "plural_forms":None, "report_msgid_bugs_to": "support@khmeros.info"}
##        if (self.ui.chkHeaderAuto.checkState() == 2):
##            self.emit(QtCore.SIGNAL("headerAuto"), userprofile)
##        self.emit(QtCore.SIGNAL("storeProfile"), userprofile)
##        
##    def emitUserprofile(self, filename):
##        self.store = factory.getobject(fileName)
##        try:
##            self.emit(QtCore.SIGNAL("fileName"),self.store.fileName())            
##        except:
##            pass               
##        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    user = Preference()
    user.show()
    sys.exit(app.exec_())        
