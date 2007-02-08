# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Feb  7 17:02:03 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Catalog(object):
    def setupUi(self, Catalog):
        Catalog.setObjectName("Catalog")
        Catalog.resize(QtCore.QSize(QtCore.QRect(0,0,531,400).size()).expandedTo(Catalog.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(Catalog)
        self.centralwidget.setObjectName("centralwidget")

        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")

        self.tableCatalog = QtGui.QTableWidget(self.centralwidget)
        self.tableCatalog.setObjectName("tableCatalog")
        self.gridlayout.addWidget(self.tableCatalog,0,0,1,1)
        Catalog.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(Catalog)
        self.menubar.setGeometry(QtCore.QRect(0,0,531,28))
        self.menubar.setObjectName("menubar")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuProject = QtGui.QMenu(self.menubar)
        self.menuProject.setObjectName("menuProject")
        Catalog.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(Catalog)
        self.statusbar.setGeometry(QtCore.QRect(0,379,531,21))
        self.statusbar.setObjectName("statusbar")
        Catalog.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(Catalog)
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
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuEdit.addAction(self.actionReload)
        self.menuFile.addAction(self.actionQuit)
        self.menuProject.addAction(self.actionConfigure)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionConfigure)

        self.retranslateUi(Catalog)
        QtCore.QMetaObject.connectSlotsByName(Catalog)

    def tr(self, string):
        return QtGui.QApplication.translate("Catalog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Catalog):
        Catalog.setWindowTitle(self.tr("Catalog Manager"))
        self.tableCatalog.clear()
        self.tableCatalog.setColumnCount(0)
        self.tableCatalog.setRowCount(0)
        self.menuHelp.setTitle(self.tr("&Help"))
        self.menuEdit.setTitle(self.tr("&Edit"))
        self.menuFile.setTitle(self.tr("&File"))
        self.menuProject.setTitle(self.tr("&Project"))
        self.actionQuit.setText(self.tr("&Quit"))
        self.actionQuit.setShortcut(self.tr("Ctrl+Q"))
        self.actionAbout.setText(self.tr("About"))
        self.actionAboutQt.setText(self.tr("About Qt"))
        self.actionReload.setText(self.tr("&Reload"))
        self.actionReload.setShortcut(self.tr("Ctrl+R"))
        self.actionConfigure.setText(self.tr("&Configure..."))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Catalog = QtGui.QMainWindow()
    ui = Ui_Catalog()
    ui.setupUi(Catalog)
    Catalog.show()
    sys.exit(app.exec_())
