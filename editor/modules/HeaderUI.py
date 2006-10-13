# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Oct  4 14:56:40 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmHeader(object):
    def setupUi(self, frmHeader):
        frmHeader.setObjectName("frmHeader")
        frmHeader.resize(QtCore.QSize(QtCore.QRect(0,0,426,388).size()).expandedTo(frmHeader.minimumSizeHint()))
##        frmHeader.setSizeGripEnabled(True)
##        frmHeader.setModal(True)

        self.gridlayout = QtGui.QGridLayout(frmHeader)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.resetButton = QtGui.QPushButton(frmHeader)
        self.resetButton.setObjectName("resetButton")
        self.hboxlayout.addWidget(self.resetButton)

        self.applyButton = QtGui.QPushButton(frmHeader)
        self.applyButton.setObjectName("applyButton")
        self.hboxlayout.addWidget(self.applyButton)

        spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.okButton = QtGui.QPushButton(frmHeader)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton(frmHeader)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self.gridlayout.addLayout(self.hboxlayout,1,0,1,1)

        self.txtHeader = QtGui.QTextEdit(frmHeader)
        self.txtHeader.setMouseTracking(False)
        self.txtHeader.setObjectName("txtHeader")
        self.gridlayout.addWidget(self.txtHeader,0,0,1,1)

        self.retranslateUi(frmHeader)
        QtCore.QMetaObject.connectSlotsByName(frmHeader)

    def tr(self, string):
        return QtGui.QApplication.translate("frmHeader", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmHeader):
        frmHeader.setWindowTitle(self.tr("Header"))
        self.resetButton.setText(self.tr("Reset"))
        self.applyButton.setText(self.tr("Apply Settings"))
        self.okButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
