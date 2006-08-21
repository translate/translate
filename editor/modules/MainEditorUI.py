# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Aug 21 13:54:38 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,571,476).size()).expandedTo(MainWindow.minimumSizeHint()))
        MainWindow.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        MainWindow.setWindowIcon(QtGui.QIcon("./images/icon.png"))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,571,27))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuOpen_Recent = QtGui.QMenu(self.menuFile)
        self.menuOpen_Recent.setIcon(QtGui.QIcon("./images/open.png"))
        self.menuOpen_Recent.setObjectName("menuOpen_Recent")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menuGo = QtGui.QMenu(self.menubar)
        self.menuGo.setObjectName("menuGo")

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")

        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")

        self.menuToolBar = QtGui.QMenu(self.menuView)
        self.menuToolBar.setObjectName("menuToolBar")

        self.menuToolbar = QtGui.QMenu(self.menuView)
        self.menuToolbar.setObjectName("menuToolbar")

        self.menuToolView = QtGui.QMenu(self.menuView)
        self.menuToolView.setObjectName("menuToolView")

        self.menuFilter = QtGui.QMenu(self.menuView)
        self.menuFilter.setObjectName("menuFilter")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,456,571,20))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.toolStandard = QtGui.QToolBar(MainWindow)
        self.toolStandard.setOrientation(QtCore.Qt.Horizontal)
        self.toolStandard.setObjectName("toolStandard")
        MainWindow.addToolBar(self.toolStandard)

        self.toolNavigation = QtGui.QToolBar(MainWindow)
        self.toolNavigation.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.toolNavigation.setAcceptDrops(False)
        self.toolNavigation.setOrientation(QtCore.Qt.Horizontal)
        self.toolNavigation.setObjectName("toolNavigation")
        MainWindow.addToolBar(self.toolNavigation)

        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setIcon(QtGui.QIcon("./images/new.png"))
        self.actionNew.setObjectName("actionNew")

        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setIcon(QtGui.QIcon("./images/open.png"))
        self.actionOpen.setObjectName("actionOpen")

        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setEnabled(False)
        self.actionSave.setIcon(QtGui.QIcon("./images/save.png"))
        self.actionSave.setObjectName("actionSave")

        self.actionSaveas = QtGui.QAction(MainWindow)
        self.actionSaveas.setEnabled(False)
        self.actionSaveas.setIcon(QtGui.QIcon("./images/saveAs.png"))
        self.actionSaveas.setObjectName("actionSaveas")

        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setIcon(QtGui.QIcon("./images/stop.png"))
        self.actionExit.setObjectName("actionExit")

        self.actionPrint = QtGui.QAction(MainWindow)
        self.actionPrint.setEnabled(False)
        self.actionPrint.setIcon(QtGui.QIcon("./images/print.png"))
        self.actionPrint.setObjectName("actionPrint")

        self.actionUndo = QtGui.QAction(MainWindow)
        self.actionUndo.setEnabled(False)
        self.actionUndo.setIcon(QtGui.QIcon("./images/undo.png"))
        self.actionUndo.setObjectName("actionUndo")

        self.actionRedo = QtGui.QAction(MainWindow)
        self.actionRedo.setEnabled(False)
        self.actionRedo.setIcon(QtGui.QIcon("./images/redo.png"))
        self.actionRedo.setObjectName("actionRedo")

        self.actionCut = QtGui.QAction(MainWindow)
        self.actionCut.setEnabled(False)
        self.actionCut.setIcon(QtGui.QIcon("./images/cut.png"))
        self.actionCut.setObjectName("actionCut")

        self.actionCopy = QtGui.QAction(MainWindow)
        self.actionCopy.setCheckable(False)
        self.actionCopy.setEnabled(False)
        self.actionCopy.setIcon(QtGui.QIcon("./images/copy.png"))
        self.actionCopy.setObjectName("actionCopy")

        self.actionPast = QtGui.QAction(MainWindow)
        self.actionPast.setEnabled(False)
        self.actionPast.setIcon(QtGui.QIcon("./images/paste.png"))
        self.actionPast.setObjectName("actionPast")

        self.actionFind = QtGui.QAction(MainWindow)
        self.actionFind.setEnabled(False)
        self.actionFind.setIcon(QtGui.QIcon("./images/find.png"))
        self.actionFind.setObjectName("actionFind")

        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")

        self.actionShowMenuBar = QtGui.QAction(MainWindow)
        self.actionShowMenuBar.setObjectName("actionShowMenuBar")

        self.actionShowTUview = QtGui.QAction(MainWindow)
        self.actionShowTUview.setObjectName("actionShowTUview")

        self.actionAboutQT = QtGui.QAction(MainWindow)
        self.actionAboutQT.setObjectName("actionAboutQT")

        self.actionShow_MenuBar = QtGui.QAction(MainWindow)
        self.actionShow_MenuBar.setObjectName("actionShow_MenuBar")

        self.actionShow_TUview = QtGui.QAction(MainWindow)
        self.actionShow_TUview.setObjectName("actionShow_TUview")

        self.actionFirst = QtGui.QAction(MainWindow)
        self.actionFirst.setEnabled(False)
        self.actionFirst.setIcon(QtGui.QIcon("./images/first.png"))
        self.actionFirst.setObjectName("actionFirst")

        self.actionPrevious = QtGui.QAction(MainWindow)
        self.actionPrevious.setEnabled(False)
        self.actionPrevious.setIcon(QtGui.QIcon("./images/previous.png"))
        self.actionPrevious.setObjectName("actionPrevious")

        self.actionNext = QtGui.QAction(MainWindow)
        self.actionNext.setEnabled(False)
        self.actionNext.setIcon(QtGui.QIcon("./images/next.png"))
        self.actionNext.setObjectName("actionNext")

        self.actionLast = QtGui.QAction(MainWindow)
        self.actionLast.setEnabled(False)
        self.actionLast.setIcon(QtGui.QIcon("./images/last.png"))
        self.actionLast.setObjectName("actionLast")

        self.actionShowDetail = QtGui.QAction(MainWindow)
        self.actionShowDetail.setObjectName("actionShowDetail")

        self.actionShowComment = QtGui.QAction(MainWindow)
        self.actionShowComment.setObjectName("actionShowComment")

        self.actionShowOverview = QtGui.QAction(MainWindow)
        self.actionShowOverview.setObjectName("actionShowOverview")

        self.actionCopySource2Target = QtGui.QAction(MainWindow)
        self.actionCopySource2Target.setObjectName("actionCopySource2Target")

        self.actionToggleFuzzy = QtGui.QAction(MainWindow)
        self.actionToggleFuzzy.setObjectName("actionToggleFuzzy")

        self.actionFile = QtGui.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")

        self.actionFind_Previous = QtGui.QAction(MainWindow)
        self.actionFind_Previous.setEnabled(False)
        self.actionFind_Previous.setObjectName("actionFind_Previous")

        self.actionFind_Next = QtGui.QAction(MainWindow)
        self.actionFind_Next.setEnabled(False)
        self.actionFind_Next.setObjectName("actionFind_Next")

        self.actionReplace = QtGui.QAction(MainWindow)
        self.actionReplace.setEnabled(False)
        self.actionReplace.setObjectName("actionReplace")

        self.actionFindAgain = QtGui.QAction(MainWindow)
        self.actionFindAgain.setEnabled(False)
        self.actionFindAgain.setObjectName("actionFindAgain")

        self.actionOpenInNewWindow = QtGui.QAction(MainWindow)
        self.actionOpenInNewWindow.setIcon(QtGui.QIcon("./images/window_new.png"))
        self.actionOpenInNewWindow.setObjectName("actionOpenInNewWindow")

        self.actionFilterFuzzy = QtGui.QAction(MainWindow)
        self.actionFilterFuzzy.setCheckable(False)
        self.actionFilterFuzzy.setChecked(False)
        self.actionFilterFuzzy.setObjectName("actionFilterFuzzy")

        self.actionFilterTranslated = QtGui.QAction(MainWindow)
        self.actionFilterTranslated.setChecked(False)
        self.actionFilterTranslated.setObjectName("actionFilterTranslated")

        self.actionFilterUntranslated = QtGui.QAction(MainWindow)
        self.actionFilterUntranslated.setObjectName("actionFilterUntranslated")

        self.actionUnfiltered = QtGui.QAction(MainWindow)
        self.actionUnfiltered.setObjectName("actionUnfiltered")
        self.menuFile.addAction(self.actionOpenInNewWindow)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuOpen_Recent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveas)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQT)
        self.menuGo.addAction(self.actionFirst)
        self.menuGo.addAction(self.actionPrevious)
        self.menuGo.addAction(self.actionNext)
        self.menuGo.addAction(self.actionLast)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPast)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionFind)
        self.menuEdit.addAction(self.actionFindAgain)
        self.menuEdit.addAction(self.actionReplace)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopySource2Target)
        self.menuEdit.addAction(self.actionToggleFuzzy)
        self.menuToolBar.addAction(self.actionShow_MenuBar)
        self.menuToolBar.addAction(self.actionShow_TUview)
        self.menuFilter.addAction(self.actionUnfiltered)
        self.menuFilter.addAction(self.actionFilterFuzzy)
        self.menuFilter.addAction(self.actionFilterTranslated)
        self.menuFilter.addAction(self.actionFilterUntranslated)
        self.menuView.addAction(self.menuToolView.menuAction())
        self.menuView.addAction(self.menuFilter.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuGo.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolStandard.addAction(self.actionOpen)
        self.toolStandard.addAction(self.actionSave)
        self.toolStandard.addAction(self.actionPrint)
        self.toolStandard.addSeparator()
        self.toolStandard.addAction(self.actionCut)
        self.toolStandard.addAction(self.actionCopy)
        self.toolStandard.addAction(self.actionPast)
        self.toolStandard.addSeparator()
        self.toolStandard.addAction(self.actionUndo)
        self.toolStandard.addAction(self.actionRedo)
        self.toolNavigation.addAction(self.actionFirst)
        self.toolNavigation.addAction(self.actionPrevious)
        self.toolNavigation.addAction(self.actionNext)
        self.toolNavigation.addAction(self.actionLast)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(self.tr("MainWindow"))
        self.menuFile.setTitle(self.tr("&File"))
        self.menuOpen_Recent.setTitle(self.tr("Open &Recent"))
        self.menuHelp.setTitle(self.tr("&Help"))
        self.menuGo.setTitle(self.tr("&Go"))
        self.menuEdit.setTitle(self.tr("&Edit"))
        self.menuView.setTitle(self.tr("&View"))
        self.menuToolBar.setTitle(self.tr("ToolBar"))
        self.menuToolbar.setTitle(self.tr("Toolbar"))
        self.menuToolView.setTitle(self.tr("ToolView"))
        self.menuFilter.setTitle(self.tr("Filter"))
        self.actionNew.setText(self.tr("&New"))
        self.actionNew.setShortcut(self.tr("Ctrl+N"))
        self.actionOpen.setText(self.tr("&Open"))
        self.actionOpen.setShortcut(self.tr("Ctrl+O"))
        self.actionSave.setText(self.tr("&Save"))
        self.actionSave.setShortcut(self.tr("Ctrl+S"))
        self.actionSaveas.setText(self.tr("Save &As"))
        self.actionSaveas.setShortcut(self.tr("Ctrl+A"))
        self.actionExit.setText(self.tr("&Quit"))
        self.actionExit.setShortcut(self.tr("Ctrl+Q"))
        self.actionPrint.setText(self.tr("&Print"))
        self.actionPrint.setShortcut(self.tr("Ctrl+P"))
        self.actionUndo.setText(self.tr("Undo"))
        self.actionUndo.setShortcut(self.tr("Ctrl+Z"))
        self.actionRedo.setText(self.tr("Redo"))
        self.actionRedo.setShortcut(self.tr("Ctrl+Shift+Z"))
        self.actionCut.setText(self.tr("Cut"))
        self.actionCut.setShortcut(self.tr("Ctrl+X"))
        self.actionCopy.setText(self.tr("Copy"))
        self.actionCopy.setShortcut(self.tr("Ctrl+C"))
        self.actionPast.setText(self.tr("Past"))
        self.actionPast.setShortcut(self.tr("Ctrl+V"))
        self.actionFind.setText(self.tr("Find"))
        self.actionFind.setShortcut(self.tr("Ctrl+F"))
        self.actionAbout.setText(self.tr("About"))
        self.actionAbout.setShortcut(self.tr("Ctrl+B"))
        self.actionShowMenuBar.setText(self.tr("Show MenuBar"))
        self.actionShowMenuBar.setShortcut(self.tr("Ctrl+M"))
        self.actionShowTUview.setText(self.tr("Show TUview"))
        self.actionShowTUview.setShortcut(self.tr("Ctrl+T"))
        self.actionAboutQT.setText(self.tr("About QT"))
        self.actionAboutQT.setShortcut(self.tr("Ctrl+T"))
        self.actionShow_MenuBar.setText(self.tr("Show MenuBar"))
        self.actionShow_TUview.setText(self.tr("Show TUview"))
        self.actionFirst.setText(self.tr("&First"))
        self.actionFirst.setShortcut(self.tr("Ctrl+Alt+Home"))
        self.actionPrevious.setText(self.tr("&Previous"))
        self.actionPrevious.setShortcut(self.tr("Shift+F3"))
        self.actionNext.setText(self.tr("&Next"))
        self.actionNext.setShortcut(self.tr("F3"))
        self.actionLast.setText(self.tr("&Last"))
        self.actionLast.setShortcut(self.tr("Ctrl+Alt+End"))
        self.actionShowDetail.setText(self.tr("Show Detail"))
        self.actionShowComment.setText(self.tr("Show Comment"))
        self.actionShowOverview.setText(self.tr("Show Overview"))
        self.actionCopySource2Target.setText(self.tr("Copy Source to Target"))
        self.actionCopySource2Target.setShortcut(self.tr("F2"))
        self.actionToggleFuzzy.setText(self.tr("Toggle fuzzy"))
        self.actionToggleFuzzy.setShortcut(self.tr("Ctrl+U"))
        self.actionFile.setText(self.tr("file"))
        self.actionFind_Previous.setText(self.tr("Find Previous"))
        self.actionFind_Next.setText(self.tr("Find Next"))
        self.actionReplace.setText(self.tr("&Replace"))
        self.actionReplace.setShortcut(self.tr("Ctrl+R"))
        self.actionFindAgain.setText(self.tr("Find Again"))
        self.actionFindAgain.setShortcut(self.tr("Ctrl+G"))
        self.actionOpenInNewWindow.setText(self.tr("Open in New Window"))
        self.actionFilterFuzzy.setText(self.tr("Fuzzy"))
        self.actionFilterTranslated.setText(self.tr("Translated"))
        self.actionFilterUntranslated.setText(self.tr("Untranslated"))
        self.actionFilterUntranslated.setIconText(self.tr("Untranslated"))
        self.actionFilterUntranslated.setToolTip(self.tr("Untranslated"))
        self.actionUnfiltered.setText(self.tr("Unfiltered"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
