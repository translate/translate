# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/Catalog.ui'
#
# Created: Wed Jun 20 16:10:43 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

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

        font = QtGui.QFont()
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

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")

        self.menuProject = QtGui.QMenu(self.menubar)
        self.menuProject.setObjectName("menuProject")

        self.menuOpenRecentProject = QtGui.QMenu(self.menuProject)
        self.menuOpenRecentProject.setEnabled(False)
        self.menuOpenRecentProject.setObjectName("menuOpenRecentProject")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
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
        self.menuEdit.addAction(self.actionFind_in_Files)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionStatistics)
        self.menuEdit.addAction(self.actionReload)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuSettings.addAction(self.actionBuild)
        self.menuSettings.addAction(self.actionConfigure)
        self.menuProject.addAction(self.actionNew)
        self.menuProject.addAction(self.actionOpen)
        self.menuProject.addAction(self.menuOpenRecentProject.menuAction())
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionFind_in_Files)
        self.toolBar.addAction(self.actionStatistics)
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionConfigure)

        self.retranslateUi(Catalog)
        QtCore.QMetaObject.connectSlotsByName(Catalog)

    def retranslateUi(self, Catalog):
        Catalog.setWindowTitle(QtGui.QApplication.translate("Catalog", "Catalog Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("Catalog", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("Catalog", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("Catalog", "&Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuProject.setTitle(QtGui.QApplication.translate("Catalog", "&Project", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOpenRecentProject.setTitle(QtGui.QApplication.translate("Catalog", "Open &Recent Project", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("Catalog", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("Catalog", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("Catalog", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("Catalog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAboutQt.setText(QtGui.QApplication.translate("Catalog", "About Qt", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReload.setText(QtGui.QApplication.translate("Catalog", "&Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReload.setShortcut(QtGui.QApplication.translate("Catalog", "F5", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConfigure.setText(QtGui.QApplication.translate("Catalog", "&Configure...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFind_in_Files.setText(QtGui.QApplication.translate("Catalog", "&Find in Files...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFind_in_Files.setShortcut(QtGui.QApplication.translate("Catalog", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStatistics.setText(QtGui.QApplication.translate("Catalog", "&Statistics", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStatistics.setShortcut(QtGui.QApplication.translate("Catalog", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBuildTM.setText(QtGui.QApplication.translate("Catalog", "&Build TM", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("Catalog", "New...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("Catalog", "Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBuild.setText(QtGui.QApplication.translate("Catalog", "Build TM...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConfigure1.setText(QtGui.QApplication.translate("Catalog", "Configure...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Catalog = QtGui.QMainWindow()
    ui = Ui_Catalog()
    ui.setupUi(Catalog)
    Catalog.show()
    sys.exit(app.exec_())
