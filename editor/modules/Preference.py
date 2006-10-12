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
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on Userprofile

import sys
from PyQt4 import QtCore, QtGui
from PreferenceUI import Ui_frmPreference

class Preference(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(self.tr("User Profile"))
        self.ui = Ui_frmPreference()
        self.ui.setupUi(self)  
        self.setModal(True)        

        #Personal Setting
        settings = QtCore.QSettings("WordForge", "Translation Editor")
        self.ui.UserName.setPlainText(settings.value("UserName").toString())
        self.ui.EmailAddress.setPlainText(settings.value("EmailAddress").toString())
        self.ui.FullLanguage.setPlainText(settings.value("FullLanguage").toString())
        self.ui.Code.setPlainText(settings.value("Code").toString())
        self.ui.SupportTeam.setPlainText(settings.value("SupportTeam").toString())
        self.ui.TimeZone.setPlainText(settings.value("TimeZone").toString())      
        
       #Font Setting
       
        self.connect(self.ui.bntOverview, QtCore.SIGNAL("clicked()"), self.fontOverview) 
        self.connect(self.ui.bntSource, QtCore.SIGNAL("clicked()"), self.fontSource) 
        self.connect(self.ui.bntTarget, QtCore.SIGNAL("clicked()"), self.fontTarget) 
        self.connect(self.ui.bntComment, QtCore.SIGNAL("clicked()"), self.fontComment) 
        
        self.connect(self.ui.okButton, QtCore.SIGNAL("clicked()"), self.accepted)
##self.operator.emitSetFont
##        if not profile.isEmpty():
##            profile = ""
##        self.ui.textEdit1.setPlainText(unicode(profile))
        # set font modify as false
        self.overviewFont = None
        self.tuSourceFont = None
        self.tuTargetFont = None
        self.commentFont = None
        
    def initFonts(self):
        # get font for display
        self.overviewFont, fontCaption = self.getFont("overview")
        self.ui.lblOverView.setText(fontCaption)
        self.tuSourceFont, fontCaption = self.getFont("tuSource")
        self.ui.lblSource.setText(fontCaption)
        self.tuTargetFont, fontCaption = self.getFont("tuTarget")
        self.ui.lblTarget.setText(fontCaption)
        self.commentFont, fontCaption = self.getFont("comment")
        self.ui.lblComment.setText(fontCaption)
        # call font changed
        self.emit(QtCore.SIGNAL("fontChanged"), "overview" , self.overviewFont)
        self.emit(QtCore.SIGNAL("fontChanged"), "tuSource" , self.tuSourceFont)
        self.emit(QtCore.SIGNAL("fontChanged"), "tuTarget" , self.tuTargetFont)
        self.emit(QtCore.SIGNAL("fontChanged"), "comment" , self.commentFont)
        # set font modify as false
        self.overviewFont = None
        self.tuSourceFont = None
        self.tuTargetFont = None
        self.commentFont = None
        
    def accepted(self):
        if (self.overviewFont):
            self.emit(QtCore.SIGNAL("fontChanged"), "overview" , self.overviewFont)
        if (self.tuSourceFont):
            self.emit(QtCore.SIGNAL("fontChanged"), "tuSource" , self.tuSourceFont)
        if (self.tuTargetFont):
            self.emit(QtCore.SIGNAL("fontChanged"), "tuTarget" , self.tuTargetFont)
        if (self.commentFont):
            self.emit(QtCore.SIGNAL("fontChanged"), "comment" , self.commentFont)
    
    def fontOverview(self):
        self.overviewFont, fontCaption = self.setFont("overview")
        self.ui.lblOverView.setText(fontCaption)
    def fontSource(self):
        self.tuSourceFont, fontCaption = self.setFont("tuSource")
        self.ui.lblSource.setText(fontCaption)
    def fontTarget(self):
        self.tuTargetFont, fontCaption = self.setFont("tuTarget")
        self.ui.lblTarget.setText(fontCaption)
    def fontComment(self):
        self.commentFont, fontCaption = self.setFont("comment")
        self.ui.lblComment.setText(fontCaption)
    
    def getFont(self, obj):
        """ return font family and size as list for each objects """
        settings = QtCore.QSettings("WordForge", "Translation Editor")
        fontFamily = settings.value(str(obj + "FontFamily")).toString()        
        fontSize = settings.value(str(obj + "FontSize")).toString()
        if (fontSize):
            fontSize = int(fontSize)
        else:
            fontSize = 10
        font = QtGui.QFont(fontFamily, fontSize)
        currentFont = fontFamily +",  "+ str(fontSize)
        return [font, currentFont]
    
    def setFont(self, obj):
        """set font to other widgets, return current font name and size"""
        #get font settings
        oldFont = self.getFont(obj)
        fontFamily = oldFont[0].family()
        fontSize = oldFont[0].pointSize()
        newFont = QtGui.QFontDialog.getFont(QtGui.QFont(fontFamily, fontSize))
        if (newFont[1]):
            fontFamily = newFont[0].family()
            fontSize = newFont[0].pointSize()
            # store font settings
            settings = QtCore.QSettings("WordForge", "Translation Editor")
            settings.setValue(str(obj + "FontFamily"), QtCore.QVariant(fontFamily))
            settings.setValue(str(obj + "FontSize"), QtCore.QVariant(fontSize))
            self.fontChanged = True
        currentFont = fontFamily +",  "+ str(fontSize)
        return [newFont[0], currentFont]

        
    def getText(self):        
        UserName = str(self.ui.UserName.toPlainText())
        EmailAddress = str(self.ui.EmailAddress.toPlainText())
        FullLanguage = str(self.ui.FullLanguage.toPlainText())
        Code = str(self.ui.Code.toPlainText())
        SupportTeam = str(self.ui.SupportTeam.toPlainText())
        TimeZone = str(self.ui.TimeZone.toPlainText())        
        
        settings = QtCore.QSettings("WordForge", "Translation Editor")
        settings.setValue("UserName",QtCore.QVariant(UserName))
        settings.setValue("EmailAddress",QtCore.QVariant(EmailAddress))
        settings.setValue("FullLanguage",QtCore.QVariant(FullLanguage))
        settings.setValue("Code",QtCore.QVariant(Code))
        settings.setValue("SupportTeam",QtCore.QVariant(SupportTeam))
        settings.setValue("TimeZone",QtCore.QVariant(TimeZone))
        
##        data = QtGui.QInputDialog.getText("QInputDialog.getText()"), self.tr("UserName:"),
##                                            self.tr("Your email address:"),
##                                            self.tr("Full Language Name:"),
##                                            self.tr("Language Code:"),
##                                            self.tr("Support Team:"),
##                                            self.tr("Time Zone:"), 
##                                            self.tr("Number of Singular/Plular Forms:"), QtGui.QLineEdit.Normal,
##                                            QtCore.QDir.home().dirName())
##        if datavaule and not text.isEmpty():
##            self.textLabel.setText(text)
##                self.emitUserprofile()
        
    def emitUserprofile(self, filename):
        self.store = factory.getobject(fileName)
        try:
            self.emit(QtCore.SIGNAL("fileName"),self.store.fileName())            
        except:
            pass               
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    user = Preference()
    user.show()
    sys.exit(app.exec_())        
