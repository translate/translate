# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Nov 29 17:10:14 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_TUview(object):
    def setupUi(self, TUview):
        TUview.setObjectName("TUview")
        TUview.setEnabled(True)
        TUview.resize(QtCore.QSize(QtCore.QRect(0,0,478,354).size()).expandedTo(TUview.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TUview.sizePolicy().hasHeightForWidth())
        TUview.setSizePolicy(sizePolicy)
        TUview.setMinimumSize(QtCore.QSize(0,0))
        TUview.setFocusPolicy(QtCore.Qt.NoFocus)
        TUview.setAutoFillBackground(True)

        self.hboxlayout = QtGui.QHBoxLayout(TUview)
        self.hboxlayout.setMargin(2)
        self.hboxlayout.setSpacing(10)
        self.hboxlayout.setObjectName("hboxlayout")

        self.splitter_2 = QtGui.QSplitter(TUview)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setChildrenCollapsible(False)
        self.splitter_2.setObjectName("splitter_2")

        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")

        self.txtSource = QtGui.QTextEdit(self.splitter)
        self.txtSource.setEnabled(False)
        self.txtSource.setMinimumSize(QtCore.QSize(0,20))

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(0),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(1),QtGui.QColor(221,223,228))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(3),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(4),QtGui.QColor(85,85,85))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(5),QtGui.QColor(199,199,199))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(6),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(8),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(9),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),QtGui.QColor(239,239,239))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(12),QtGui.QColor(103,141,178))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,238))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(15),QtGui.QColor(82,24,139))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(0),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(1),QtGui.QColor(221,223,228))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(3),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(4),QtGui.QColor(85,85,85))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(5),QtGui.QColor(199,199,199))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(6),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(8),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(9),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),QtGui.QColor(239,239,239))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(12),QtGui.QColor(103,141,178))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,238))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(15),QtGui.QColor(82,24,139))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(0),QtGui.QColor(128,128,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(1),QtGui.QColor(221,223,228))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(3),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(4),QtGui.QColor(85,85,85))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(5),QtGui.QColor(199,199,199))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(6),QtGui.QColor(199,199,199))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(8),QtGui.QColor(128,128,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(9),QtGui.QColor(239,239,239))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),QtGui.QColor(239,239,239))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(12),QtGui.QColor(86,117,148))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,238))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(15),QtGui.QColor(82,24,139))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        self.txtSource.setPalette(palette)
        self.txtSource.setTabChangesFocus(True)
        self.txtSource.setUndoRedoEnabled(False)
        self.txtSource.setReadOnly(True)
        self.txtSource.setTabStopWidth(79)
        self.txtSource.setObjectName("txtSource")

        self.lblComment = QtGui.QLabel(self.splitter)
        self.lblComment.setMinimumSize(QtCore.QSize(0,20))
        self.lblComment.setTextFormat(QtCore.Qt.PlainText)
        self.lblComment.setObjectName("lblComment")

        self.txtTarget = QtGui.QTextEdit(self.splitter_2)
        self.txtTarget.setEnabled(False)
        self.txtTarget.setMinimumSize(QtCore.QSize(0,20))
        self.txtTarget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.txtTarget.setObjectName("txtTarget")
        self.hboxlayout.addWidget(self.splitter_2)

        self.fileScrollBar = QtGui.QScrollBar(TUview)
        self.fileScrollBar.setEnabled(False)
        self.fileScrollBar.setMaximum(0)
        self.fileScrollBar.setTracking(False)
        self.fileScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.fileScrollBar.setObjectName("fileScrollBar")
        self.hboxlayout.addWidget(self.fileScrollBar)

        self.retranslateUi(TUview)
        QtCore.QMetaObject.connectSlotsByName(TUview)
        TUview.setTabOrder(self.txtSource,self.txtTarget)

    def tr(self, string):
        return QtGui.QApplication.translate("TUview", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, TUview):
        TUview.setWindowTitle(self.tr("Ui_TUview"))
        self.fileScrollBar.setToolTip(self.tr("Navigate in your file"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    TUview = QtGui.QWidget()
    ui = Ui_TUview()
    ui.setupUi(TUview)
    TUview.show()
    sys.exit(app.exec_())
