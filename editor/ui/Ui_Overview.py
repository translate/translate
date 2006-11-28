# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Tue Nov 28 10:00:44 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,562,487).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(1)
        self.gridlayout.setSpacing(1)
        self.gridlayout.setObjectName("gridlayout")

        self.tableOverview = QtGui.QTableWidget(Form)
        self.tableOverview.setEnabled(False)
        self.tableOverview.setTabKeyNavigation(False)
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
        self.tableOverview.setRowCount(0)
        self.tableOverview.clear()
        self.tableOverview.setColumnCount(0)
        self.tableOverview.setRowCount(0)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
