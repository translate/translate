# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Jan 24 16:02:59 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_TUview(object):
    def setupUi(self, TUview):
        TUview.setObjectName("TUview")
        TUview.setEnabled(True)
        TUview.resize(QtCore.QSize(QtCore.QRect(0,0,427,292).size()).expandedTo(TUview.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(13),QtGui.QSizePolicy.Policy(13))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TUview.sizePolicy().hasHeightForWidth())
        TUview.setSizePolicy(sizePolicy)
        TUview.setMaximumSize(QtCore.QSize(16777187,16777215))
        TUview.setFocusPolicy(QtCore.Qt.NoFocus)
        TUview.setAutoFillBackground(True)

        self.gridlayout = QtGui.QGridLayout(TUview)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.fileScrollBar = QtGui.QScrollBar(TUview)
        self.fileScrollBar.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileScrollBar.sizePolicy().hasHeightForWidth())
        self.fileScrollBar.setSizePolicy(sizePolicy)
        self.fileScrollBar.setMaximum(0)
        self.fileScrollBar.setTracking(False)
        self.fileScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.fileScrollBar.setObjectName("fileScrollBar")
        self.gridlayout.addWidget(self.fileScrollBar,0,2,3,1)

        spacerItem = QtGui.QSpacerItem(16,588,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,0,1,3,1)

        self.lblComment = QtGui.QLabel(TUview)
        self.lblComment.setObjectName("lblComment")
        self.gridlayout.addWidget(self.lblComment,1,0,1,1)

        self.txtSource = QtGui.QTextEdit(TUview)
        self.txtSource.setTabChangesFocus(True)
        self.txtSource.setUndoRedoEnabled(False)
        self.txtSource.setReadOnly(True)
        self.txtSource.setTabStopWidth(79)
        self.txtSource.setObjectName("txtSource")
        self.gridlayout.addWidget(self.txtSource,0,0,1,1)

        self.txtTarget = QtGui.QTextEdit(TUview)
        self.txtTarget.setObjectName("txtTarget")
        self.gridlayout.addWidget(self.txtTarget,2,0,1,1)

        self.retranslateUi(TUview)
        QtCore.QMetaObject.connectSlotsByName(TUview)

    def tr(self, string):
        return QtGui.QApplication.translate("TUview", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, TUview):
        TUview.setWindowTitle(self.tr("Detail"))
        self.fileScrollBar.setToolTip(self.tr("Navigate in your file"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    TUview = QtGui.QWidget()
    ui = Ui_TUview()
    ui.setupUi(TUview)
    TUview.show()
    sys.exit(app.exec_())
