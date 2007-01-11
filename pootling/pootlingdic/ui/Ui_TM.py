# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Thu Jan 11 08:15:42 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,433,393).size()).expandedTo(Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.lineFile = QtGui.QLineEdit(self.frame)
        self.lineFile.setGeometry(QtCore.QRect(20,40,271,22))
        self.lineFile.setObjectName("lineFile")

        self.chkScan = QtGui.QCheckBox(self.frame)
        self.chkScan.setGeometry(QtCore.QRect(20,75,121,21))
        self.chkScan.setObjectName("chkScan")

        self.lineDatabase = QtGui.QLineEdit(self.frame)
        self.lineDatabase.setGeometry(QtCore.QRect(20,137,271,22))
        self.lineDatabase.setObjectName("lineDatabase")

        self.proBar = QtGui.QProgressBar(self.frame)
        self.proBar.setGeometry(QtCore.QRect(20,247,271,23))
        self.proBar.setProperty("value",QtCore.QVariant(24))
        self.proBar.setOrientation(QtCore.Qt.Horizontal)
        self.proBar.setObjectName("proBar")

        self.btnGenerate = QtGui.QPushButton(self.frame)
        self.btnGenerate.setGeometry(QtCore.QRect(310,247,85,26))
        self.btnGenerate.setObjectName("btnGenerate")

        self.btnBrowseDatabase = QtGui.QPushButton(self.frame)
        self.btnBrowseDatabase.setGeometry(QtCore.QRect(310,137,85,26))
        self.btnBrowseDatabase.setObjectName("btnBrowseDatabase")

        self.btnBrowseFile = QtGui.QPushButton(self.frame)
        self.btnBrowseFile.setGeometry(QtCore.QRect(310,40,85,26))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowseFile.sizePolicy().hasHeightForWidth())
        self.btnBrowseFile.setSizePolicy(sizePolicy)
        self.btnBrowseFile.setObjectName("btnBrowseFile")

        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(20,20,145,21))

        font = QtGui.QFont(self.label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(20,117,112,21))

        font = QtGui.QFont(self.label_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(20,220,104,21))

        font = QtGui.QFont(self.label_3.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.chkrepeated = QtGui.QCheckBox(self.frame)
        self.chkrepeated.setGeometry(QtCore.QRect(20,171,171,23))
        self.chkrepeated.setObjectName("chkrepeated")
        self.gridlayout.addWidget(self.frame,0,0,2,2)

        spacerItem = QtGui.QSpacerItem(20,61,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,1,1,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem1 = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)

        self.btnok = QtGui.QPushButton(Dialog)
        self.btnok.setObjectName("btnok")
        self.hboxlayout.addWidget(self.btnok)

        self.btncancel = QtGui.QPushButton(Dialog)
        self.btncancel.setObjectName("btncancel")
        self.hboxlayout.addWidget(self.btncancel)
        self.gridlayout.addLayout(self.hboxlayout,2,0,1,2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Dialog"))
        self.chkScan.setText(self.tr("Scan all folders"))
        self.btnGenerate.setText(self.tr("Generate"))
        self.btnBrowseDatabase.setText(self.tr("Browse..."))
        self.btnBrowseFile.setText(self.tr("Browse..."))
        self.label.setText(self.tr("Path to translated file"))
        self.label_2.setText(self.tr("Database folder"))
        self.label_3.setText(self.tr("Total progress:"))
        self.chkrepeated.setText(self.tr("Repeat source string"))
        self.btnok.setText(self.tr("OK"))
        self.btncancel.setText(self.tr("Cancel"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
