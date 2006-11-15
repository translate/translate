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
import time, os

class Header(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)        
        self.ui = None
        
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)
    
    def getFileName(self, fileName):
        (path, self.fileName) = os.path.split(str(fileName))
        
    def setupUI(self):
        self.ui = Ui_frmHeader()
        self.ui.setupUi(self) 
        self.headerDic = {}
       
    def showDialog(self, otherComments, headerDic):
        """ make the dialog visible with otherComments and header filled in"""
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Header Editor"))
            self.setModal(True)
            self.setupUI()
            
            #connect signals
            QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accepted)
            QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
            QtCore.QObject.connect(self.ui.resetButton,QtCore.SIGNAL("clicked()"), self.reset)
            QtCore.QObject.connect(self.ui.tableHeader, QtCore.SIGNAL("cellClicked(int, int)"), self.getRowCol)
            QtCore.QObject.connect(self.ui.tableHeader, QtCore.SIGNAL("cellClicked(int, int)"), self.appendRow)
            QtCore.QObject.connect(self.ui.btnUp,QtCore.SIGNAL("clicked()"), self.moveUp)
            QtCore.QObject.connect(self.ui.btnDown ,QtCore.SIGNAL("clicked()"), self.moveDown)
            QtCore.QObject.connect(self.ui.btnInsertRow,QtCore.SIGNAL("clicked()"), self.insertNewRow)
            QtCore.QObject.connect(self.ui.btnDeleteRow,QtCore.SIGNAL("clicked()"), self.DeleteRow)
            
             # set up table appearance and behavior        
            self.headerLabels = [self.tr("Key"), self.tr("Value")]            
            self.ui.tableHeader.setHorizontalHeaderLabels(self.headerLabels)
            self.ui.tableHeader.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.ui.tableHeader.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.ui.tableHeader.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setHighlightSections(False)
            self.ui.tableHeader.setEnabled(True)

            self.headerDic = headerDic
            self.addItemToTable()
            
        otherCommentsStr = " "
        for i in range(len(otherComments)):
            otherCommentsStr += otherComments[i].lstrip("#")
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        self.oldOtherComments = self.ui.txtOtherComments.toPlainText()        
        self.show()
    
    def reset(self):
        """Reset back the original header"""                
        self.addItemToTable(self.headerDic)
    
    def moveUp(self):
        """ Move the selected item up"""      
        # Swap between items
        self.ui.tableHeader.setItem(self.row-1, 0, self.selectedKey)
        self.ui.tableHeader.setItem(self.row-1, 1, self.selectedValue) 
        self.ui.tableHeader.setItem(self.row, 0, self.aboveSelectedKey)
        self.ui.tableHeader.setItem(self.row, 1, self.aboveSelectedValue)                  
        
    def moveDown(self):
        """ Move the selected item down"""
         # Swap between items
        self.ui.tableHeader.setItem(self.row, 0, self.underSelectedKey)
        self.ui.tableHeader.setItem(self.row, 1, self.underSelectedValue) 
        self.ui.tableHeader.setItem(self.row+1, 0, self.selectedKey)
        self.ui.tableHeader.setItem(self.row+1, 1, self.selectedValue)
        
    def insertNewRow(self):
        """ Insert a row befor the selected row """
        self.ui.tableHeader.insertRow(self.row)     
      
    def DeleteRow(self):
        """ Delete selected row"""
        self.ui.tableHeader.removeRow(self.row)
        
    def naviState(self):
        # if selected item is the first item, cannot move up
        if (self.row == 0):
            self.ui.btnUp.setEnabled(False)
            self.ui.btnDown.setEnabled(True)
        # if selected item is the last item, cannot move down
        elif(self.row == self.ui.tableHeader.rowCount() - 1):
            self.ui.btnDown.setEnabled(False)
            self.ui.btnUp.setEnabled(True)
        else:
            self.ui.btnUp.setEnabled(True)
            self.ui.btnDown.setEnabled(True)
    
    def rememberItems(self):
        """Remember selected item and item above selected item"""
        self.selectedKey = self.ui.tableHeader.takeItem(self.row, 0)
        self.selectedValue = self.ui.tableHeader.takeItem(self.row, 1)
        self.aboveSelectedKey = self.ui.tableHeader.takeItem(self.row-1, 0)
        self.aboveSelectedValue = self.ui.tableHeader.takeItem(self.row-1, 1)
        self.underSelectedKey = self.ui.tableHeader.takeItem(self.row+1, 0)
        self.underSelectedValue = self.ui.tableHeader.takeItem(self.row+1, 1)
        
    def getRowCol(self, row, col):
        """ slot for signals cellClicked  """
        self.row = row
        self.col = col
        self.naviState()
        self.rememberItems()          
          
    def appendRow(self):
        """ Append one row to the last"""
        lastRow = self.ui.tableHeader.rowCount() - 1
        if (self.row == lastRow):          
            self.ui.tableHeader.insertRow(lastRow)
        
    def addItemToTable(self, headerDic = None):
        """ Add old items to the table"""
        if (headerDic == None):
            headerDic = self.headerDic
        #rowCount according to the old headerDic length
        self.ui.tableHeader.setRowCount(len(headerDic) + 1)
        i = 0
        for key, value in headerDic.items():
            item0 = QtGui.QTableWidgetItem(QtCore.QString(key.lstrip('"')))   
            item1 = QtGui.QTableWidgetItem(QtCore.QString(value.rstrip('"')))   
            self.ui.tableHeader.setItem(i, 0, item0)
            self.ui.tableHeader.setItem(i, 1, item1)
            i += 1   
            
    def generatedHeader(self,generated_header):
        """ slot for headerGenerated"""
        self.generated_header = generated_header
        
    def applySettings(self):    
        """set user profile from Qsettings into the tableHeader"""
        newHeaderDic = {}
        userProfileDic = {}
        userName = self.settings.value("UserName", QtCore.QVariant(""))        
        emailAddress = self.settings.value("EmailAddress", QtCore.QVariant(""))
        FullLanguage = self.settings.value("FullLanguage", QtCore.QVariant(""))
        Code = self.settings.value("Code", QtCore.QVariant(""))
        SupportTeam = self.settings.value("SupportTeam", QtCore.QVariant(""))
        TimeZone = self.settings.value("TimeZone", QtCore.QVariant(""))        
        Last_Translator = userName.toString() + '<' + emailAddress.toString() + '>'        
        Language_Team =  FullLanguage.toString() + '<' + SupportTeam.toString() + '>'        
         #if header doesn't exist, call makeheader, otherwise, only update from setting
        #if there is no user profile 
        if (self.ui.tableHeader.rowCount() == 1):
            userProfileDic = {'charset':"CHARSET", 'encoding':"ENCODING", 'project_id_version': self.fileName, 'pot_creation_date':None, 'po_revision_date': False, 'last_translator': str(Last_Translator), 'language_team':str(Language_Team), 'mime_version':None, 'plural_forms':None, 'report_msgid_bugs_to':None}
            self.emit(QtCore.SIGNAL("makeHeader"), userProfileDic)
            userProfileDic = self.generated_header
        else:
            self.headerDic['Language-Team'] = str(Language_Team)
            self.headerDic['Last-Translator'] = str(Last_Translator)
            self.headerDic['PO-Revision-Date'] = time.strftime("%Y-%m-%d %H:%M%z")
            self.headerDic['X-Generator'] = "WordForge Translation Editor v.0.1"
            userProfileDic = self.headerDic
        self.addItemToTable(userProfileDic)       

        #set all the infomation into a dictionary
        for i in range(self.ui.tableHeader.rowCount()):   
            if (self.ui.tableHeader.item(i, 0) != None):                
                newHeaderDic[str(self.ui.tableHeader.item(i, 0).text())] = str(self.ui.tableHeader.item(i,1).text())
        return newHeaderDic     

    def accepted(self):
        """send header information"""        
        if (not self.ui):
            self.setupUI()
        self.emit(QtCore.SIGNAL("updateHeader"), self.ui.txtOtherComments.toPlainText(), self.applySettings())
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Header = Header()
    Header.show()
    sys.exit(app.exec_())
