# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Mar 26 10:25:17 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(Form.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,2,0,1,1)

        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,0,1,1)

        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4,3,0,1,1)

        self.lblTranslator = QtGui.QLabel(Form)
        self.lblTranslator.setObjectName("lblTranslator")
        self.gridlayout.addWidget(self.lblTranslator,2,1,1,1)

        self.lblPath = QtGui.QLabel(Form)
        self.lblPath.setObjectName("lblPath")
        self.gridlayout.addWidget(self.lblPath,0,1,1,1)

        self.lblFile = QtGui.QLabel(Form)
        self.lblFile.setObjectName("lblFile")
        self.gridlayout.addWidget(self.lblFile,1,1,1,1)

        self.lblDate = QtGui.QLabel(Form)
        self.lblDate.setObjectName("lblDate")
        self.gridlayout.addWidget(self.lblDate,3,1,1,1)

        self.tblTM = QtGui.QTableWidget(Form)
        self.tblTM.setObjectName("tblTM")
        self.gridlayout.addWidget(self.tblTM,4,0,1,2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        Form.setWindowTitle(self.tr("Lookup"))
        self.label_3.setText(self.tr("Translator:"))
        self.label_2.setText(self.tr("Found file:"))
        self.label.setText(self.tr("Found path:"))
        self.label_4.setText(self.tr("Date:"))
        self.tblTM.setRowCount(0)
        self.tblTM.setColumnCount(2)
        self.tblTM.clear()
        self.tblTM.setColumnCount(2)
        self.tblTM.setRowCount(0)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
