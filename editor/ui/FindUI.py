# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Sep 29 17:27:05 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setEnabled(True)
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,800,70).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(800,70))
        Form.setMaximumSize(QtCore.QSize(16777215,0))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(95,10,251,24))
        self.lineEdit.setObjectName("lineEdit")

        self.findNext = QtGui.QPushButton(Form)
        self.findNext.setEnabled(False)
        self.findNext.setGeometry(QtCore.QRect(353,11,61,22))

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

        self.findPrevious = QtGui.QPushButton(Form)
        self.findPrevious.setEnabled(False)
        self.findPrevious.setGeometry(QtCore.QRect(421,11,81,22))

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

        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(95,40,251,24))
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.replace = QtGui.QPushButton(Form)
        self.replace.setEnabled(False)
        self.replace.setGeometry(QtCore.QRect(353,40,61,22))

        font = QtGui.QFont(self.replace.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.replace.setFont(font)
        self.replace.setFlat(False)
        self.replace.setObjectName("replace")

        self.replaceAll = QtGui.QPushButton(Form)
        self.replaceAll.setEnabled(False)
        self.replaceAll.setGeometry(QtCore.QRect(421,40,81,22))

        font = QtGui.QFont(self.replaceAll.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.replaceAll.setFont(font)
        self.replaceAll.setFlat(False)
        self.replaceAll.setObjectName("replaceAll")

        self.lblReplace = QtGui.QLabel(Form)
        self.lblReplace.setGeometry(QtCore.QRect(3,42,95,22))
        self.lblReplace.setSizeIncrement(QtCore.QSize(0,0))

        font = QtGui.QFont(self.lblReplace.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(True)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblReplace.setFont(font)
        self.lblReplace.setObjectName("lblReplace")

        self.lblFind = QtGui.QLabel(Form)
        self.lblFind.setGeometry(QtCore.QRect(16,14,79,22))
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))

        font = QtGui.QFont(self.lblFind.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(True)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblFind.setFont(font)
        self.lblFind.setObjectName("lblFind")

        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(507,9,291,55))

        font = QtGui.QFont(self.groupBox.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")

        self.line = QtGui.QFrame(self.groupBox)
        self.line.setGeometry(QtCore.QRect(3,26,284,5))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.matchcase = QtGui.QCheckBox(self.groupBox)
        self.matchcase.setGeometry(QtCore.QRect(11,33,91,17))

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

        self.insource = QtGui.QCheckBox(self.groupBox)
        self.insource.setGeometry(QtCore.QRect(10,4,81,17))

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
        self.incomment.setGeometry(QtCore.QRect(98,4,101,17))

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

        self.intarget = QtGui.QCheckBox(self.groupBox)
        self.intarget.setGeometry(QtCore.QRect(203,4,81,17))

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

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        self.findNext.setText(self.tr("&Next"))
        self.findPrevious.setText(self.tr("&Previous"))
        self.replace.setText(self.tr("&Replace"))
        self.replaceAll.setText(self.tr("Replace &All"))
        self.lblReplace.setText(self.tr("Replace With:"))
        self.lblFind.setText(self.tr("Search For:"))
        self.matchcase.setText(self.tr("Mat&ch case"))
        self.insource.setText(self.tr("In &Source"))
        self.incomment.setText(self.tr("In &Comment"))
        self.intarget.setText(self.tr("In &Target"))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
