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
from ui.Ui_Header import Ui_frmHeader
from modules.Operator import Operator
from modules.World import World

class Header(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)        
        self.ui = None
        
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)

    def showDialog(self, otherComments, headerDic):
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
            
             # set up table appearance and behavior
        
            self.headerLabels = [self.tr("Key"), self.tr("Value")]            
            self.ui.tableHeader.setRowCount(10)
            self.ui.tableHeader.setHorizontalHeaderLabels(self.headerLabels)
            self.ui.tableHeader.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.ui.tableHeader.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.ui.tableHeader.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setHighlightSections(False)
            self.ui.tableHeader.setEnabled(True)
            self.headerDic = headerDic
            self.addOldItemToTable()
            
        otherCommentsStr = " "
        for i in range(len(otherComments)):
            otherCommentsStr += otherComments[i].lstrip("#")
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        self.oldOtherComments = self.ui.txtOtherComments.toPlainText()        
        self.show()
    
    def reset(self):
        """Reset back the original header"""                
        self.addOldItemToTable()
        
    def addOldItemToTable(self):
        """ Add old items to the table"""
        i = 0
        for key, value in self.headerDic.items():
            item0 = QtGui.QTableWidgetItem(QtCore.QString(key))   
            item1 = QtGui.QTableWidgetItem(QtCore.QString(value))   
            self.ui.tableHeader.setItem(i, 0, item0)
            self.ui.tableHeader.setItem(i, 1, item1)
            i += 1
        
    def applySettings(self):    
        """set user profile from Qsettings into the tableHeader, all information need filling in"""
        newHeaderDic = {}
        userName = self.settings.value("UserName", QtCore.QVariant(""))        
        emailAddress = self.settings.value("EmailAddress", QtCore.QVariant(""))
        FullLanguage = self.settings.value("FullLanguage", QtCore.QVariant(""))
        Code = self.settings.value("Code", QtCore.QVariant(""))
        SupportTeam = self.settings.value("SupportTeam", QtCore.QVariant(""))
        TimeZone = self.settings.value("TimeZone", QtCore.QVariant(""))
        
        Last_Translator = str(userName) + '<' + str(emailAddress) + '>'
        Language_Team =  str(FullLanguage) + '<' + str(SupportTeam) + '>'
        print type(str(Last_Translator))
        item0 = QtGui.QTableWidgetItem(QtCore.QString(Last_Translator))   
        item1 = QtGui.QTableWidgetItem(QtCore.QString(Language_Team)) 
        self.ui.tableHeader.setItem(5, 0, item0)
        self.ui.tableHeader.setItem(6, 1, item1)
        for i in range(self.ui.tableHeader.rowCount()):           
            newHeaderDic[self.ui.tableHeader.item(i,0).text()] = self.ui.tableHeader.item(i,1).text()
        return newHeaderDic

    def accepted(self):
        """send header information"""        
        self.emit(QtCore.SIGNAL("updateHeader"), self.ui.txtOtherComments.toPlainText(), self.applySettings())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
