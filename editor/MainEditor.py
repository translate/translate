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
# of the License, or (at your option) any later version.http://rak3k.wordpress.com/
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

import sys
from PyQt4 import QtCore, QtGui
from modules.MainEditorUI import Ui_MainWindow
from modules.TUview import TUview
from modules.Overview import OverviewDock
from modules.Comment import CommentDock
from modules.Header import Header
from modules.Operator import Operator
from modules.FileAction import FileAction
from modules.Find import Find
from modules.Preference import Preference
from modules.AboutEditor import AboutEditor


class MainWindow(QtGui.QMainWindow):
    MaxRecentFiles = 10
    windowList = []

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)       
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)         
        self.resize(800, 600)        
        self.ui.recentaction = []
        self.createRecentAction()                
        #User must to fill your information
##        self.profile = UserProfile()              
##        if  self.profile == isNull():
##        if not self.profile.isEmpty():    
##            self.profile.show()             
##        else:
##            sys.exit(app.exec_())
            
        # create radio selection for menu filter
        filterGroup = QtGui.QActionGroup(self.ui.menuFilter)
        #filterGroup.setExclusive(False)
        self.ui.actionUnfiltered.setActionGroup(filterGroup)
        self.ui.actionFilterFuzzy.setActionGroup(filterGroup)
        self.ui.actionFilterTranslated.setActionGroup(filterGroup)
        self.ui.actionFilterUntranslated.setActionGroup(filterGroup)
        self.ui.actionUnfiltered.setCheckable(True)
        self.ui.actionFilterFuzzy.setCheckable(True)
        self.ui.actionFilterTranslated.setCheckable(True)
        self.ui.actionFilterUntranslated.setCheckable(True)
        self.ui.actionUnfiltered.setChecked(True)       
        
        # set disable
        self.ui.actionUnfiltered.setDisabled(True)
        self.ui.actionFilterFuzzy.setDisabled(True)
        self.ui.actionFilterTranslated.setDisabled(True)
        self.ui.actionFilterUntranslated.setDisabled(True)
        
        #plug in overview widget
        self.dockOverview = OverviewDock()        
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockOverview)        
        self.ui.menuViews.addAction(self.dockOverview.actionShow())        
        
        #plug in TUview widget
        self.dockTUview = TUview()                        
        self.setCentralWidget(self.dockTUview)
        self.ui.menuViews.addAction(self.dockTUview.actionShow())              
        
        #plug in comment widget
        self.dockComment = CommentDock()        
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockComment)
        self.ui.menuViews.addAction(self.dockComment.actionShow())                          

        #add widgets to statusbar
        #TODO: Decorate Status Bar

        self.statuslabel = QtGui.QLabel()
        self.searchlabel = QtGui.QLabel()        
        self.ui.statusbar.addWidget(self.statuslabel)
        self.ui.statusbar.addPermanentWidget(self.searchlabel)

        #create operator
        self.operator = Operator()                
        
        #Help menu of aboutQt        
        self.aboutDialog = AboutEditor()        
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog, QtCore.SLOT("show()"))
        self.connect(self.ui.actionAboutQT, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))     
        
        # create file action object and file action menu related signals
        self.fileaction = FileAction()        
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.connect(self.ui.actionOpenInNewWindow, QtCore.SIGNAL("triggered()"), self.startInNewWindow)
        self.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.fileaction.save)
        self.connect(self.ui.actionSaveas, QtCore.SIGNAL("triggered()"), self.fileaction.saveAs)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        
        # create Find widget and connect signals related to it        
        self.findBar = Find()      
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.findBar)              
        self.findBar.ui.lineEdit.setFocus()
        self.connect(self.ui.actionFind, QtCore.SIGNAL("triggered()"), self.findBar.showFind)        
        self.connect(self.ui.actionReplace, QtCore.SIGNAL("triggered()"), self.findBar.showReplace)        
        self.connect(self.findBar, QtCore.SIGNAL("startSearch"), self.operator.startSearch)
        self.connect(self.findBar, QtCore.SIGNAL("findNext"), self.operator.searchNext)
        self.connect(self.findBar, QtCore.SIGNAL("findPrevious"), self.operator.searchPrevious)
        
        # connect setHighLightSourcek setHighLightTarget, setHighLightComment by passing offset, and length
        self.connect(self.operator, QtCore.SIGNAL("foundInSource"), self.dockTUview.setHighLightSource)
        self.connect(self.operator, QtCore.SIGNAL("foundInTarget"), self.dockTUview.setHighLightTarget)
        self.connect(self.operator, QtCore.SIGNAL("foundInComment"), self.dockComment.setHighLightComment)
        self.connect(self.operator, QtCore.SIGNAL("clearHighLight"), self.dockComment.clearHighLight)
        self.connect(self.operator, QtCore.SIGNAL("clearHighLight"), self.dockTUview.clearHighLight)
        self.connect(self.operator, QtCore.SIGNAL("searchNotFound"), self.searchlabel.setText)        
    
        # Edit menu action
        self.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), self.undoer)
        self.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), self.redoer) 
##        self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), self.dockTUview.selectCut)
        
        self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), self.copier)
        self.connect(self.ui.actionPast, QtCore.SIGNAL("triggered()"), self.paster)   
        # Select All File
        self.connect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), self.selectAll)   
        
        # action Preferences menu 
        self.preference = Preference()
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL("triggered()"), self.preference,QtCore.SLOT("show()"))
        self.connect(self.preference, QtCore.SIGNAL("fontChanged"), self.fontChanged)
        self.preference.initFonts()
        
        
        # Other actions        
        self.connect(self.ui.actionNext, QtCore.SIGNAL("triggered()"), self.operator.next)
        self.connect(self.ui.actionPrevious, QtCore.SIGNAL("triggered()"), self.operator.previous)
        self.connect(self.ui.actionFirst, QtCore.SIGNAL("triggered()"), self.operator.first) 
        self.connect(self.ui.actionLast, QtCore.SIGNAL("triggered()"), self.operator.last)
        self.connect(self.ui.actionCopySource2Target, QtCore.SIGNAL("triggered()"), self.dockTUview.source2target)
        
        # Edit Header
        self.headerDialog = Header()        
        self.connect(self.ui.actionEdit_Header, QtCore.SIGNAL("triggered()"), self.headerDialog, QtCore.SLOT("show()"))
        
        # action filter menu
        self.connect(self.ui.actionUnfiltered, QtCore.SIGNAL("triggered()"), self.operator.unfiltered)
        self.connect(self.ui.actionFilterFuzzy, QtCore.SIGNAL("triggered()"), self.operator.filterFuzzy)
        self.connect(self.ui.actionFilterTranslated, QtCore.SIGNAL("triggered()"), self.operator.filterTranslated)
        self.connect(self.ui.actionFilterUntranslated, QtCore.SIGNAL("triggered()"), self.operator.filterUntranslated)        
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)
        
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateTUview)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateComment)
        self.connect(self.operator, QtCore.SIGNAL("header"), self.headerDialog.updateHeader)  
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.operator.emitHeader)
        
        self.connect(self.operator, QtCore.SIGNAL("hideUnit"), self.dockOverview.hideUnit)
        self.connect(self.operator, QtCore.SIGNAL("hideUnit"), self.dockTUview.hideUnit)
        
        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockOverview.highLightItem)
        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockTUview.highLightScrollbar)
        self.connect(self.dockTUview, QtCore.SIGNAL("currentId"), self.operator.setCurrentUnit)
        self.connect(self.dockOverview, QtCore.SIGNAL("currentId"), self.operator.setCurrentUnit)
        self.connect(self.dockOverview, QtCore.SIGNAL("currentId"), self.dockTUview.ui.txtTarget.setFocus)

##        self.connect(self.operator, QtCore.SIGNAL("changetarget"), self.dockTUview.txtClear)
        
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockTUview.checkModified)
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockComment.checkModified)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.dockOverview.setTarget)           
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.operator.saveStoreToFile)        
        self.connect(self.operator, QtCore.SIGNAL("savedAlready"), self.ui.actionSave.setEnabled)
        self.connect(self.dockTUview, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)     
        self.connect(self.dockComment, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)     

        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.setTitle)
        self.connect(self.operator, QtCore.SIGNAL("toggleFirstLastUnit"), self.toggleFirstLastUnit)

        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockTUview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockOverview.filteredList)
        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockTUview.filteredList)
        
        # set file status information to text label of status bar
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.statuslabel.setText)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.setOpening)        
       
    def cutter(self):
        object = self.focusWidget()
        object = self.isEnabled(bool)
        try:
            object.cut()
        except AttributeError:
            pass
        
    def copier(self):
        object = self.focusWidget()
        try:
            object.copy()
        except AttributeError:
            pass
    
    def paster(self):
        object = self.focusWidget()
        object.paste()
        
    def redoer(self):       
        object = self.focusWidget()
        try:
            object.document().redo()
        except AttributeError:
            pass
        
    def undoer(self):
        object = self.focusWidget()
        try:
            object.document().undo()
        except AttributeError:
            pass    
        
    def selectAll(self):
        object = self.focusWidget()
        try:
            object.selectAll()
        except AttributeError:
            pass       

    def setOpening(self, fileName):        
        self.setTitle(fileName)
        self.operator.getUnits(fileName)          
        self.ui.actionSave.setEnabled(False)  
        self.ui.actionSaveas.setEnabled(True)
        self.ui.actionUndo.setEnabled(True)
        self.ui.actionRedo.setEnabled(True)

        self.ui.actionPast.setEnabled(True)
        self.ui.actionSelectAll.setEnabled(True)
        self.ui.actionFind.setEnabled(True)
        self.ui.actionReplace.setEnabled(True)
        # FIXME what will happen if the file only contains 1 TU? Jens
        settings = QtCore.QSettings("WordForge", "Translation Editor")
        files = settings.value("recentFileList").toStringList()
        files.removeAll(fileName)        
        files.prepend(fileName)
        while files.count() > MainWindow.MaxRecentFiles:
            files.removeLast()
        settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction() 
        
        self.ui.actionUnfiltered.setEnabled(True)
        self.ui.actionFilterFuzzy.setEnabled(True)
        self.ui.actionFilterTranslated.setEnabled(True)
        self.ui.actionFilterUntranslated.setEnabled(True)
        self.ui.actionUnfiltered.setChecked(True)
        
    def startRecentAction(self):
        action = self.sender()
        if action:                
            self.fileaction.setFileName(action.data().toString())

    def createRecentAction(self):
        for i in range(MainWindow.MaxRecentFiles):
            self.ui.recentaction.append(QtGui.QAction(self))
            self.ui.recentaction[i].setVisible(False)
            self.connect(self.ui.recentaction[i], QtCore.SIGNAL("triggered()"), self.startRecentAction)
            self.ui.menuOpen_Recent.addAction(self.ui.recentaction[i])
        self.updateRecentAction()                  
    
    def updateRecentAction(self):        
        settings = QtCore.QSettings("WordForge", "Translation Editor")
        files = settings.value("recentFileList").toStringList()
        numRecentFiles = min(files.count(), MainWindow.MaxRecentFiles)             

        for i in range(numRecentFiles):
            # FIXME make sure that the text does not get too long. Jens
            self.ui.recentaction[i].setText(files[i])          
            self.ui.recentaction[i].setData(QtCore.QVariant(files[i]))              
            self.ui.recentaction[i].setVisible(True)
        
        for j in range(numRecentFiles, MainWindow.MaxRecentFiles):
            self.ui.recentaction[j].setVisible(False)
    
    def closeEvent(self, event):
        if self.operator.modified():  
            if self.fileaction.aboutToClose(self):
                event.accept()
            else:
                event.ignore()
           
    def setTitle(self, title):
        shownName = QtCore.QFileInfo(title).fileName()
        self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(self.tr("Translation Editor")))        
    
    def disableUndo(self):
        self.ui.actionUndo.setVisible(True)
        
    def enableUndo(self):
        self.ui.actionUndo.setEnabled(True)    
    
    def toggleFirstLastUnit(self, boolFirst, boolLast):
        """ set enable/disable first, previous, next, and last unit buttons """
        # disable first and previous unit buttons
        self.ui.actionFirst.setEnabled(boolFirst)
        self.ui.actionPrevious.setEnabled(boolFirst)
        self.ui.actionNext.setEnabled(boolLast)
        self.ui.actionLast.setEnabled(boolLast)
    
##    def setEnabledSave(self, bool):
##        self.ui.actionSave.setEnabled(bool)
    
    def fontChanged(self, obj, font):
        if (obj == "overview"):
            self.dockOverview.setFontOverView(font)
        elif (obj == "tuSource"):
            self.dockTUview.setFontSource(font)
        elif (obj == "tuTarget"):
            self.dockTUview.setFontTarget(font)
        elif (obj == "comment"):
            self.dockComment.setFontComment(font)

    
    def disableAll(self):
        self.ui.actionFirst.setDisabled(True)
        self.ui.actionPrevious.setDisabled(True)
        self.ui.actionNext.setDisabled(True)
        self.ui.actionLast.setDisabled(True)

    def startInNewWindow(self):        
        other = MainWindow()
        MainWindow.windowList.append(other) 
        if other.fileaction.openFile():
            other.show()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec_())
