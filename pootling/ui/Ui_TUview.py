# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Tue Jan 23 15:27:08 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_TUview(object):
    def setupUi(self, TUview):
        TUview.setObjectName("TUview")
        TUview.setEnabled(True)
        TUview.resize(QtCore.QSize(QtCore.QRect(0,0,417,280).size()).expandedTo(TUview.minimumSizeHint()))

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

        spacerItem = QtGui.QSpacerItem(16,588,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,0,1,3,1)

        self.lblComment = QtGui.QLabel(TUview)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(0),QtGui.QColor(255,24,35))
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
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(0),QtGui.QColor(255,24,35))
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
        self.lblComment.setPalette(palette)
        self.lblComment.setObjectName("lblComment")
        self.gridlayout.addWidget(self.lblComment,1,0,1,1)

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

        self.tabSource = QtGui.QTabWidget(TUview)
        self.tabSource.setObjectName("tabSource")

        self.tabSourceSingle = QtGui.QWidget()
        self.tabSourceSingle.setObjectName("tabSourceSingle")

        self.gridlayout1 = QtGui.QGridLayout(self.tabSourceSingle)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.txtSource = QtGui.QTextEdit(self.tabSourceSingle)
        self.txtSource.setTabChangesFocus(True)
        self.txtSource.setUndoRedoEnabled(False)
        self.txtSource.setReadOnly(True)
        self.txtSource.setTabStopWidth(79)
        self.txtSource.setObjectName("txtSource")
        self.gridlayout1.addWidget(self.txtSource,0,0,1,1)
        self.tabSource.addTab(self.tabSourceSingle, "")
        self.gridlayout.addWidget(self.tabSource,0,0,1,1)

        self.tabTarget = QtGui.QTabWidget(TUview)
        self.tabTarget.setObjectName("tabTarget")

        self.tabTargetSingle = QtGui.QWidget()
        self.tabTargetSingle.setObjectName("tabTargetSingle")

        self.gridlayout2 = QtGui.QGridLayout(self.tabTargetSingle)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.txtTarget = QtGui.QTextEdit(self.tabTargetSingle)
        self.txtTarget.setObjectName("txtTarget")
        self.gridlayout2.addWidget(self.txtTarget,0,0,1,1)
        self.tabTarget.addTab(self.tabTargetSingle, "")
        self.gridlayout.addWidget(self.tabTarget,2,0,1,1)

        self.retranslateUi(TUview)
        self.tabSource.setCurrentIndex(0)
        self.tabTarget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TUview)

    def tr(self, string):
        return QtGui.QApplication.translate("TUview", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, TUview):
        TUview.setWindowTitle(self.tr("Detail"))
        self.fileScrollBar.setToolTip(self.tr("Navigate in your file"))
        self.tabSource.setTabText(self.tabSource.indexOf(self.tabSourceSingle), self.tr("Singular"))
        self.tabTarget.setTabText(self.tabTarget.indexOf(self.tabTargetSingle), self.tr("Singular"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    TUview = QtGui.QWidget()
    ui = Ui_TUview()
    ui.setupUi(TUview)
    TUview.show()
    sys.exit(app.exec_())
