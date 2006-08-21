#!/usr/bin/python
# -*- coding: utf8 -*-

#WordForge Translation Editor
# (c) 2006 Open Forum of Cambodia, all rights reserved.
#
# Version 1.0 
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details.
#
# Developed by:
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

import sys
##import os.path
#### add a modules path in sys.path so the other module inside it is known during import
##sys.path.append(os.path.join(sys.path[0] ,"modules"))


from PyQt4 import QtCore, QtGui
from modules.MainEditorUI import Ui_MainWindow
from translate.storage import factory
from modules.TUview import TUview
from modules.Overview import OverviewDock
from modules.Comment import CommentDock
from modules.Operator import Operator
from modules.FileAction import FileAction
from modules.Find import Find

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
##        self.pasteAvailable()

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

        self.connect(self.ui.actionFilter, QtCore.SIGNAL("toggled(bool)"), self.toggleFilter)
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)
        
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateTUview)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateComment)        

        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockOverview.updateItem)
        self.connect(self.operator, QtCore.SIGNAL("currentPosition"), self.dockTUview.updateScrollbar)
        self.connect(self.dockTUview, QtCore.SIGNAL("scrollbarPosition"), self.operator.setCurrentPosition)
        self.connect(self.dockOverview, QtCore.SIGNAL("itemSelected"), self.operator.setCurrentUnit)

        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockTUview.checkModified)
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockComment.checkModified)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.dockOverview.setTarget)
        
        #self.connect(self.dockTUview, QtCore.SIGNAL("itemSelected"), self.operator.setCurrentUnit)
        #self.connect(self.dockTUview, QtCore.SIGNAL("sliderChanged"), self.dockOverview.scrollToSlider)
        
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.operator.saveStoreToFile)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.setTitle)        
        self.connect(self.operator, QtCore.SIGNAL("firstUnit"), self.disableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("firstUnit"), self.enableNextLast)
        self.connect(self.operator, QtCore.SIGNAL("lastUnit"), self.enableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("lastUnit"), self.disableNextLast)
        self.connect(self.operator, QtCore.SIGNAL("middleUnit"), self.enableFirstPrev)
        self.connect(self.operator, QtCore.SIGNAL("middleUnit"), self.enableNextLast)        
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.refillItems)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockTUview.slotNewUnits)
   
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.showCurrentStatus)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.setOpening)  
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.showCurrentStatus)           
        
            
    def objectAvailable(self):
        if self.dockTUview.ui.txtTarget.hasFocus():
            return self.dockTUview.ui.txtTarget
        elif self.dockComment.ui.txtComment.hasFocus():
            return self.dockComment.ui.txtComment
        else:
            return
            
    def pasteAvailable(self):
        objclipboard = QtGui.QClipboard()
        if QtGui.QClipboard.ownsClipboard():
            self.ui.actionPast.setEnabled(True)
            
    def selections(self):
        object = self.objectAvailable()
        try:
            self.connect(object, QtCore.SIGNAL("selectionChanged()"), QtCore.SLOT("setEnabled"))
        except TypeError:
            return
        self.ui.actionCut.setEnabled(True)
        self.ui.actionCopy.setEnabled(True)
    
    def cutter(self):
        object = self.objectAvailable()
        self.operator.cutEdit(object)
        self.ui.actionPast.setEnabled(True)
        
    def copier(self):
        object = self.objectAvailable()
        self.operator.copyEdit(object)
        self.ui.actionPast.setEnabled(True)
        
    def paster(self):
        object = self.objectAvailable()
        object.paste()
        
    def redoer(self):
        object = self.objectAvailable()
        self.operator.redoEdit(object)
        
    def undoer(self):
        object = self.objectAvailable()
        self.operator.undoEdit(object)
        print object.isUndoRedoEnabled()
##        if object.isUndoRedoEnabled():
##            self.ui.actionUndo.setEnabled(False)
    
         
    def toggleFilter(self, filter):
        if filter:
            self.operator.emitFilteredUnits()
        else:
            self.operator.emitNewUnits() 

    def showCurrentStatus(self, status):
        self.statuslabel.setText(' ' + status + ' ')

    def setOpening(self, fileName):        
        self.setTitle(fileName)
        self.operator.getUnits(fileName)            
        self.ui.actionSave.setEnabled(True)         # enable Save and Saveas action after opening file
        self.ui.actionSaveas.setEnabled(True)
        self.ui.actionUndo.setEnabled(True)
        self.ui.actionRedo.setEnabled(True)
        self.ui.actionFind.setEnabled(True)
        self.disableFirstPrev()
        self.enableNextLast()   
        settings = QtCore.QSettings("KhmerOS", "Translation Editor")
        files = settings.value("recentFileList").toStringList()
        files.removeAll(fileName)        
        files.prepend(fileName)      
        self.selections()
        while files.count() > MainWindow.MaxRecentFiles:
            files.removeAt(files.count()-1)        
        settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction() 
        
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
        if self.operator.modified():  
            if self.fileaction.aboutToSave(self):
                event.accept()
            else:
                event.ignore()
           
    def setTitle(self, title):
        shownName = QtCore.QFileInfo(title).fileName()
        self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(self.tr("Translation Editor")))
    
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
    sys.exit(app.exec_())
