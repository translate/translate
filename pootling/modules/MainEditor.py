
#!/usr/bin/python
# -*- coding: utf8 -*-
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
# 
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

import os
import sys
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_MainEditor import Ui_MainWindow
from pootling.modules.TUview import TUview
from pootling.modules.Overview import OverviewDock
from pootling.modules.Comment import CommentDock
from pootling.modules.Header import Header
from pootling.modules.Operator import Operator
from pootling.modules.FileAction import FileAction
from pootling.modules.Find import Find
from pootling.modules.Catalog import Catalog
from pootling.modules.Preference import Preference
from pootling.modules.AboutEditor import AboutEditor
import pootling.modules.World as World
from pootling.modules import tmSetting
from pootling.modules import tableTM
import __version__

class MainWindow(QtGui.QMainWindow):
    """
    The main window which holds the toolviews.
    """

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.recentaction = []
        self.ui.bookmarkaction = []
        self.setWindowTitle(World.settingApp + ' ' + __version__.ver)
        self.createBookmarkAction()
        self.clearBookmarks()
        
        # get the last geometry
        geometry = World.settings.value("lastGeometry")
        if (geometry.isValid()):
            self.setGeometry(geometry.toRect())

        sepAction = self.ui.menuWindow.actions()[0]
        #plug in overview widget
        self.dockOverview = OverviewDock(self)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockOverview)
        action = self.dockOverview.toggleViewAction()
        action.setText("&Overview")
        action.setStatusTip("Toggle the Overview window")
        action.setWhatsThis("<h3>Toggle the Overview window</h3>If the Overview window is hidden then display it. If it is displayed then close it.")
        self.ui.menuWindow.insertAction(sepAction, action)
        
        #plug in TUview widget
        self.dockTUview = TUview(self)
        self.setCentralWidget(self.dockTUview)
        action = self.dockTUview.toggleViewAction()
        action.setText("&Detail")
        action.setStatusTip("Toggle the Detail window")
        action.setWhatsThis("<h3>Toggle the Detail window</h3>If the Detail window is hidden then display it. If it is displayed then close it.")
        self.ui.menuWindow.insertAction(sepAction, action)
        
        #plug in comment widget
        self.dockComment = CommentDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockComment)
        action = self.dockComment.toggleViewAction()
        action.setText("&Comment")
        action.setStatusTip("Toggle the Comment window")
        action.setWhatsThis("<h3>Toggle the Comment window</h3>If the Comment window is hidden then display it. If it is displayed then close it.")
        self.ui.menuWindow.insertAction(sepAction, action)
#        self.ui.menuWindow.insertAction(sepAction, self.dockComment.toggleViewAction())
       
        #add widgets to statusbar
        self.statusfuzzy = QtGui.QLabel()
        pixmap = QtGui.QPixmap("../images/fuzzy.png")
        self.statusfuzzy.setPixmap(pixmap.scaled(16, 16, QtCore.Qt.KeepAspectRatio))
        self.statusfuzzy.setToolTip("Current unit is fuzzy")
        
        self.statuslabel = QtGui.QLabel()
        self.statuslabel.setFrameStyle(QtGui.QFrame.NoFrame)
        self.statuslabel.setMargin(1)
        self.ui.statusbar.addWidget(self.statuslabel)
        self.ui.statusbar.setWhatsThis("<h3>Status Bar</h3>Shows the progress of the translation in the file and messages about the current state of the application.")

        #add action from each toolbar toggleviewaction to toolbars submenu of view menu
        self.ui.menuToolbars.addAction(self.ui.toolFile.toggleViewAction())
        self.ui.menuToolbars.addAction(self.ui.toolEdit.toggleViewAction())
        self.ui.menuToolbars.addAction(self.ui.toolNavigation.toggleViewAction())
        self.ui.menuToolbars.addAction(self.ui.toolFilter.toggleViewAction())

        #create operator
        self.operator = Operator()
        
        # action Tool menu of Catalog Manager
        self.Catalog = Catalog(self)
        self.connect(self.ui.actionCatalogManager, QtCore.SIGNAL("triggered()"), self.Catalog.showDialog)

         # TM table
        self.table = tableTM.tableTM(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.table)
        action = self.table.toggleViewAction()
        action.setText("TM &Lookup")
        action.setStatusTip("Toggle the TM Lookup window")
        action.setWhatsThis("<h3>Toggle the TM Lookup window</h3>If the TM Lookup window is hidden then display it. If it is displayed then close it.")
        self.ui.menuWindow.insertAction(sepAction, action)
        self.connect(self.operator, QtCore.SIGNAL("candidates"), self.table.fillTable)
        self.connect(self.table, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.table.filterChanged)
        
        #Help menu of aboutQt
        self.ui.menuHelp.addSeparator()
        action = QtGui.QWhatsThis.createAction(self)
        action.setText(self.tr("&What's This?"))
        action.setStatusTip("Context sensitive help")
        action.setWhatsThis("<h3>Display context sensitive help</h3>In what's This? mode, the mouse cursor shows an arrow with a question mark, and you can click on the interface elements to get a short description of what they do and how to use them in a dialog, the feature can be accessed using the context help button in the titlebar.")
        self.ui.menuHelp.addAction(action)
        self.aboutDialog = AboutEditor(self)
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.aboutDialog.showDialog)
        self.connect(self.ui.actionAboutQT, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("aboutQt()"))
        
        # create file action object and file action menu related signals
        self.fileaction = FileAction(self)
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.connect(self.ui.action_Close, QtCore.SIGNAL("triggered()"), self.closeFile)
        self.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.fileaction.save)
        self.connect(self.ui.actionSaveas, QtCore.SIGNAL("triggered()"), self.fileaction.saveAs)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("close()"))
        self.createRecentAction()
        
        # create Find widget and connect signals related to it
        self.findBar = Find(self)
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
        self.connect(self.operator, QtCore.SIGNAL("replaceText"), self.dockComment.replaceText)
       
       # Goto menu action
        self.ui.actionGoTo.setIcon(QtGui.QIcon("../images/goto.png"))
        self.connect(self.ui.actionGoTo, QtCore.SIGNAL("triggered()"), self.showGoto)
        
        # Bookmarks menu action
        self.connect(self.ui.actionAddBookmarks, QtCore.SIGNAL("triggered()"), self.setBookmarks)
        self.connect(self.ui.actionClearBookmarks, QtCore.SIGNAL("triggered()"), self.clearBookmarks)
        
        # action Preferences menu 
        self.preference = Preference(self)
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL("triggered()"), self.preference.showDialog)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockComment.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockOverview.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("settingsChanged"), self.dockTUview.applySettings)
        self.connect(self.preference, QtCore.SIGNAL("TMpreference"), self.operator.setLookupStatus)
        
        # action setting Path of TM
        self.tmsetting = tmSetting.tmSetting(self)
        self.connect(self.ui.actionBuild_TM, QtCore.SIGNAL("triggered()"), self.tmsetting.showDialog)
        self.connect(self.operator, QtCore.SIGNAL("noTM"), self.showTemporaryMessage)
        self.connect(self.tmsetting, QtCore.SIGNAL("matcher"), self.operator.setMatcher)
        # action lookup text and auto translation from TM
        self.connect(self.ui.actionAuto_translate, QtCore.SIGNAL("triggered()"), self.operator.autoTranslate)
        
        # Edit Header
        self.headerDialog = Header(self, self.operator)
        self.connect(self.ui.actionEdit_Header, QtCore.SIGNAL("triggered()"), self.headerDialog.showDialog)

        # Other actions
        self.connect(self.ui.actionFirst, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollFirst)
        self.connect(self.ui.actionPrevious, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollPrevious)
        self.connect(self.ui.actionNext, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollNext)
        self.connect(self.ui.actionLast, QtCore.SIGNAL("triggered()"), self.dockOverview.scrollLast)
        self.connect(self.ui.actionCopySource2Target, QtCore.SIGNAL("triggered()"), self.dockTUview.source2target)

        # action filter menu
        self.connect(self.ui.actionFilterFuzzy, QtCore.SIGNAL("toggled(bool)"), self.operator.filterFuzzy)
        self.connect(self.ui.actionFilterTranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterTranslated)
        self.connect(self.ui.actionFilterUntranslated, QtCore.SIGNAL("toggled(bool)"), self.operator.filterUntranslated)
        self.connect(self.ui.actionToggleFuzzy, QtCore.SIGNAL("triggered()"), self.operator.toggleFuzzy)
    
        # "currentUnit" sends currentUnit, currentIndex
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockOverview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockTUview.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.dockComment.updateView)
        self.connect(self.operator, QtCore.SIGNAL("currentUnit"), self.addFuzzyIcon)
        self.connect(self.dockOverview, QtCore.SIGNAL("filteredIndex"), self.operator.setUnitFromPosition)
        self.connect(self.dockTUview, QtCore.SIGNAL("scrollToRow"), self.dockOverview.scrollToRow)

        self.connect(self.dockOverview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockTUview, QtCore.SIGNAL("targetChanged"), self.operator.setTarget)
        self.connect(self.dockComment, QtCore.SIGNAL("commentChanged"), self.operator.setComment)
        self.connect(self.fileaction, QtCore.SIGNAL("fileSaved"), self.operator.saveStoreToFile)
        self.connect(self.fileaction, QtCore.SIGNAL("saveFile"), self.operator.setModified)
        self.connect(self.operator, QtCore.SIGNAL("readyForSave"), self.ui.actionSave.setEnabled)

        self.connect(self.fileaction, QtCore.SIGNAL("fileSaved"), self.setTitle)
        self.connect(self.dockOverview, QtCore.SIGNAL("toggleFirstLastUnit"), self.toggleFirstLastUnit)

        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockOverview.slotNewUnits)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockTUview.viewSetting)
        self.connect(self.operator, QtCore.SIGNAL("newUnits"), self.dockComment.viewSetting)
        # "filterChanged" sends filter and number of filtered items.
        self.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.dockOverview.filterChanged)
        self.connect(self.operator, QtCore.SIGNAL("filterChanged"), self.dockTUview.filterChanged)

        # set file status information to text label of status bar.
        self.connect(self.operator, QtCore.SIGNAL("currentStatus"), self.statuslabel.setText)
        self.connect(self.fileaction, QtCore.SIGNAL("fileOpened"), self.openFile)
        self.connect(self.operator, QtCore.SIGNAL("fileIsOK"), self.setOpening)

        # progress bar
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.progressBar)
        self.connect(self.dockOverview, QtCore.SIGNAL("progressBarValue"), self.updateProgress)

        # get the last state of mainwindows's toolbars and dockwidgets
        state = World.settings.value("MainWindowState")
        # check if the last state is valid it will restore
        if (state.isValid()):
            self.restoreState(state.toByteArray(), 1)
        
        tuViewHidden = World.settings.value("TuViewHidden", QtCore.QVariant(False))
        self.dockTUview.setHidden(tuViewHidden.toBool())
        self.findBar.setHidden(True)
        
        self.connect(self.Catalog, QtCore.SIGNAL("openFile"), self.openFile)
        self.connect(self.Catalog, QtCore.SIGNAL("goto"), self.dockOverview.gotoRow)

    def updateProgress(self, value):
        if (not self.progressBar.isVisible()):
            self.progressBar.setVisible(True)
        elif (value == 100):
            self.progressBar.setVisible(False)
        self.progressBar.setValue(value)
    
    def enableCopyCut(self, bool):
        self.ui.actionCopy.setEnabled(bool)
        self.ui.actionCut.setEnabled(bool)        

    def enableUndo(self, bool):
        self.ui.actionUndo.setEnabled(bool)

    def enableRedo(self, bool):
        self.ui.actionRedo.setEnabled(bool)

    def showGoto(self):
        value, ok = QtGui.QInputDialog.getInteger(self, self.tr("Goto"), self.tr("Unit Index:"), 1, 1, self.operator.status.numTotal)
        if ok:
            self.dockOverview.gotoRow(value)

    def setBookmarks(self):
        unit = self.operator.getCurrentUnit()
        id = self.dockOverview.getCurrentIndex()
        reducedSource = str(id) + " : " + unit.source[:15] + "..."
        bookmark = World.settings.value("bookmarkList").toStringList()
        bookmark.removeAll(reducedSource)
        bookmark.prepend(reducedSource)
        while bookmark.count() > World.MaxRecentFiles:
            bookmark.removeAt(bookmark.count() - 1)
        World.settings.setValue("bookmarkList", QtCore.QVariant(bookmark))
        self.updateBookmarkAction()

    def createBookmarkAction(self):
        for i in range(World.MaxRecentFiles):
            self.ui.bookmarkaction.append(QtGui.QAction(self))
            self.ui.bookmarkaction[i].setVisible(False)
            self.connect(self.ui.bookmarkaction[i], QtCore.SIGNAL("triggered()"), self.startBookmarkAction)
            self.ui.menuBookmark.addAction(self.ui.bookmarkaction[i])
        self.updateBookmarkAction()
    
    def startBookmarkAction(self):
        action = self.sender()
        if action:
            index = str(action.data().toString()).split(" : ")
            self.dockOverview.gotoRow(int(index[0]))
    
    def updateBookmarkAction(self):
        """
        Update recent actions of Open Recent Files with names of recent opened files
        """
        bookmark = World.settings.value("bookmarkList").toStringList()
        numBookmark = min(bookmark.count(), World.MaxRecentFiles)
        for i in range(numBookmark):
            self.ui.bookmarkaction[i].setText(bookmark[i])
            self.ui.bookmarkaction[i].setData(QtCore.QVariant(bookmark[i]))
            self.ui.bookmarkaction[i].setVisible(True)

        for j in range(numBookmark, World.MaxRecentFiles):
            self.ui.bookmarkaction[j].setVisible(False)

    def clearBookmarks(self):
        files = World.settings.value("bookmarkList").toStringList()
        numRecentFiles = min(files.count(), World.MaxRecentFiles)
        for i in range(numRecentFiles):
            self.ui.bookmarkaction[i].setVisible(False)
        World.settings.remove("bookmarkList")

    def setOpening(self, fileName): 
        """
        set status after open a file
        @param fileName string, the filename to open
        """
        self.OpeningClosingFile(fileName, True)
        files = World.settings.value("recentFileList").toStringList()
        files.removeAll(fileName)
        files.prepend(fileName)
        while files.count() > World.MaxRecentFiles:
            files.removeAt(files.count() - 1)
        if (files.count() > 0):
            self.ui.menuOpen_Recent.setEnabled(True)
        World.settings.setValue("recentFileList", QtCore.QVariant(files))
        self.updateRecentAction()
        self.clearBookmarks()
        
    def startRecentAction(self):
        action = self.sender()
        if action:
            # TODO: remove filename from recent file if it doesn't exist.
            self.fileaction.setFileName(action.data().toString())
    
    def clearRecentAction(self):
        self.ui.menuOpen_Recent.clear()
        self.ui.menuOpen_Recent.setEnabled(False)
        World.settings.remove("recentFileList")
        # remove menu Open_Recent action, and add Open action to toolbar
        self.addOpenToBar()
    
    def createRecentAction(self):
        for i in range(World.MaxRecentFiles):
            self.ui.recentaction.append(QtGui.QAction(self))
            self.ui.recentaction[i].setVisible(False)
            self.connect(self.ui.recentaction[i], QtCore.SIGNAL("triggered()"), self.startRecentAction)
            self.ui.menuOpen_Recent.addAction(self.ui.recentaction[i])
        self.ui.menuOpen_Recent.addSeparator()
        self.clearAction = QtGui.QAction("&Clear", self)
        self.connect(self.clearAction, QtCore.SIGNAL("triggered()"), self.clearRecentAction)
        self.ui.menuOpen_Recent.addAction(self.clearAction)
        self.ui.menuOpen_Recent.setEnabled(False)
        self.updateRecentAction()

    def updateRecentAction(self):
        """
        Update recent actions of Open Recent Files with names of recent opened files
        """
        if (not len(self.ui.menuOpen_Recent.actions())):
            self.createRecentAction()
        files = World.settings.value("recentFileList").toStringList()
        if (files.count() > 0):
            self.ui.menuOpen_Recent.setEnabled(True)
        numRecentFiles = min(files.count(), World.MaxRecentFiles)
        for i in range(numRecentFiles):
            self.ui.recentaction[i].setText(self.tr("&" + str(i+1) + ": ") + files[i])
            self.ui.recentaction[i].setData(QtCore.QVariant(files[i]))
            self.ui.recentaction[i].setVisible(True)

        for j in range(numRecentFiles, World.MaxRecentFiles):
            self.ui.recentaction[j].setVisible(False)
        # remove Open action from toolbar, and add menu Open_Recent action to toolbar
        self.addOpenToBar()

    def closeEvent(self, event):
        """
        @param QCloseEvent Object: received close event when closing mainwindows
        """
        QtGui.QMainWindow.closeEvent(self, event)
        if self.operator.getModified():
            if self.fileaction.aboutToClose(self):
                event.accept()
            else:
                event.ignore()
        
        # remember last geometry
        World.settings.setValue("lastGeometry", QtCore.QVariant(self.geometry()))
        
        # remember last state
        state = self.saveState(1)
        World.settings.setValue("MainWindowState", QtCore.QVariant(state))
        World.settings.setValue("TuViewHidden", QtCore.QVariant(self.dockTUview.isHidden()))
        
    def setTitle(self, title):
        """set the title of program.
        @param title: title string."""
        if (title):
            shownName = QtCore.QFileInfo(title).fileName()
            self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(World.settingApp))

    def toggleFirstLastUnit(self, atFirst, atLast):
        """set enable/disable first, previous, next, and last unit buttons
        @param atFirst: bool indicates that the unit is at first place
        @param atLast: bool indicates that the unit is at last place
        """
        self.ui.actionFirst.setDisabled(atFirst)
        self.ui.actionPrevious.setDisabled(atFirst)
        self.ui.actionNext.setDisabled(atLast)
        self.ui.actionLast.setDisabled(atLast)

    def showTemporaryMessage(self, text):
        self.ui.statusbar.showMessage(text, 3000)
        
    def focusChanged(self, oldWidget, newWidget):
        if (oldWidget):
            self.disconnect(oldWidget, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyCut)
            self.disconnect(oldWidget, QtCore.SIGNAL("undoAvailable(bool)"), self.enableUndo)
            self.disconnect(oldWidget, QtCore.SIGNAL("redoAvailable(bool)"), self.enableRedo)
            # cut, copy and paste in oldWidget
            if (callable(getattr(oldWidget, "cut", None))):
                self.disconnect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("cut()"))

            if (callable(getattr(oldWidget, "copy", None))):
                self.disconnect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("copy()"))

            if (callable(getattr(oldWidget, "paste", None))):
                self.disconnect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("paste()"))
            # undo, redo and selectAll in oldWidget
            if (callable(getattr(oldWidget, "document", None))):
                self.disconnect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), oldWidget.document(), QtCore.SLOT("undo()"))
                self.disconnect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), oldWidget.document(), QtCore.SLOT("redo()"))

            if (callable(getattr(oldWidget, "selectAll", None))):
                self.disconnect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), oldWidget, QtCore.SLOT("selectAll()"))
        if (newWidget):
            self.connect(newWidget, QtCore.SIGNAL("copyAvailable(bool)"), self.enableCopyCut)
            self.connect(newWidget, QtCore.SIGNAL("undoAvailable(bool)"), self.enableUndo)
            self.connect(newWidget, QtCore.SIGNAL("redoAvailable(bool)"), self.enableRedo)
            # cut, copy and paste in newWidget
            if (callable(getattr(newWidget, "cut", None))):
                self.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("cut()"))

            if (callable(getattr(newWidget, "copy", None))):
                self.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("copy()"))

            if (callable(getattr(newWidget, "paste", None))):
                self.connect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("paste()"))
                if (callable(getattr(newWidget, "isReadOnly", None))):
                    self.ui.actionPaste.setEnabled(not newWidget.isReadOnly())
                else:
                    self.ui.actionPaste.setEnabled(True)
            else:
                self.ui.actionPaste.setEnabled(False)
            # Select All
            if (callable(getattr(newWidget, "selectAll", None))):
                self.connect(self.ui.actionSelectAll , QtCore.SIGNAL("triggered()"), newWidget, QtCore.SLOT("selectAll()"))

            if (callable(getattr(newWidget, "textCursor", None))):
                hasSelection = newWidget.textCursor().hasSelection()
                self.enableCopyCut(hasSelection)
            else:
                self.enableCopyCut(False)

            #it will not work for QLineEdits
            if (callable(getattr(newWidget, "document", None))):
                undoAvailable = newWidget.document().isUndoAvailable()
                redoAvailable = newWidget.document().isRedoAvailable()
                self.enableUndo(undoAvailable)
                self.enableRedo(redoAvailable)
                self.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"), newWidget.document(), QtCore.SLOT("undo()"))
                self.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"), newWidget.document(), QtCore.SLOT("redo()"))
            else:
                self.enableUndo(False)
                self.enableRedo(False)
    
    def addFuzzyIcon(self, unit):
        self.ui.statusbar.removeWidget(self.statusfuzzy)
        if hasattr(unit, "x_editor_state"):
            if (unit.x_editor_state & World.fuzzy):
                self.statusfuzzy.setVisible(True)
                self.ui.statusbar.addWidget(self.statusfuzzy)
    
    def openFile(self, value):
        closed = self.closeFile()
        if (closed):
            self.operator.getUnits(value)
    
    def closeFile(self):
        """return True when successfully close file, else return False."""
        if (not self.operator.getModified()):
            self.setClosingFile()
        else:
            if self.fileaction.aboutToClose(self):
                self.setClosingFile()
            else:
                return False
        return True

    def setClosingFile(self):
        """
        set status after closing a file
        """
        filename = ""
        self.OpeningClosingFile(filename, False)
        self.operator.setAfterfileClosed()
        self.ui.actionSave.setEnabled(False)
        self.statuslabel.setText("")
    
    def OpeningClosingFile(self, filename, bool):
        self.setWindowTitle(((filename != "") and (filename + ' - ') or filename) + World.settingApp + ' ' + __version__.ver)
        self.ui.action_Close.setEnabled(bool)
        self.ui.actionSaveas.setEnabled(bool)
        self.ui.actionPaste.setEnabled(bool)
    
        self.ui.actionSelectAll.setEnabled(bool)
        self.ui.actionFind.setEnabled(bool)
        self.ui.actionReplace.setEnabled(bool)
        self.ui.actionCopySource2Target.setEnabled(bool)
        self.ui.actionEdit_Header.setEnabled(bool)
        self.ui.actionGoTo.setEnabled(bool)
        self.ui.actionAddBookmarks.setEnabled(bool)
        self.ui.actionToggleFuzzy.setEnabled(bool)
        self.ui.actionFilterFuzzy.setEnabled(bool)
        self.ui.actionFilterTranslated.setEnabled(bool)
        self.ui.actionFilterUntranslated.setEnabled(bool)
        self.ui.actionAuto_translate.setEnabled(bool)
        self.findBar.toggleViewAction().setVisible(bool)
    
    def addOpenToBar(self):
        '''add Open action or menu Open_Recent action to toolbar
        
        '''
        if (hasattr(self, "actionOpen")):
            self.ui.toolFile.removeAction(self.actionOpen)
        if not self.ui.menuOpen_Recent.isEnabled():
            self.actionOpen = self.ui.actionOpen
        else:
            self.actionOpen = self.ui.menuOpen_Recent.menuAction()
            self.disconnect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
            self.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.fileaction.openFile)
        self.actionOpen.setToolTip(self.tr("Open"))
        self.actionOpen.setWhatsThis("<h3>Open a file</h3>You will be asked for the name of a file to be opened and open recent file in an editor window.") 
        self.ui.toolFile.insertAction(self.ui.actionSave, self.actionOpen)
        
def main(inputFile = None):
    # set the path for QT in order to find the icons
    if __name__ == "__main__":
        QtCore.QDir.setCurrent(os.path.join(sys.path[0], "../ui"))
    else:
        import distutils.sysconfig
        packagesdir = distutils.sysconfig.get_python_lib(prefix="/usr/local/")
        QtCore.QDir.setCurrent(os.path.join(packagesdir, "pootling", "ui"))
    app = QtGui.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    
    if (inputFile):
        if os.path.exists(inputFile):
            editor.fileaction.setFileName(inputFile)
        else:
            msg = editor.tr("%1 file name doesn't exist").arg(inputFile)
            QtGui.QMessageBox.warning(editor, editor.tr("File not found") , msg)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
