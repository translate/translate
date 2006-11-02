# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Oct 18 17:05:14 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmHeader(object):
    def setupUi(self, frmHeader):
        frmHeader.setObjectName("frmHeader")
        frmHeader.resize(QtCore.QSize(QtCore.QRect(0,0,426,388).size()).expandedTo(frmHeader.minimumSizeHint()))
        frmHeader.setSizeGripEnabled(True)
        frmHeader.setModal(True)

        self.gridlayout = QtGui.QGridLayout(frmHeader)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(frmHeader)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.txtHeader = QtGui.QTextEdit(frmHeader)
        self.txtHeader.setEnabled(True)
        self.txtHeader.setMouseTracking(False)
        self.txtHeader.setReadOnly(True)
        self.txtHeader.setObjectName("txtHeader")
        self.gridlayout.addWidget(self.txtHeader,3,0,1,1)

        self.txtOtherComments = QtGui.QTextEdit(frmHeader)
        self.txtOtherComments.setObjectName("txtOtherComments")
        self.gridlayout.addWidget(self.txtOtherComments,1,0,1,1)

        self.label_2 = QtGui.QLabel(frmHeader)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,2,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.resetButton = QtGui.QPushButton(frmHeader)
        self.resetButton.setEnabled(True)
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
        self.gridlayout.addLayout(self.hboxlayout,4,0,1,1)

        self.retranslateUi(frmHeader)
        QtCore.QObject.connect(self.okButton,QtCore.SIGNAL("clicked()"),frmHeader.accept)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),frmHeader.reject)
        QtCore.QMetaObject.connectSlotsByName(frmHeader)

    def tr(self, string):
        return QtGui.QApplication.translate("frmHeader", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmHeader):
        frmHeader.setWindowTitle(self.tr("Header"))
        self.label.setText(self.tr("Comment"))
        self.label_2.setText(self.tr("Header"))
        self.resetButton.setText(self.tr("Reset"))
        self.applyButton.setText(self.tr("Apply Settings"))
        self.okButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
