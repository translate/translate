# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Nov  3 17:14:51 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setEnabled(True)
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,600,70).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(600,70))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(2)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(0,26))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridlayout.addWidget(self.lineEdit_2,1,1,1,1)

        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setMinimumSize(QtCore.QSize(0,26))
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit,0,1,1,1)

        self.lblReplace = QtGui.QLabel(Form)
        self.lblReplace.setSizeIncrement(QtCore.QSize(0,0))
        self.lblReplace.setObjectName("lblReplace")
        self.gridlayout.addWidget(self.lblReplace,1,0,1,1)

        self.lblFind = QtGui.QLabel(Form)
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))
        self.lblFind.setObjectName("lblFind")
        self.gridlayout.addWidget(self.lblFind,0,0,1,1)

        self.findNext = QtGui.QPushButton(Form)
        self.findNext.setEnabled(False)

        font = QtGui.QFont(self.findNext.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.findNext.setFont(font)
        self.findNext.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.findNext.setAutoDefault(True)
        self.findNext.setDefault(True)
        self.findNext.setFlat(False)
        self.findNext.setObjectName("findNext")
        self.gridlayout.addWidget(self.findNext,0,2,1,1)

        self.replace = QtGui.QPushButton(Form)
        self.replace.setEnabled(False)

        font = QtGui.QFont(self.replace.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.replace.setFont(font)
        self.replace.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.replace.setFlat(False)
        self.replace.setObjectName("replace")
        self.gridlayout.addWidget(self.replace,1,2,1,1)

        self.replaceAll = QtGui.QPushButton(Form)
        self.replaceAll.setEnabled(False)

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
        self.gridlayout.addWidget(self.replaceAll,1,3,1,1)

        self.findPrevious = QtGui.QPushButton(Form)
        self.findPrevious.setEnabled(False)

        font = QtGui.QFont(self.findPrevious.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.findPrevious.setFont(font)
        self.findPrevious.setFlat(False)
        self.findPrevious.setObjectName("findPrevious")
        self.gridlayout.addWidget(self.findPrevious,0,3,1,1)

        self.groupBox = QtGui.QGroupBox(Form)

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

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout1.setMargin(2)
        self.gridlayout1.setSpacing(2)
        self.gridlayout1.setObjectName("gridlayout1")

        self.intarget = QtGui.QCheckBox(self.groupBox)
        self.intarget.setMinimumSize(QtCore.QSize(85,0))

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
        self.gridlayout1.addWidget(self.intarget,0,1,1,1)

        self.insource = QtGui.QCheckBox(self.groupBox)
        self.insource.setMinimumSize(QtCore.QSize(85,0))

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
        self.gridlayout1.addWidget(self.insource,0,0,1,1)

        self.incomment = QtGui.QCheckBox(self.groupBox)
        self.incomment.setMinimumSize(QtCore.QSize(85,0))

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
        self.gridlayout1.addWidget(self.incomment,0,2,1,1)

        self.matchcase = QtGui.QCheckBox(self.groupBox)
        self.matchcase.setMinimumSize(QtCore.QSize(85,0))

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
        self.gridlayout1.addWidget(self.matchcase,2,0,1,1)
        self.gridlayout.addWidget(self.groupBox,0,4,2,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.findNext,self.findPrevious)
        Form.setTabOrder(self.findPrevious,self.replace)
        Form.setTabOrder(self.replace,self.replaceAll)

    def tr(self, string):
        return QtGui.QApplication.translate("Form", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Form):
        self.lblReplace.setText(self.tr("Replace with:"))
        self.lblFind.setText(self.tr("Search for:"))
        self.findNext.setText(self.tr("&Next"))
        self.replace.setText(self.tr("&Replace"))
        self.replaceAll.setText(self.tr("Replace &All"))
        self.findPrevious.setText(self.tr("&Previous"))
        self.intarget.setText(self.tr("&Target"))
        self.insource.setText(self.tr("&Source"))
        self.incomment.setText(self.tr("&Comment"))
        self.matchcase.setText(self.tr("Matc&h case"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
