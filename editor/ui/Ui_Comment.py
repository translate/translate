# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Dec  1 10:02:14 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmComment(object):
    def setupUi(self, frmComment):
        frmComment.setObjectName("frmComment")
        frmComment.resize(QtCore.QSize(QtCore.QRect(0,0,171,231).size()).expandedTo(frmComment.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmComment.sizePolicy().hasHeightForWidth())
        frmComment.setSizePolicy(sizePolicy)
        frmComment.setMinimumSize(QtCore.QSize(150,50))
        frmComment.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.gridlayout = QtGui.QGridLayout(frmComment)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.splitter = QtGui.QSplitter(frmComment)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.txtTranslatorComment = QtGui.QTextEdit(self.splitter)
        self.txtTranslatorComment.setEnabled(False)
        self.txtTranslatorComment.setMinimumSize(QtCore.QSize(0,0))
        self.txtTranslatorComment.setObjectName("txtTranslatorComment")

        self.txtLocationComment = QtGui.QTextEdit(self.splitter)
        self.txtLocationComment.setObjectName("txtLocationComment")
        self.gridlayout.addWidget(self.splitter,0,0,1,1)

        self.retranslateUi(frmComment)
        QtCore.QMetaObject.connectSlotsByName(frmComment)

    def tr(self, string):
        return QtGui.QApplication.translate("frmComment", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmComment):
        frmComment.setWindowTitle(self.tr("Comments"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    frmComment = QtGui.QWidget()
    ui = Ui_frmComment()
    ui.setupUi(frmComment)
    frmComment.show()
    sys.exit(app.exec_())
