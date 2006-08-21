# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Tue Aug 15 10:24:37 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setEnabled(True)
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,800,30).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(800,30))
        Form.setMaximumSize(QtCore.QSize(16777215,30))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(0,0,800,29))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(800,29))
        self.frame.setMaximumSize(QtCore.QSize(16777215,30))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName("frame")

        self.lineEdit = QtGui.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(35,3,171,24))
        self.lineEdit.setObjectName("lineEdit")

        self.line_2 = QtGui.QFrame(self.frame)
        self.line_2.setGeometry(QtCore.QRect(659,5,16,21))
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setGeometry(QtCore.QRect(672,4,101,21))

        font = QtGui.QFont(self.checkBox.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.checkBox.setFont(font)
        self.checkBox.setObjectName("checkBox")

        self.line = QtGui.QFrame(self.frame)
        self.line.setGeometry(QtCore.QRect(407,6,16,20))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.pushButton_3 = QtGui.QPushButton(self.frame)
        self.pushButton_3.setGeometry(QtCore.QRect(297,5,111,21))

        font = QtGui.QFont(self.pushButton_3.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setIcon(QtGui.QIcon("../images/previous.png"))
        self.pushButton_3.setFlat(False)
        self.pushButton_3.setObjectName("pushButton_3")

        self.lblFind = QtGui.QLabel(self.frame)
        self.lblFind.setGeometry(QtCore.QRect(1,7,32,17))
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))

        font = QtGui.QFont(self.lblFind.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.lblFind.setFont(font)
        self.lblFind.setObjectName("lblFind")

        self.pushButton_4 = QtGui.QPushButton(self.frame)
        self.pushButton_4.setGeometry(QtCore.QRect(764,5,31,21))

        font = QtGui.QFont(self.pushButton_4.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setIcon(QtGui.QIcon("./images/more.png"))
        self.pushButton_4.setObjectName("pushButton_4")

        self.checkBox_2 = QtGui.QCheckBox(self.frame)
        self.checkBox_2.setGeometry(QtCore.QRect(420,5,81,21))

        font = QtGui.QFont(self.checkBox_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")

        self.pushButton_2 = QtGui.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(211,5,81,21))

        font = QtGui.QFont(self.pushButton_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setIcon(QtGui.QIcon("./images/next.png"))
        self.pushButton_2.setFlat(False)
        self.pushButton_2.setObjectName("pushButton_2")

        self.checkBox_3 = QtGui.QCheckBox(self.frame)
        self.checkBox_3.setGeometry(QtCore.QRect(500,5,71,21))

        font = QtGui.QFont(self.checkBox_3.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setObjectName("checkBox_3")

        self.checkBox_4 = QtGui.QCheckBox(self.frame)
        self.checkBox_4.setGeometry(QtCore.QRect(573,5,91,21))

        font = QtGui.QFont(self.checkBox_4.font())
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.checkBox_4.setFont(font)
        self.checkBox_4.setObjectName("checkBox_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        self.checkBox.setText(self.tr("Mat&ch case"))
        self.pushButton_3.setText(self.tr("Find &Previous"))
        self.lblFind.setText(self.tr("Find:"))
        self.checkBox_2.setText(self.tr("In &Source"))
        self.pushButton_2.setText(self.tr("Find &Next"))
        self.checkBox_3.setText(self.tr("In &Target"))
        self.checkBox_4.setText(self.tr("In &Comment"))
