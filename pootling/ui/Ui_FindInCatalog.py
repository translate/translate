# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/FindInCatalog.ui'
#
# Created: Tue Mar  6 09:00:56 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_frmFind(object):
    def setupUi(self, frmFind):
        frmFind.setObjectName("frmFind")
        frmFind.setEnabled(True)
        frmFind.resize(QtCore.QSize(QtCore.QRect(0,0,695,44).size()).expandedTo(frmFind.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmFind.sizePolicy().hasHeightForWidth())
        frmFind.setSizePolicy(sizePolicy)
        frmFind.setAutoFillBackground(True)

        self.gridlayout = QtGui.QGridLayout(frmFind)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.lineEdit = QtGui.QLineEdit(frmFind)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setMinimumSize(QtCore.QSize(0,26))
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit,0,1,1,1)

        self.find = QtGui.QPushButton(frmFind)
        self.find.setEnabled(True)
        self.find.setIcon(QtGui.QIcon("../images/find.png"))
        self.find.setAutoDefault(True)
        self.find.setDefault(True)
        self.find.setFlat(False)
        self.find.setObjectName("find")
        self.gridlayout.addWidget(self.find,0,2,1,1)

        self.lblFind = QtGui.QLabel(frmFind)
        self.lblFind.setSizeIncrement(QtCore.QSize(0,0))
        self.lblFind.setObjectName("lblFind")
        self.gridlayout.addWidget(self.lblFind,0,0,1,1)

        self.groupBox = QtGui.QGroupBox(frmFind)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")

        self.hboxlayout = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(11)
        self.hboxlayout.setObjectName("hboxlayout")

        self.chbsource = QtGui.QCheckBox(self.groupBox)
        self.chbsource.setChecked(True)
        self.chbsource.setObjectName("chbsource")
        self.hboxlayout.addWidget(self.chbsource)

        self.chbtarget = QtGui.QCheckBox(self.groupBox)
        self.chbtarget.setChecked(True)
        self.chbtarget.setObjectName("chbtarget")
        self.hboxlayout.addWidget(self.chbtarget)
        self.gridlayout.addWidget(self.groupBox,0,4,1,1)

        self.retranslateUi(frmFind)
        QtCore.QMetaObject.connectSlotsByName(frmFind)
        frmFind.setTabOrder(self.lineEdit,self.find)

    def retranslateUi(self, frmFind):
        frmFind.setWindowTitle(QtGui.QApplication.translate("frmFind", "Find", None, QtGui.QApplication.UnicodeUTF8))
        self.find.setText(QtGui.QApplication.translate("frmFind", " &Find", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFind.setText(QtGui.QApplication.translate("frmFind", "Find String in Files:", None, QtGui.QApplication.UnicodeUTF8))
        self.chbsource.setText(QtGui.QApplication.translate("frmFind", "S&ource", None, QtGui.QApplication.UnicodeUTF8))
        self.chbtarget.setText(QtGui.QApplication.translate("frmFind", "T&arget", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    frmFind = QtGui.QWidget()
    ui = Ui_frmFind()
    ui.setupUi(frmFind)
    frmFind.show()
    sys.exit(app.exec_())
