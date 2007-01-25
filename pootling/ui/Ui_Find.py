# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Tue Jan 23 15:27:08 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmFind(object):
    def setupUi(self, frmFind):
        frmFind.setObjectName("frmFind")
        frmFind.setEnabled(True)
        frmFind.resize(QtCore.QSize(QtCore.QRect(0,0,703,64).size()).expandedTo(frmFind.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmFind.sizePolicy().hasHeightForWidth())
        frmFind.setSizePolicy(sizePolicy)
        frmFind.setAutoFillBackground(True)

        self.hboxlayout = QtGui.QHBoxLayout(frmFind)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.lineEdit_2 = QtGui.QLineEdit(frmFind)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(0,26))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridlayout.addWidget(self.lineEdit_2,1,1,1,1)

        self.lblReplace = QtGui.QLabel(frmFind)
        self.lblReplace.setSizeIncrement(QtCore.QSize(0,0))
        self.lblReplace.setObjectName("lblReplace")
        self.gridlayout.addWidget(self.lblReplace,1,0,1,1)

        self.findNext = QtGui.QPushButton(frmFind)
        self.findNext.setEnabled(False)
        self.findNext.setAutoDefault(True)
        self.findNext.setDefault(True)
        self.findNext.setFlat(False)
        self.findNext.setObjectName("findNext")
        self.gridlayout.addWidget(self.findNext,0,2,1,1)

        self.lblFind = QtGui.QLabel(frmFind)
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))
        self.lblFind.setObjectName("lblFind")
        self.gridlayout.addWidget(self.lblFind,0,0,1,1)

        self.lineEdit = QtGui.QLineEdit(frmFind)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setMinimumSize(QtCore.QSize(0,26))
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit,0,1,1,1)

        self.findPrevious = QtGui.QPushButton(frmFind)
        self.findPrevious.setEnabled(False)
        self.findPrevious.setAutoDefault(True)
        self.findPrevious.setDefault(True)
        self.findPrevious.setFlat(False)
        self.findPrevious.setObjectName("findPrevious")
        self.gridlayout.addWidget(self.findPrevious,0,3,1,1)

        self.replace = QtGui.QPushButton(frmFind)
        self.replace.setEnabled(False)
        self.replace.setAutoDefault(True)
        self.replace.setDefault(True)
        self.replace.setFlat(False)
        self.replace.setObjectName("replace")
        self.gridlayout.addWidget(self.replace,1,2,1,1)

        self.replaceAll = QtGui.QPushButton(frmFind)
        self.replaceAll.setEnabled(False)
        self.replaceAll.setAutoDefault(True)
        self.replaceAll.setDefault(True)
        self.replaceAll.setFlat(False)
        self.replaceAll.setObjectName("replaceAll")
        self.gridlayout.addWidget(self.replaceAll,1,3,1,1)
        self.hboxlayout.addLayout(self.gridlayout)

        self.groupBox = QtGui.QGroupBox(frmFind)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(11)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.insource = QtGui.QCheckBox(self.groupBox)
        self.insource.setCheckable(True)
        self.insource.setTristate(False)
        self.insource.setObjectName("insource")
        self.hboxlayout1.addWidget(self.insource)

        self.intarget = QtGui.QCheckBox(self.groupBox)
        self.intarget.setObjectName("intarget")
        self.hboxlayout1.addWidget(self.intarget)

        self.incomment = QtGui.QCheckBox(self.groupBox)
        self.incomment.setChecked(False)
        self.incomment.setObjectName("incomment")
        self.hboxlayout1.addWidget(self.incomment)
        self.hboxlayout.addWidget(self.groupBox)

        self.matchcase = QtGui.QCheckBox(frmFind)
        self.matchcase.setObjectName("matchcase")
        self.hboxlayout.addWidget(self.matchcase)

        self.retranslateUi(frmFind)
        QtCore.QMetaObject.connectSlotsByName(frmFind)
        frmFind.setTabOrder(self.lineEdit,self.findNext)
        frmFind.setTabOrder(self.findNext,self.findPrevious)
        frmFind.setTabOrder(self.findPrevious,self.lineEdit_2)
        frmFind.setTabOrder(self.lineEdit_2,self.replace)
        frmFind.setTabOrder(self.replace,self.replaceAll)

    def tr(self, string):
        return QtGui.QApplication.translate("frmFind", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmFind):
        frmFind.setWindowTitle(self.tr("Find & Replace"))
        self.lblReplace.setText(self.tr("Replace"))
        self.findNext.setText(self.tr("&Next"))
        self.lblFind.setText(self.tr("Search"))
        self.findPrevious.setText(self.tr("  &Previous  "))
        self.replace.setText(self.tr("&Replace"))
        self.replaceAll.setText(self.tr("Replace &All"))
        self.insource.setText(self.tr("S&ource"))
        self.intarget.setText(self.tr("&Target"))
        self.incomment.setText(self.tr("&Comment"))
        self.matchcase.setText(self.tr("&Match case"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    frmFind = QtGui.QWidget()
    ui = Ui_frmFind()
    ui.setupUi(frmFind)
    frmFind.show()
    sys.exit(app.exec_())
