# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jhe/khmerOS/svn-wordforge/trunk/editor/ui/TUview.ui'
#
# Created: Thu Nov 30 21:43:27 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_TUview(object):
    def setupUi(self, TUview):
        TUview.setObjectName("TUview")
        TUview.setEnabled(True)
        TUview.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(TUview.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TUview.sizePolicy().hasHeightForWidth())
        TUview.setSizePolicy(sizePolicy)
        TUview.setMinimumSize(QtCore.QSize(200,140))
        TUview.setFocusPolicy(QtCore.Qt.NoFocus)
        TUview.setAutoFillBackground(True)

        self.hboxlayout = QtGui.QHBoxLayout(TUview)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(0)
        self.hboxlayout.setObjectName("hboxlayout")

        self.splitter = QtGui.QSplitter(TUview)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setOpaqueResize(True)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")

        self.txtSource = QtGui.QTextEdit(self.splitter)
        self.txtSource.setTabChangesFocus(True)
        self.txtSource.setUndoRedoEnabled(False)
        self.txtSource.setReadOnly(True)
        self.txtSource.setTabStopWidth(79)
        self.txtSource.setObjectName("txtSource")

        self.lblComment = QtGui.QLabel(self.splitter)
        self.lblComment.setTextFormat(QtCore.Qt.PlainText)
        self.lblComment.setObjectName("lblComment")

        self.txtTarget = QtGui.QTextEdit(self.splitter)
        self.txtTarget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.txtTarget.setObjectName("txtTarget")
        self.hboxlayout.addWidget(self.splitter)

        spacerItem = QtGui.QSpacerItem(5,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

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
        self.hboxlayout.addWidget(self.fileScrollBar)

        self.retranslateUi(TUview)
        QtCore.QMetaObject.connectSlotsByName(TUview)
        TUview.setTabOrder(self.txtSource,self.txtTarget)

    def retranslateUi(self, TUview):
        TUview.setWindowTitle(QtGui.QApplication.translate("TUview", "Detail", None, QtGui.QApplication.UnicodeUTF8))
        self.fileScrollBar.setToolTip(QtGui.QApplication.translate("TUview", "Navigate in your file", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    TUview = QtGui.QWidget()
    ui = Ui_TUview()
    ui.setupUi(TUview)
    TUview.show()
    sys.exit(app.exec_())
