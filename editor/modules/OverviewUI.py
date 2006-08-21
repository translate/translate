# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Aug 14 13:59:20 2006

#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,399,277).size()).expandedTo(Form.minimumSizeHint()))
        Form.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.treeOverview = QtGui.QTreeWidget(Form)
        self.treeOverview.setAlternatingRowColors(True)
        self.treeOverview.setIndentation(0)
        self.treeOverview.setColumnCount(3)
        self.treeOverview.setSortingEnabled(True)
        self.treeOverview.setObjectName("treeOverview")
        self.gridlayout.addWidget(self.treeOverview,0,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        Form.setWindowTitle(self.tr("Form"))
        self.treeOverview.headerItem().setText(0,self.tr("Id"))
        self.treeOverview.headerItem().setText(1,self.tr("Source"))
        self.treeOverview.headerItem().setText(2,self.tr("Target"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
