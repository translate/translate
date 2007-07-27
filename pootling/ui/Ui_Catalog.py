# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Jul 23 10:00:42 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Catalog(object):
    def setupUi(self, Catalog):
        Catalog.setObjectName("Catalog")
        Catalog.setWindowModality(QtCore.Qt.NonModal)
        Catalog.resize(QtCore.QSize(QtCore.QRect(0,0,581,412).size()).expandedTo(Catalog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Catalog.sizePolicy().hasHeightForWidth())
        Catalog.setSizePolicy(sizePolicy)

        self.centralwidget = QtGui.QWidget(Catalog)
        self.centralwidget.setObjectName("centralwidget")

        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.treeCatalog = QtGui.QTreeWidget(self.centralwidget)

        font = QtGui.QFont(self.treeCatalog.font())
        font.setPointSize(10)
        self.treeCatalog.setFont(font)
        self.treeCatalog.setFocusPolicy(QtCore.Qt.NoFocus)
        self.treeCatalog.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.treeCatalog.setAcceptDrops(False)
        self.treeCatalog.setAlternatingRowColors(True)
        self.treeCatalog.setObjectName("treeCatalog")
        self.gridlayout.addWidget(self.treeCatalog,0,0,1,1)
        Catalog.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(Catalog)
        self.menubar.setGeometry(QtCore.QRect(0,0,581,28))
        self.menubar.setObjectName("menubar")

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuProject = QtGui.QMenu(self.menubar)
        self.menuProject.setObjectName("menuProject")

        self.menuOpenRecentProject = QtGui.QMenu(self.menuProject)
        self.menuOpenRecentProject.setEnabled(False)
        self.menuOpenRecentProject.setObjectName("menuOpenRecentProject")

        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        Catalog.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(Catalog)
        self.statusbar.setObjectName("statusbar")
        Catalog.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(Catalog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.toolBar.setAcceptDrops(True)
        self.toolBar.setOrientation(QtCore.Qt.Horizontal)
        self.toolBar.setObjectName("toolBar")
        Catalog.addToolBar(self.toolBar)

        self.actionQuit = QtGui.QAction(Catalog)
        self.actionQuit.setIcon(QtGui.QIcon("../images/exit.png"))
        self.actionQuit.setObjectName("actionQuit")

        self.actionAbout = QtGui.QAction(Catalog)
        self.actionAbout.setObjectName("actionAbout")

        self.actionAboutQt = QtGui.QAction(Catalog)
        self.actionAboutQt.setObjectName("actionAboutQt")

        self.actionReload = QtGui.QAction(Catalog)
        self.actionReload.setEnabled(False)
        self.actionReload.setIcon(QtGui.QIcon("../images/reload.png"))
        self.actionReload.setObjectName("actionReload")

        self.actionConfigure = QtGui.QAction(Catalog)
        self.actionConfigure.setIcon(QtGui.QIcon("../images/configure.png"))
        self.actionConfigure.setObjectName("actionConfigure")

        self.actionFind_in_Files = QtGui.QAction(Catalog)
        self.actionFind_in_Files.setEnabled(False)
        self.actionFind_in_Files.setIcon(QtGui.QIcon("../images/find.png"))
        self.actionFind_in_Files.setObjectName("actionFind_in_Files")

        self.actionStatistics = QtGui.QAction(Catalog)
        self.actionStatistics.setEnabled(False)
        self.actionStatistics.setIcon(QtGui.QIcon("../images/statistic.png"))
        self.actionStatistics.setObjectName("actionStatistics")

        self.actionBuildTM = QtGui.QAction(Catalog)
        self.actionBuildTM.setObjectName("actionBuildTM")

        self.actionNew = QtGui.QAction(Catalog)
        self.actionNew.setObjectName("actionNew")

        self.actionOpen = QtGui.QAction(Catalog)
        self.actionOpen.setObjectName("actionOpen")

        self.actionBuild = QtGui.QAction(Catalog)
        self.actionBuild.setIcon(QtGui.QIcon("../images/memory.png"))
        self.actionBuild.setObjectName("actionBuild")

        self.actionConfigure1 = QtGui.QAction(Catalog)
        self.actionConfigure1.setIcon(QtGui.QIcon("../images/configure.png"))
        self.actionConfigure1.setObjectName("actionConfigure1")

        self.actionStop = QtGui.QAction(Catalog)
        self.actionStop.setEnabled(False)
        self.actionStop.setIcon(QtGui.QIcon("../images/stop.png"))
        self.actionStop.setObjectName("actionStop")
        self.menuEdit.addAction(self.actionFind_in_Files)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionStatistics)
        self.menuEdit.addAction(self.actionReload)
        self.menuFile.addAction(self.actionQuit)
        self.menuProject.addAction(self.actionNew)
        self.menuProject.addAction(self.actionOpen)
        self.menuProject.addAction(self.menuOpenRecentProject.menuAction())
        self.menuSettings.addAction(self.actionBuild)
        self.menuSettings.addAction(self.actionConfigure)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionFind_in_Files)
        self.toolBar.addAction(self.actionStatistics)
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addAction(self.actionConfigure)

        self.retranslateUi(Catalog)
        QtCore.QMetaObject.connectSlotsByName(Catalog)

    def tr(self, string):
        return QtGui.QApplication.translate("Catalog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Catalog):
        Catalog.setWindowTitle(self.tr("Catalog Manager"))
        self.menuEdit.setTitle(self.tr("&Edit"))
        self.menuFile.setTitle(self.tr("&File"))
        self.menuProject.setTitle(self.tr("&Project"))
        self.menuOpenRecentProject.setToolTip(self.tr("This open recent project."))
        self.menuOpenRecentProject.setStatusTip(self.tr("This open recent project."))
        self.menuOpenRecentProject.setWhatsThis(self.tr("<h3>Open recent project</h3>Use this to be asked for the name exist of project in catalog manager."))
        self.menuOpenRecentProject.setTitle(self.tr("Open &Recent Project"))
        self.menuSettings.setTitle(self.tr("&Settings"))
        self.menuHelp.setTitle(self.tr("&Help"))
        self.actionQuit.setText(self.tr("&Quit"))
        self.actionQuit.setStatusTip(self.tr("Quit the application."))
        self.actionQuit.setWhatsThis(self.tr("<h3>Quit</h3>Use this to quit the application. Any unsaved changes will be prompted."))
        self.actionQuit.setShortcut(self.tr("Ctrl+Q"))
        self.actionAbout.setText(self.tr("About"))
        self.actionAbout.setStatusTip(self.tr("Display information about this software."))
        self.actionAbout.setWhatsThis(self.tr("Display information about this software."))
        self.actionAboutQt.setText(self.tr("About Qt"))
        self.actionAboutQt.setStatusTip(self.tr("Display information about the Qt toolkit."))
        self.actionAboutQt.setWhatsThis(self.tr("Display information about the Qt toolkit."))
        self.actionReload.setText(self.tr("&Reload"))
        self.actionReload.setShortcut(self.tr("F5"))
        self.actionConfigure.setText(self.tr("&Configure..."))
        self.actionFind_in_Files.setText(self.tr("&Find in Files..."))
        self.actionFind_in_Files.setStatusTip(self.tr("Find text in the shown strings."))
        self.actionFind_in_Files.setWhatsThis(self.tr("<h3>Find</h3>Use this to find text in the shown strings. The find dialog will show at the bottom of the editor."))
        self.actionFind_in_Files.setShortcut(self.tr("Ctrl+F"))
        self.actionStatistics.setText(self.tr("&Statistics"))
        self.actionStatistics.setShortcut(self.tr("Ctrl+S"))
        self.actionBuildTM.setText(self.tr("&Build TM"))
        self.actionNew.setText(self.tr("New..."))
        self.actionNew.setStatusTip(self.tr("This opens a dialog for entering  the information for a new project."))
        self.actionNew.setWhatsThis(self.tr("<h3>New...</h3>Use this to open a dialog for entering  the information for a new project."))
        self.actionOpen.setText(self.tr("Open..."))
        self.actionOpen.setStatusTip(self.tr("This open an existing project."))
        self.actionOpen.setWhatsThis(self.tr("<h3>Open</h3>Use this to open an existing project."))
        self.actionBuild.setText(self.tr("Build TM..."))
        self.actionBuild.setToolTip(self.tr("Build the translation memory."))
        self.actionBuild.setStatusTip(self.tr("Build the translation memory."))
        self.actionBuild.setWhatsThis(self.tr("<h3>Build TM</h3>Use this to build the translation memory."))
        self.actionConfigure1.setText(self.tr("Configure..."))
        self.actionStop.setText(self.tr("Stop"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Catalog = QtGui.QMainWindow()
    ui = Ui_Catalog()
    ui.setupUi(Catalog)
    Catalog.show()
    sys.exit(app.exec_())
