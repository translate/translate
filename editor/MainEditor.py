
#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
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
# This module is working on the main windows of Editor

import sys
import os.path

## add a modules path in sys.path so the other module inside it is known during import
sys.path.append(os.path.join(sys.path[0] ,"modules"))

from PyQt4 import QtCore, QtGui
from modules.MainEditorUI import Ui_MainWindow
##from translate.storage import factory
from modules.TUview import TUview
from modules.Overview import OverviewDock
from modules.Comment import CommentDock
from modules.Operator import Operator
from modules.FileAction import FileAction
from modules.Find import Find
from modules.AboutEditor import AboutEditor

class MainWindow(QtGui.QMainWindow):
    MaxRecentFiles = 10
    windowList = []
##    self.dockTUview, self.dockComment = QtGui.QTextEdit()
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)       
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)         
        self.resize(800, 600)        
        self.ui.recentaction = []
        self.createRecentAction()                

        self.filter = None
        
        # create radio selection for menu filter
        filterGroup = QtGui.QActionGroup(self.ui.menuFilter)
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
        self.ui.menuToolView.addAction(self.dockOverview.actionShow())        
        
        #plug in TUview widget
        self.dockTUview = TUview()                        
        self.setCentralWidget(self.dockTUview)
        self.ui.menuToolView.addAction(self.dockTUview.actionShow())              
        
        #plug in comment widget
        self.dockComment = CommentDock()        
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockComment)
        self.ui.menuToolView.addAction(self.dockComment.actionShow())                          

        #create Find widget
        self.find = Find()        
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.find)        
        self.find.setVisible(False)      

        #add widgets to statusbar
        #TODO: Decorate Status Bar
        self.statuslabel = QtGui.QLabel()        
        self.ui.statusbar.addWidget(self.statuslabel)                

        #create operator
        self.operator = Operator()        
        
        # fileaction object of File menu
        self.fileaction = FileAction()
        #Help menu of aboutQt        
        self.aboutDialog = AboutEditor()        
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog, QtCore.SLOT("show()"))
        self.connect(self.ui.actionAboutQT, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
     
        
        # File menu action                
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.connect(self.ui.actionOpenInNewWindow, QtCore.SIGNAL("triggered()"), self.StartInNewWindow)
        self.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.fileaction.save)
        self.connect(self.ui.actionSaveas, QtCore.SIGNAL("triggered()"), self.fileaction.saveAs)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        self.connect(self.ui.actionFind, QtCore.SIGNAL("triggered()"), self.showFindBar)        
        
        # Edit menu action
        self.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), self.undoer)
        self.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), self.redoer) 
        self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), self.cutter)
        self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), self.copier)
        self.connect(self.ui.actionPast, QtCore.SIGNAL("triggered()"), self.paster)                
        
        # Other actions        
        self.connect(self.ui.actionNext, QtCore.SIGNAL("triggered()"), self.operator.next)
        self.connect(self.ui.actionPrevious, QtCore.SIGNAL("triggered()"), self.operator.previous)
        self.connect(self.ui.actionFirst, QtCore.SIGNAL("triggered()"), self.operator.first)        
        self.connect(self.ui.actionLast, QtCore.SIGNAL("triggered()"), self.operator.last)
        self.connect(self.ui.actionCopySource2Target, QtCore.SIGNAL("triggered()"), self.dockTUview.source2target)

        # action filter menu
        self.connect(self.ui.actionUnfiltered, QtCore.SIGNAL("triggered()"), self.unfiltered)
        self.connect(self.ui.actionFilterFuzzy, QtCore.SIGNAL("triggered()"), self.filterFuzzy)
        self.connect(self.ui.actionFilterTranslated, QtCore.SIGNAL("triggered()"), self.filterTranslated)
        self.connect(self.ui.actionFilterUntranslated, QtCore.SIGNAL("triggered()"), self.filterUntranslated)        
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)
        
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateTUview)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateComment)        

        self.connect(self.operator, QtCore.SIGNAL("takeoutUnit"), self.takeoutUnit)
        
        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockOverview.updateItem)
        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockTUview.updateScrollbar)
        self.connect(self.dockTUview, QtCore.SIGNAL("scrollbarPosition"), self.operator.setCurrentPosition)
        self.connect(self.dockOverview, QtCore.SIGNAL("itemSelected"), self.operator.setCurrentUnit)

##        self.connect(self.operator, QtCore.SIGNAL("changetarget"), self.dockTUview.txtClear)
        
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockTUview.checkModified)
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockComment.checkModified)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.dockOverview.setTarget)
        
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.operator.saveStoreToFile)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.setTitle)
        self.connect(self.operator, QtCore.SIGNAL("firstUnit"), self.disableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("firstUnit"), self.enableNextLast)
        self.connect(self.operator, QtCore.SIGNAL("lastUnit"), self.enableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("lastUnit"), self.disableNextLast)
        self.connect(self.operator, QtCore.SIGNAL("middleUnit"), self.enableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("middleUnit"), self.enableNextLast)        
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockTUview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("noUnit"), self.disableAll)
        
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.showCurrentStatus)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.setOpening)  
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.showCurrentStatus)       
    
       
    def unfiltered(self):
        self.filter = None
        self.operator.emitNewUnits()    

    def filterFuzzy(self):
        self.filter = 'fuzzy'
        self.operator.emitFilteredUnits(self.filter)
    
    def filterTranslated(self):
        self.filter = 'translated'
        self.operator.emitFilteredUnits(self.filter)
    
    def filterUntranslated(self):
        self.filter = 'untranslated'
        self.operator.emitFilteredUnits(self.filter)
    
    def takeoutUnit(self, value):
        if (self.filter):
            self.dockOverview.takeoutUnit(value)
            self.dockTUview.takeoutUnit(value)
            self.operator.takeoutUnit(value)
    
    def objectAvailable(self):
        if self.dockTUview.ui.txtTarget.hasFocus():
            return self.dockTUview.ui.txtTarget
        elif self.dockTUview.ui.txtSource.hasFocus():
            return self.dockTUview.ui.txtSource
        elif self.dockComment.ui.txtComment.hasFocus():
            return self.dockComment.ui.txtComment
        else:
            return
        
    def cutter(self):
        object = self.objectAvailable()
        self.operator.cutEdit(object)
        if self.dockTUview.ui.txtTarget ==None:
            print "ssd"
        
    def copier(self):
        object = self.objectAvailable()
        self.operator.copyEdit(object)
            
    def paster(self):
        try:
            object = self.objectAvailable()
            object.paste()
        except AttributeError:
            pass
        
    def redoer(self):
        object = self.objectAvailable()
        self.operator.redoEdit(object)
        
    def undoer(self):
        object = self.objectAvailable()
        self.operator.undoEdit(object)
    
    def showCurrentStatus(self, status):
        self.statuslabel.setText(' ' + status + ' ')

    def setOpening(self, fileName):        
        self.setTitle(fileName)
        self.operator.getUnits(fileName)            
        self.ui.actionSave.setEnabled(True)         # enable Save and Saveas action after opening file
        self.ui.actionSaveas.setEnabled(True)
        self.ui.actionUndo.setEnabled(True)
        self.ui.actionRedo.setEnabled(True)
        self.ui.actionCut.setEnabled(True)
        self.ui.actionCopy.setEnabled(True)
##        if QClipboard.ownsClipboard():
        self.ui.actionPast.setEnabled(True)
        self.ui.actionFind.setEnabled(True)
        self.disableFirstPrev()
        self.enableNextLast()   
        settings = QtCore.QSettings("KhmerOS", "Translation Editor")
        files = settings.value("recentFileList").toStringList()
        files.removeAll(fileName)        
        files.prepend(fileName)        
        while files.count() > MainWindow.MaxRecentFiles:
            files.removeAt(files.count()-1)        
        settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction() 
        
        self.ui.actionUnfiltered.setEnabled(True)
        self.ui.actionFilterFuzzy.setEnabled(True)
        self.ui.actionFilterTranslated.setEnabled(True)
        self.ui.actionFilterUntranslated.setEnabled(True)
        
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
        settings = QtCore.QSettings("KhmerOS", "Translation Editor")
        files = settings.value("recentFileList").toStringList()
        numRecentFiles = min(files.count(), MainWindow.MaxRecentFiles)             

        for i in range(numRecentFiles):           
            self.ui.recentaction[i].setText(files[i])          
            self.ui.recentaction[i].setData(QtCore.QVariant(files[i]))              
            self.ui.recentaction[i].setVisible(True)
        
        for j in range(numRecentFiles, MainWindow.MaxRecentFiles):
            self.ui.recentaction[j].setVisible(False)
    
    def closeEvent(self, event):            
        self.aboutDialog.closeAbout()
        if self.operator.modified():  
            if self.fileaction.aboutToSave(self):
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
        
    def disableFirstPrev(self):        
        self.ui.actionFirst.setDisabled(True)        
        self.ui.actionPrevious.setDisabled(True)                                  
    
    def enableFirstPrev(self):        
        self.ui.actionFirst.setEnabled(True)
        self.ui.actionPrevious.setEnabled(True)
    
    def disableNextLast(self):
        self.ui.actionNext.setDisabled(True)        
        self.ui.actionLast.setDisabled(True)                              
    
    def enableNextLast(self):
        self.ui.actionNext.setEnabled(True)         
        self.ui.actionLast.setEnabled(True)                                  

    def disableAll(self):
        self.ui.actionFirst.setDisabled(True)
        self.ui.actionPrevious.setDisabled(True)
        self.ui.actionNext.setDisabled(True)
        self.ui.actionLast.setDisabled(True)
        
    def showFindBar(self):
        self.find.setVisible(True)             
        
    def StartInNewWindow(self):        
        other = MainWindow()
        MainWindow.windowList.append(other) 
        other.fileaction.openFile()
        other.show()                   

    
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
##    self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog, QtCore.SLOT("show()"))
    sys.exit(app.exec_())
