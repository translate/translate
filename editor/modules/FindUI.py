# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Aug 23 11:37:43 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setEnabled(True)
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,800,35).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(800,35))
        Form.setMaximumSize(QtCore.QSize(16777215,30))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(0,0,800,35))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(800,35))
        self.frame.setMaximumSize(QtCore.QSize(16777215,30))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName("frame")

        self.lblFind = QtGui.QLabel(self.frame)
        self.lblFind.setGeometry(QtCore.QRect(1,5,35,22))
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))

        font = QtGui.QFont(self.lblFind.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.lblFind.setFont(font)
        self.lblFind.setObjectName("lblFind")

        self.pushButton_4 = QtGui.QPushButton(self.frame)
        self.pushButton_4.setGeometry(QtCore.QRect(775,5,21,22))

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

        self.lineEdit = QtGui.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(36,5,171,22))
        self.lineEdit.setObjectName("lineEdit")

        self.findNext = QtGui.QPushButton(self.frame)
        self.findNext.setEnabled(False)
        self.findNext.setGeometry(QtCore.QRect(212,5,84,22))

        font = QtGui.QFont(self.findNext.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.findNext.setFont(font)
        self.findNext.setIcon(QtGui.QIcon("./images/next.png"))
        self.findNext.setFlat(False)
        self.findNext.setObjectName("findNext")

        self.findPrevious = QtGui.QPushButton(self.frame)
        self.findPrevious.setEnabled(False)
        self.findPrevious.setGeometry(QtCore.QRect(298,5,112,22))

        font = QtGui.QFont(self.findPrevious.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.findPrevious.setFont(font)
        self.findPrevious.setIcon(QtGui.QIcon("./images/previous.png"))
        self.findPrevious.setFlat(False)
        self.findPrevious.setObjectName("findPrevious")

        self.matchcase = QtGui.QCheckBox(self.frame)
        self.matchcase.setGeometry(QtCore.QRect(682,5,91,22))

        font = QtGui.QFont(self.matchcase.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.matchcase.setFont(font)
        self.matchcase.setObjectName("matchcase")

        self.groupBox = QtGui.QGroupBox(self.frame)
        self.groupBox.setGeometry(QtCore.QRect(414,5,265,22))
        self.groupBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.groupBox.setObjectName("groupBox")

        self.intarget = QtGui.QCheckBox(self.groupBox)
        self.intarget.setGeometry(QtCore.QRect(86,2,78,17))

        font = QtGui.QFont(self.intarget.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.intarget.setFont(font)
        self.intarget.setObjectName("intarget")

        self.insource = QtGui.QCheckBox(self.groupBox)
        self.insource.setGeometry(QtCore.QRect(4,2,81,17))

        font = QtGui.QFont(self.insource.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.insource.setFont(font)
        self.insource.setCheckable(True)
        self.insource.setChecked(True)
        self.insource.setTristate(False)
        self.insource.setObjectName("insource")

        self.incomment = QtGui.QCheckBox(self.groupBox)
        self.incomment.setGeometry(QtCore.QRect(166,2,96,17))

        font = QtGui.QFont(self.incomment.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.incomment.setFont(font)
        self.incomment.setChecked(False)
        self.incomment.setObjectName("incomment")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        self.lblFind.setText(self.tr("Find:"))
        self.findNext.setText(self.tr("Find &Next"))
        self.findPrevious.setText(self.tr("Find &Previous"))
        self.matchcase.setText(self.tr("Mat&ch case"))
        self.intarget.setText(self.tr("In &Target"))
        self.insource.setText(self.tr("In &Source"))
        self.incomment.setText(self.tr("In &Comment"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
