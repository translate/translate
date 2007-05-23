#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
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
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on any Headers of current TU.

import time
import os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_Header import Ui_frmHeader
import pootling.modules.World as World
from translate.storage import poheader

import __version__

class Header(QtGui.QDialog):
    """Hold infomation of Header file.

    """
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
        """Make the dialog visible with header infomation fill in, if any.
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
            
             # set up table appearance and behavior
            self.headerLabels = [self.tr("Key"), self.tr("Value")]
            self.ui.tableHeader.setHorizontalHeaderLabels(self.headerLabels)
            self.ui.tableHeader.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.ui.tableHeader.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.ui.tableHeader.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            self.ui.tableHeader.horizontalHeader().setHighlightSections(False)
            self.ui.tableHeader.setEnabled(True)
            self.ui.tableHeader.verticalHeader().hide()
        self.ui.tableHeader.clear()
        self.ui.tableHeader.setRowCount(0)
        #Obtain header information from file
        otherComments, self.headerDic = self.operator.headerData()
        #remember for reset usage
        self.oldOtherComments = otherComments
        self.oldHeaderDic = self.headerDic
        
        if (self.headerDic):
            self.addItemToTable(self.headerDic)
            self.btnRMStat()
        
        if (self.ui.tableHeader.rowCount() != 0):
            self.ui.btnDown.setEnabled(True)
            self.ui.btnUp.setEnabled(True)
            self.ui.tableHeader.setCurrentCell(0,0)
        
        otherCommentsStr = " "
        if (otherComments):
            for i in range(len(otherComments)):
                # The "#" charactor is not important to show to translator  
                otherCommentsStr += otherComments[i].lstrip("#")
        self.ui.txtOtherComments.setPlainText(unicode(otherCommentsStr))
        self.show()
    
    def addItemToTable(self, headerDic):
        """Add items to the table.
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
        
    def reset(self):
        """Reset back the original header."""
        if (len(self.oldHeaderDic) != 0):
            self.addItemToTable(self.oldHeaderDic)
        self.ui.txtOtherComments.setPlainText(self.oldOtherComments)
        
    def moveItem(self, distance) :
        """ Move the selected item up or down.
        
        @param distance: A difference for the current row"""
        
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
        """Move the selected item up."""
        self.moveItem(-1)
        
    def moveDown(self):
        """Move the selected item down."""
        self.moveItem(+1)
        
    def insertNewRow(self):
        """Insert a row befor the selected row."""
        self.ui.btnDeleteRow.setEnabled(True)
        table = self.ui.tableHeader
        currRow = table.currentRow()
        table.insertRow(currRow)
        table.setItem(currRow, 0, QtGui.QTableWidgetItem())
        table.setItem(currRow, 1, QtGui.QTableWidgetItem())
        table.setCurrentCell(currRow, table.currentColumn())
        
    def deleteRow(self):
        """Delete selected row."""
        self.btnRMStat()
        if (self.stat == False):
            return
        self.ui.tableHeader.removeRow(self.ui.tableHeader.currentRow())

    def btnRMStat(self):
        """Enabled/disabled status to button DeleteRow."""
        if (self.ui.tableHeader.rowCount() > 0 ):
            self.ui.btnDeleteRow.setEnabled(True)
            self.stat = True
        else:
            self.ui.btnDeleteRow.setEnabled(False)
            self.stat = False

    def naviState(self, current, previous):
        """Enabled/ disabled status of button moveup/ movedown."""
        currRow = self.ui.tableHeader.currentRow()
        rowCount = self.ui.tableHeader.rowCount()
        upEnabled = False
        downEnabled = False
        if (rowCount > 1):
            upEnabled = (currRow > 0)
            downEnabled = (currRow < rowCount - 1)
        self.ui.btnUp.setEnabled(upEnabled)
        self.ui.btnDown.setEnabled(downEnabled)
    
    def applySettings(self):
        """Set user profile from Qsettings into the tableHeader.
        
            @return: Return a header as dictionary """
            
        userProfileDic = {} # a dictionary store info from preference
        
        userName = World.settings.value("UserName", QtCore.QVariant(""))
        emailAddress = World.settings.value("EmailAddress", QtCore.QVariant(""))
        FullLanguage = World.settings.value("FullLanguage", QtCore.QVariant(""))
        Code = World.settings.value("Code", QtCore.QVariant(""))
        SupportTeam = World.settings.value("SupportTeam", QtCore.QVariant(""))
        TimeZone = World.settings.value("TimeZone", QtCore.QVariant(""))
        if (emailAddress.toString() != ""):
            Last_Translator = userName.toString() + '<' + emailAddress.toString() + '>'
        else:
            Last_Translator = userName.toString()
        if (SupportTeam.toString() !=""):
            Language_Team =  FullLanguage.toString() + '<' + SupportTeam.toString() + '>'
        else:
            Language_Team =  FullLanguage.toString()
            
        nPlural = World.settings.value("nPlural", QtCore.QVariant(str(2)))
        pluralEquation = World.settings.value("equation", QtCore.QVariant(""))
        
        # test if it is a po or poxliff header.
        if (not isinstance(self.operator.store, poheader.poheader)):
            return
        header = self.operator.store.header()
        #if header doesn't exist, call makeheader, otherwise, only update from setting
        if not header:
            (path, fileName) = os.path.split(str(self.operator.fileName).lower())
            userProfileDic = {'charset':"CHARSET", 'encoding':"ENCODING", 'project_id_version': fileName, 'pot_creation_date':None, 'po_revision_date': False, 'last_translator': str(Last_Translator), 'language_team':str(Language_Team), 'mime_version':None, 'plural_forms':None, 'report_msgid_bugs_to':'translate-editor@lists.sourceforge.net'}
            self.headerDic = self.operator.makeNewHeader(userProfileDic)
        else:
            self.headerDic['Language-Team'] = str(Language_Team)
            self.headerDic['Last-Translator'] = str(Last_Translator)
            self.headerDic['PO-Revision-Date'] = time.strftime("%Y-%m-%d %H:%M%z")
            self.headerDic['Plural-Forms'] = 'nplurals=' + nPlural.toString() + '; plural=' + pluralEquation.toString() + ';'
            self.headerDic["Content-Type"] = "text/plain; charset=UTf-8"
            self.headerDic['X-Generator'] = World.settingApp + ' ' + __version__.ver
        #Plural form should be updated either the header is just created or it is already in the file.
        self.operator.store.updateheaderplural(int(nPlural.toString()), str(pluralEquation.toString()))
        
        #TODO: why do we need this?
        if (len(self.headerDic) == 0):
            return
        if (self.ui): 
            self.addItemToTable(self.headerDic)
        return self.headerDic
    
    def updateOnSave(self):
        """Slot for headerAuto."""
        otherComments, self.headerDic = self.operator.headerData()
        self.operator.updateNewHeader(otherComments, self.applySettings())
        
    def accepted(self):
        """send header information"""
        newHeaderDic = {} # a dictionary that hold all header infomation from header table.
        #set all the infomation into a dictionary
        for i in range(self.ui.tableHeader.rowCount()):
                newHeaderDic[str(self.ui.tableHeader.item(i, 0).text())] = str(self.ui.tableHeader.item(i,1).text())
        self.operator.updateNewHeader(self.ui.txtOtherComments.toPlainText(), newHeaderDic)
        
if __name__ == "__main__":
    import sys
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    from pootling.modules.Operator import Operator
    operatorObj = Operator()
    Header = Header(None, operatorObj)
    Header.showDialog()
    sys.exit(app.exec_())
