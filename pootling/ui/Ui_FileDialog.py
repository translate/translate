# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Feb  5 14:09:05 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,400,231).size()).expandedTo(Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.lineLocation = QtGui.QLineEdit(Dialog)
        self.lineLocation.setObjectName("lineLocation")
        self.gridlayout.addWidget(self.lineLocation,1,0,1,3)

        self.treeView = QtGui.QTreeView(Dialog)
        self.treeView.setObjectName("treeView")
        self.gridlayout.addWidget(self.treeView,0,0,1,3)

        spacerItem = QtGui.QSpacerItem(201,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,2,0,1,1)

        self.btnQuit = QtGui.QPushButton(Dialog)
        self.btnQuit.setObjectName("btnQuit")
        self.gridlayout.addWidget(self.btnQuit,2,2,1,1)

        self.btnAdd = QtGui.QPushButton(Dialog)
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout.addWidget(self.btnAdd,2,1,1,1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Select a file or a location"))
        self.btnQuit.setText(self.tr("&Quit"))
        self.btnAdd.setText(self.tr("&Add"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
