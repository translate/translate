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
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_MainEditor import Ui_MainWindow
from modules.TUview import TUview
from modules.Overview import OverviewDock
from modules.Comment import CommentDock
from modules.Header import Header
from modules.Operator import Operator
from modules.FileAction import FileAction
from modules.Find import Find
from modules.Preference import Preference
from modules.AboutEditor import AboutEditor
import modules.World as World

class MainWindow(QtGui.QMainWindow):
    """
    The main window which holds the toolviews.
    """
    windowList = []

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.recentaction = []
        self.setWindowTitle(World.settingOrg + ' ' + World.settingApp + ' ' + World.settingVer)
        
        self.createRecentAction()
        self.setObjectName("mainwindows")
        
        # get the last geometry
        geometry = World.settings.value("lastGeometry")
        if (geometry.isValid()):
            self.setGeometry(geometry.toRect())
            
        # get the last state of mainwindows's toolbars and dockwidgets
        state = World.settings.value("lastState")
        
        #plug in overview widget
        self.dockOverview = OverviewDock()
        self.dockOverview.setObjectName("dockOverview")
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockOverview)
        self.ui.menuTools.addAction(self.dockOverview.actionShow())
        
        #plug in TUview widget
        self.dockTUview = TUview()
        self.dockTUview.setObjectName("dockTUview")
        self.ui.menuTools.addAction(self.dockTUview.actionShow())
        
        #plug in comment widget
        self.dockComment = CommentDock()
        self.dockComment.setObjectName("dockComment")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockComment)
        self.ui.menuTools.addAction(self.dockComment.actionShow())
        
        # check if the last state is valid it will restore
        if (not state.isValid()):
            self.setCentralWidget(self.dockTUview)
        else:
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockTUview)
            self.restoreState(state.toByteArray(), 1)
            if (self.dockOverview.isHidden()):
                self.dockOverview._actionShow.setText("Show Overview")
            if (self.dockTUview.isHidden()):
                self.dockTUview._actionShow.setText("Show Detail")
            if (self.dockComment.isHidden()):
                self.dockComment._actionShow.setText("Show Comment")
            
        #add widgets to statusbar
        self.statuslabel = QtGui.QLabel()
        self.statuslabel.setFrameStyle(QtGui.QFrame.NoFrame)
        self.ui.statusbar.addWidget(self.statuslabel)
        
        #create operator
        self.operator = Operator()
        
        #Help menu of aboutQt
        self.aboutDialog = AboutEditor()
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog.showDialog)
        self.connect(self.ui.actionAboutQT, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
        
        # create file action object and file action menu related signals
        self.fileaction = FileAction(self)
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.connect(self.ui.actionOpenInNewWindow, QtCore.SIGNAL("triggered()"), self.startInNewWindow)
        self.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.fileaction.save)
        self.connect(self.ui.actionSaveas, QtCore.SIGNAL("triggered()"), self.fileaction.saveAs)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        
        # create Find widget and connect signals related to it
        self.findBar = Find()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.findBar)
        self.connect(self.ui.actionFind, QtCore.SIGNAL("triggered()"), self.findBar.showFind)
        self.connect(self.ui.actionReplace, QtCore.SIGNAL("triggered()"), self.findBar.showReplace)
        self.connect(self.findBar, QtCore.SIGNAL("initSearch"), self.operator.initSearch)
        self.connect(self.findBar, QtCore.SIGNAL("searchNext"), self.operator.searchNext)
        self.connect(self.findBar, QtCore.SIGNAL("searchPrevious"), self.operator.searchPrevious)
        
        self.connect(self.findBar, QtCore.SIGNAL("replace"), self.operator.replace)
        self.connect(self.findBar, QtCore.SIGNAL("replaceAll"), self.operator.replaceAll)
        
        # "searchFound" sends container and location to be highlighted.
        self.connect(self.operator, QtCore.SIGNAL("searchResult"), self.dockTUview.highlightSearch)
        self.connect(self.operator, QtCore.SIGNAL("searchResult"), self.dockComment.highlightSearch)
        self.connect(self.operator, QtCore.SIGNAL("generalInfo"), self.showTemporaryMessage)
        # "replaceText" sends text field, start, length, and text to replace.
        self.connect(self.operator, QtCore.SIGNAL("replaceText"), self.dockTUview.replaceText)
        
        # Edit menu action
        self.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), self.undoer)
        self.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), self.redoer)
        
        #self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), self.dockComment.ui.txtComment, QtCore.SLOT("cut()"))
        #self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), self.dockTUview.ui.txtSource, QtCore.SLOT("copy()"))
        self.ui.actionCut.setEnabled(False)
        self.ui.actionCopy.setEnabled(False)
        self.connect(self.dockComment, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyPaste)
        self.connect(self.dockTUview, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyPaste)

        self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), self.cutter)
        self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), self.copier)
        self.connect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"), self.paster)

        # Select All File
        self.connect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), self.selectAll)

        # action Preferences menu 
        self.preference = Preference()
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL("triggered()"), self.preference.showDialog)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockComment.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockOverview.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockTUview.applySettings)

        # Edit Header
        self.headerDialog = Header()
        self.connect(self.ui.actionEdit_Header, QtCore.SIGNAL("triggered()"), self.operator.emitHeaderInfo)
        self.connect(self.operator, QtCore.SIGNAL("headerInfo"), self.headerDialog.showDialog)
        self.connect(self.operator, QtCore.SIGNAL("headerGenerated"), self.headerDialog.generatedHeader)
        self.connect(self.operator, QtCore.SIGNAL("headerAuto"), self.headerDialog.accepted)
        self.connect(self.headerDialog, QtCore.SIGNAL("updateHeader"), self.operator.updateNewHeader)
        self.connect(self.headerDialog, QtCore.SIGNAL("makeHeader"), self.operator.makeNewHeader)

        # Other actions
        self.connect(self.ui.actionNext, QtCore.SIGNAL("triggered()"), self.operator.next)
        self.connect(self.ui.actionPrevious, QtCore.SIGNAL("triggered()"), self.operator.previous)
        self.connect(self.ui.actionFirst, QtCore.SIGNAL("triggered()"), self.operator.first)
        self.connect(self.ui.actionLast, QtCore.SIGNAL("triggered()"), self.operator.last)
        self.connect(self.ui.actionCopySource2Target, QtCore.SIGNAL("triggered()"), self.dockTUview.source2target)

        # action filter menu
        self.connect(self.ui.actionFilterFuzzy, QtCore.SIGNAL("toggled(bool)"), self.operator.filterFuzzy)
        self.connect(self.ui.actionFilterTranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterTranslated)
        self.connect(self.ui.actionFilterUntranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterUntranslated)
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)

        # "currentUnit" sends currentUnit, currentIndex, and currentState.
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockOverview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateView)
        self.connect(self.dockTUview, QtCore.SIGNAL("currentIndex"), self.operator.setCurrentUnit)
        self.connect(self.dockOverview, QtCore.SIGNAL("currentIndex"), self.operator.setCurrentUnit)

        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockTUview.checkModified)
        self.connect(self.operator, QtCore.SIGNAL("updateUnit"), self.dockComment.checkModified)
        self.connect(self.dockOverview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockOverview, QtCore.SIGNAL("targetChanged"), self.dockTUview.setTarget)

        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.dockOverview.updateTarget)
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.operator.saveStoreToFile)
        self.connect(self.operator, QtCore.SIGNAL("savedAlready"), self.ui.actionSave.setEnabled)
        self.connect(self.dockTUview, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)
        self.connect(self.dockComment, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)

        self.connect(self.fileaction, QtCore.SIGNAL("fileName"), self.setTitle)
        self.connect(self.operator, QtCore.SIGNAL("toggleFirstLastUnit"), self.toggleFirstLastUnit)

        # newUnits sends newUnits and unitsStatus.
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockTUview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockOverview.filteredList)
        self.connect(self.operator, QtCore.SIGNAL("filteredList"), self.dockTUview.filteredList)

        # set file status information to text label of status bar.
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.statuslabel.setText)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.setOpening)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.operator.getUnits)
        
    def enableCopyPaste(self, bool):
        self.ui.actionCopy.setEnabled(bool)
        self.ui.actionCut.setEnabled(bool)

    def cutter(self):
        object = self.focusWidget()
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
        try:
            object.paste()
        except AttributeError:
            pass

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
        """
        set status after open a file
        @param fileName string, the filename to open
        """

        self.setTitle(fileName)
        self.ui.actionSave.setEnabled(False)  
        self.ui.actionSaveas.setEnabled(True)
        self.ui.actionUndo.setEnabled(True)
        self.ui.actionRedo.setEnabled(True)
        self.ui.actionPaste.setEnabled(True)
        self.ui.actionSelectAll.setEnabled(True)
        self.ui.actionFind.setEnabled(True)
        self.ui.actionReplace.setEnabled(True)
        self.ui.actionEdit_Header.setEnabled(True)
        # FIXME: what will happen if the file only contains 1 TU? Jens
        files = World.settings.value("recentFileList").toStringList()
        files.removeAll(fileName)
        files.prepend(fileName)
        while files.count() > World.MaxRecentFiles:
            files.removeLast()
        World.settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction() 

        self.ui.actionToggleFuzzy.setEnabled(True)
        self.ui.actionFilterFuzzy.setEnabled(True)
        self.ui.actionFilterTranslated.setEnabled(True)
        self.ui.actionFilterUntranslated.setEnabled(True)
    
    def startRecentAction(self):
        action = self.sender()
        if action:
            self.fileaction.setFileName(action.data().toString())

    def createRecentAction(self):
        for i in range(World.MaxRecentFiles):
            self.ui.recentaction.append(QtGui.QAction(self))
            self.ui.recentaction[i].setVisible(False)
            self.connect(self.ui.recentaction[i], QtCore.SIGNAL("triggered()"), self.startRecentAction)
            self.ui.menuOpen_Recent.addAction(self.ui.recentaction[i])
        self.updateRecentAction()

    def updateRecentAction(self):
        # FIXME: comment this
        files = World.settings.value("recentFileList").toStringList()
        numRecentFiles = min(files.count(), World.MaxRecentFiles)

        for i in range(numRecentFiles):
            # FIXME: make sure that the text does not get too long. Jens
            self.ui.recentaction[i].setText(files[i])
            self.ui.recentaction[i].setData(QtCore.QVariant(files[i]))
            self.ui.recentaction[i].setVisible(True)

        for j in range(numRecentFiles, World.MaxRecentFiles):
            self.ui.recentaction[j].setVisible(False)

    def closeEvent(self, event):
        # FIXME: comment the param
        if self.operator.modified():
            if self.fileaction.aboutToClose(self):
                event.accept()
            else:
                event.ignore()
                
        # remember last geometry
        World.settings.setValue("lastGeometry", QtCore.QVariant(self.geometry()))
        
        # remember last state
        state = self.saveState(1)
        World.settings.setValue("lastState", QtCore.QVariant(state))
        
    def setTitle(self, title):
        """set the title of program.
        @param title: title string."""
        shownName = QtCore.QFileInfo(title).fileName()
        self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(World.settingApp))

    def disableUndo(self):
        self.ui.actionUndo.setVisible(True)

    def enableUndo(self):
        self.ui.actionUndo.setEnabled(True)

    def toggleFirstLastUnit(self, atFirst, atLast):
        """set enable/disable first, previous, next, and last unit buttons
        @param atFirst: bool indicates that the unit is at first place
        @param atLast: bool indicates that the unit is at last place
        """
        self.ui.actionFirst.setDisabled(atFirst)
        self.ui.actionPrevious.setDisabled(atFirst)
        self.ui.actionNext.setDisabled(atLast)
        self.ui.actionLast.setDisabled(atLast)
    
    def startInNewWindow(self):
        other = MainWindow()
        MainWindow.windowList.append(other)
        if other.fileaction.openFile():
            other.show()
        
    def showTemporaryMessage(self, text):
        self.ui.statusbar.showMessage(text, 3000)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec_())
