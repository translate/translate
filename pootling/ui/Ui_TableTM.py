# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/k-da/Documents/poxole/trunk/pootling/ui/TableTM.ui'
#
# Created: Wed May  2 10:39:56 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,335,439).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(150,50))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")

        self.tblTM = QtGui.QTableWidget(Form)
        self.tblTM.setObjectName("tblTM")
        self.gridlayout.addWidget(self.tblTM,3,0,1,3)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,2,2,1)

        self.lblTranslator = QtGui.QLabel(Form)
        self.lblTranslator.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblTranslator.setObjectName("lblTranslator")
        self.gridlayout.addWidget(self.lblTranslator,1,1,1,1)

        self.lblDate = QtGui.QLabel(Form)
        self.lblDate.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblDate.setObjectName("lblDate")
        self.gridlayout.addWidget(self.lblDate,2,1,1,1)

        self.lblPath = QtGui.QLabel(Form)
        self.lblPath.setWindowModality(QtCore.Qt.NonModal)
        self.lblPath.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.lblPath.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblPath.setWordWrap(False)
        self.lblPath.setObjectName("lblPath")
        self.gridlayout.addWidget(self.lblPath,0,1,1,1)

        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,1,0,1,1)

        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4,2,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Lookup", None, QtGui.QApplication.UnicodeUTF8))
        self.tblTM.setRowCount(0)
        self.tblTM.setColumnCount(2)
        self.tblTM.clear()
        self.tblTM.setColumnCount(2)
        self.tblTM.setRowCount(0)
        self.label.setText(QtGui.QApplication.translate("Form", "Found in:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Translator:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Date:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
