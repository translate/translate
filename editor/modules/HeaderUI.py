# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Sep 27 10:07:57 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmHeader(object):
    def setupUi(self, frmHeader):
        frmHeader.setObjectName("frmHeader")
        frmHeader.resize(QtCore.QSize(QtCore.QRect(0,0,534,395).size()).expandedTo(frmHeader.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(frmHeader)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.txtHeader = QtGui.QTextEdit(frmHeader)
        self.txtHeader.setObjectName("txtHeader")
        self.gridlayout.addWidget(self.txtHeader,0,0,1,1)

        self.retranslateUi(frmHeader)
        QtCore.QMetaObject.connectSlotsByName(frmHeader)

    def tr(self, string):
        return QtGui.QApplication.translate("frmHeader", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmHeader):
        frmHeader.setWindowTitle(self.tr("Header"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    frmHeader = QtGui.QWidget()
    ui = Ui_frmHeader()
    ui.setupUi(frmHeader)
    frmHeader.show()
    sys.exit(app.exec_())
