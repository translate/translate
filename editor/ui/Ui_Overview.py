# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Oct 23 14:47:57 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,562,487).size()).expandedTo(Form.minimumSizeHint()))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(2)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tableOverview = QtGui.QTableWidget(Form)
        self.tableOverview.setEnabled(False)
        self.tableOverview.setAlternatingRowColors(True)
        self.tableOverview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableOverview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableOverview.setShowGrid(False)
        self.tableOverview.setSortingEnabled(True)
        self.tableOverview.setObjectName("tableOverview")
        self.gridlayout.addWidget(self.tableOverview,0,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        Form.setWindowTitle(self.tr("Form"))
        self.tableOverview.clear()
        self.tableOverview.setColumnCount(3)
        self.tableOverview.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(self.tr("Index"))
        self.tableOverview.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(self.tr("Source"))
        self.tableOverview.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(self.tr("Target"))
        self.tableOverview.setHorizontalHeaderItem(2,headerItem2)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
