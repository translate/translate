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

import time
import os
from PyQt4 import QtCore, QtGui
from ui.Ui_Header import Ui_frmHeader
import modules.World as World
from translate.storage import poheader

class Header(QtGui.QDialog):
    def __init__(self, parent, operator):
        QtGui.QDialog.__init__(self, parent)
        self.operator = operator
        QtCore.QObject.connect(self.operator, QtCore.SIGNAL("headerAuto"), self.updateOnSave)
        self.ui = None
        
    def setupUI(self):
        self.ui = Ui_frmHeader()
        self.ui.setupUi(self) 
        self.headerDic = {}
       
    def showDialog(self):
        """make the dialog visible
        """
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Header Editor"))
            self.setModal(True)
            self.setupUI()
            
            #connect signals
            QtCore.QObject.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"), self.accepted)
            QtCore.QObject.connect(self.ui.applyButton,QtCore.SIGNAL("clicked()"), self.applySettings)
            QtCore.QObject.connect(self.ui.resetButton,QtCore.SIGNAL("clicked()"), self.reset)
            QtCore.QObject.connect(self.ui.tableHeader,QtCore.SIGNAL("currentItemChanged(QTableWidgetItem *, QTableWidgetItem *)"), self.naviState)
            QtCore.QObject.connect(self.ui.btnUp,QtCore.SIGNAL("clicked()"), self.moveUp)
            QtCore.QObject.connect(self.ui.btnDown ,QtCore.SIGNAL("clicked()"), self.moveDown)
            QtCore.QObject.connect(self.ui.btnInsertRow,QtCore.SIGNAL("clicked()"), self.insertNewRow)
            QtCore.QObject.connect(self.ui.btnDeleteRow,QtCore.SIGNAL("clicked()"), self.deleteRow)
            QtCore.QObject.connect(self.ui.txtOtherComments, QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)
            
             # set up table appearance and behavior
            self.ui.tableHeader.clear()
            self.headerLabels = [self.tr("Key"), self.tr("Value")]
            self.ui.tableHeader.setHorizontalHeaderLabels(self.headerLabels)
            self.ui.tableHeader.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.ui.tableHeader.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.ui.tableHeader.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setHighlightSections(False)
            self.ui.tableHeader.setEnabled(True)
            self.ui.tableHeader.verticalHeader().hide()
        otherComments, self.headerDic = self.operator.headerData() 
##        self.headerDicForReset = self.headerDic
        if (self.headerDic):
            self.addItemToTable(self.headerDic)
            self.btnRMStat()
        otherCommentsStr = " "
        if (otherComments):
            for i in range(len(otherComments)):
                otherCommentsStr += otherComments[i].lstrip("#")
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        self.oldOtherComments = self.ui.txtOtherComments.toPlainText()
        self.show()
    def emitReadyForSave(self):
        self.emit(QtCore.SIGNAL("readyForSave"), True)
        
    def reset(self):
        """Reset back the original header"""
        self.addItemToTable(self.headerDic)
##        self.addItemToTable(self.headerDicForReset)
        self.ui.txtOtherComments.setPlainText(self.oldOtherComments)
        
    def moveItem(self, distance) :
        """ Move the selected item up or down
        @param distance is a difference for the current row"""
        
        table = self.ui.tableHeader
        currRow = table.currentRow()
        targetRow = currRow + distance
        if ((targetRow >= 0) and (targetRow < self.ui.tableHeader.rowCount())):
            # Swap between items
            for i in range(table.columnCount()):
                item = QtGui.QTableWidgetItem(table.item(currRow, i))
                table.setItem(currRow, i, QtGui.QTableWidgetItem(table.item(targetRow, i)))
                table.setItem(targetRow, i, item)
            table.setCurrentCell(targetRow, table.currentColumn())
                
    def moveUp(self):
        """ Move the selected item up"""
        self.moveItem(-1)
        
    def moveDown(self):
        """ Move the selected item down"""
        self.moveItem(+1)
        
    def insertNewRow(self):
        """ Insert a row befor the selected row """
        self.ui.btnDeleteRow.setEnabled(True)
        table = self.ui.tableHeader
        currRow = table.currentRow()
        table.insertRow(currRow)
        table.setItem(currRow, 0, QtGui.QTableWidgetItem())
        table.setItem(currRow, 1, QtGui.QTableWidgetItem())
        table.setCurrentCell(currRow, table.currentColumn())
        
    def deleteRow(self):
        """ Delete selected row"""
        self.btnRMStat()
        if (self.stat == False):
            return
        if (str(self.ui.tableHeader.item(self.ui.tableHeader.currentRow(), 0).text()) != ""):
            del self.headerDic[str(self.ui.tableHeader.item(self.ui.tableHeader.currentRow(), 0).text())]
        self.ui.tableHeader.removeRow(self.ui.tableHeader.currentRow())

    def btnRMStat(self):
        if (self.ui.tableHeader.rowCount() > 0 ):
            self.ui.btnDeleteRow.setEnabled(True)
            self.stat = True
        else:
            self.ui.btnDeleteRow.setEnabled(False)
            self.stat = False

    def naviState(self, current, previous):
        """ enabled/ disabled status of button moveup/ movedown"""
        currRow = self.ui.tableHeader.currentRow()
        rowCount = self.ui.tableHeader.rowCount()
        upEnabled = False
        downEnabled = False
        if (rowCount > 1):
            upEnabled = (currRow > 0)
            downEnabled = (currRow < rowCount - 1)
        self.ui.btnUp.setEnabled(upEnabled)
        self.ui.btnDown.setEnabled(downEnabled)
    
    def addItemToTable(self, headerDic):
        """ Add items to the table
        @ param headerDic: a dictionary of header information for putting in header table"""
        #rowCount according to the old headerDic length
        self.ui.tableHeader.setRowCount(len(headerDic))
        i = 0
        for key, value in headerDic.items():
            item0 = QtGui.QTableWidgetItem(QtCore.QString(key))
            item1 = QtGui.QTableWidgetItem(QtCore.QString(value))
            self.ui.tableHeader.setItem(i, 0, item0)
            self.ui.tableHeader.setItem(i, 1, item1)
            i += 1
     
    def applySettings(self):
        """set user profile from Qsettings into the tableHeader
             return a header as dictionary """
        userProfileDic = {}
        userName = World.settings.value("UserName", QtCore.QVariant(""))
        emailAddress = World.settings.value("EmailAddress", QtCore.QVariant(""))
        FullLanguage = World.settings.value("FullLanguage", QtCore.QVariant(""))
        Code = World.settings.value("Code", QtCore.QVariant(""))
        SupportTeam = World.settings.value("SupportTeam", QtCore.QVariant(""))
        TimeZone = World.settings.value("TimeZone", QtCore.QVariant(""))
        Last_Translator = userName.toString() + '<' + emailAddress.toString() + '>'
        Language_Team =  FullLanguage.toString() + '<' + SupportTeam.toString() + '>'
         #if header doesn't exist, call makeheader, otherwise, only update from setting
        #if there is no user profile 
        if (not isinstance(self.operator.store, poheader.poheader)):
            return
        header = self.operator.store.header()
        if not header:
            (path, fileName) = os.path.split(str(self.operator.fileName).lower())
            userProfileDic = {'charset':"CHARSET", 'encoding':"ENCODING", 'project_id_version': fileName, 'pot_creation_date':None, 'po_revision_date': False, 'last_translator': str(Last_Translator), 'language_team':str(Language_Team), 'mime_version':None, 'plural_forms':None, 'report_msgid_bugs_to':None}
            self.headerDic = self.operator.makeNewHeader(userProfileDic)
        else:
            self.headerDic['Language-Team'] = str(Language_Team)
            self.headerDic['Last-Translator'] = str(Last_Translator)
            self.headerDic['PO-Revision-Date'] = time.strftime("%Y-%m-%d %H:%M%z")
            self.headerDic['X-Generator'] = World.settingOrg + ' ' + World.settingApp + ' ' + World.settingVer
        if (len(self.headerDic) == 0):
            return
        if (self.ui): 
            self.addItemToTable(self.headerDic)
        return self.headerDic
    
    def updateOnSave(self):
        """ slot for headerAuto """
        otherComments, self.headerDic = self.operator.headerData()
        self.operator.updateNewHeader(otherComments, self.applySettings())
        
    def accepted(self):
        """send header information"""
        newHeaderDic = {}
        #set all the infomation into a dictionary
        for i in range(self.ui.tableHeader.rowCount()):
                newHeaderDic[str(self.ui.tableHeader.item(i, 0).text())] = str(self.ui.tableHeader.item(i,1).text())
        self.operator.updateNewHeader(self.ui.txtOtherComments.toPlainText(), newHeaderDic)
        
if __name__ == "__main__":
    import sys
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    from modules.Operator import Operator
    operatorObj = Operator()
    Header = Header(None, operatorObj)
    Header.showDialog()
    sys.exit(app.exec_())
