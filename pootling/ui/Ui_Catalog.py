# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/Catalog.ui'
#
# Created: Fri Mar 30 17:21:32 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Catalog(object):
    def setupUi(self, Catalog):
        Catalog.setObjectName("Catalog")
        Catalog.resize(QtCore.QSize(QtCore.QRect(0,0,531,400).size()).expandedTo(Catalog.minimumSizeHint()))

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
        self.treeCatalog.setAlternatingRowColors(True)
        self.treeCatalog.setObjectName("treeCatalog")
        self.gridlayout.addWidget(self.treeCatalog,0,0,1,1)
        Catalog.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(Catalog)
        self.menubar.setGeometry(QtCore.QRect(0,0,531,28))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menuProject = QtGui.QMenu(self.menubar)
        self.menuProject.setObjectName("menuProject")

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        Catalog.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(Catalog)
        self.statusbar.setObjectName("statusbar")
        Catalog.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(Catalog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
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
        self.actionFind_in_Files.setEnabled(True)
        self.actionFind_in_Files.setIcon(QtGui.QIcon("../images/find.png"))
        self.actionFind_in_Files.setObjectName("actionFind_in_Files")

        self.actionStatistics = QtGui.QAction(Catalog)
        self.actionStatistics.setIcon(QtGui.QIcon("../images/statistic.png"))
        self.actionStatistics.setObjectName("actionStatistics")

        self.actionBuildTM = QtGui.QAction(Catalog)
        self.actionBuildTM.setObjectName("actionBuildTM")
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuProject.addAction(self.actionConfigure)
        self.menuProject.addAction(self.actionBuildTM)
        self.menuEdit.addAction(self.actionFind_in_Files)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionStatistics)
        self.menuEdit.addAction(self.actionReload)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionQuit)
        self.toolBar.addAction(self.actionFind_in_Files)
        self.toolBar.addAction(self.actionStatistics)
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionConfigure)

        self.retranslateUi(Catalog)
        QtCore.QMetaObject.connectSlotsByName(Catalog)

    def retranslateUi(self, Catalog):
        Catalog.setWindowTitle(QtGui.QApplication.translate("Catalog", "Catalog Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("Catalog", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("Catalog", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuProject.setTitle(QtGui.QApplication.translate("Catalog", "&Project", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("Catalog", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
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



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Catalog = QtGui.QMainWindow()
    ui = Ui_Catalog()
    ui.setupUi(Catalog)
    Catalog.show()
    sys.exit(app.exec_())
