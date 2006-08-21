# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Thu Aug 10 12:01:25 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmComment(object):
    def setupUi(self, frmComment):
        frmComment.setObjectName("frmComment")
        frmComment.resize(QtCore.QSize(QtCore.QRect(0,0,534,395).size()).expandedTo(frmComment.minimumSizeHint()))
        frmComment.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.gridlayout = QtGui.QGridLayout(frmComment)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.txtComment = QtGui.QTextEdit(frmComment)
        self.txtComment.setObjectName("txtComment")
        self.gridlayout.addWidget(self.txtComment,0,0,1,1)

        self.retranslateUi(frmComment)
        QtCore.QMetaObject.connectSlotsByName(frmComment)

    def tr(self, string):
        return QtGui.QApplication.translate("frmComment", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmComment):
        frmComment.setWindowTitle(self.tr("Comments"))
