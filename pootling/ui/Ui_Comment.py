# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Dec  6 16:53:57 2006
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
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.splitter = QtGui.QSplitter(frmComment)
        self.splitter.setMinimumSize(QtCore.QSize(16,20))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")

        self.txtTranslatorComment = QtGui.QTextEdit(self.splitter)
        self.txtTranslatorComment.setEnabled(False)
        self.txtTranslatorComment.setMinimumSize(QtCore.QSize(0,0))
        self.txtTranslatorComment.setObjectName("txtTranslatorComment")

        self.txtLocationComment = QtGui.QTextEdit(self.splitter)

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
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(9),QtGui.QColor(225,219,255))
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
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(9),QtGui.QColor(225,219,255))
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
        self.txtLocationComment.setPalette(palette)
        self.txtLocationComment.setReadOnly(True)
        self.txtLocationComment.setObjectName("txtLocationComment")
        self.gridlayout.addWidget(self.splitter,0,0,1,1)

        self.retranslateUi(frmComment)
        QtCore.QMetaObject.connectSlotsByName(frmComment)

    def tr(self, string):
        return QtGui.QApplication.translate("frmComment", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmComment):
        frmComment.setWindowTitle(self.tr("Comments"))
        self.txtTranslatorComment.setToolTip(self.tr("Translators\' comments"))
        self.txtLocationComment.setToolTip(self.tr("String\'s location"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    frmComment = QtGui.QWidget()
    ui = Ui_frmComment()
    ui.setupUi(frmComment)
    frmComment.show()
    sys.exit(app.exec_())
