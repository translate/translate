# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/k-da/Documents/poxole/trunk/pootling/ui/TableTM.ui'
#
# Created: Mon May 28 16:17:10 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,227,175).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(13),QtGui.QSizePolicy.Policy(13))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(100,50))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")

        self.tblTM = QtGui.QTableWidget(Form)
        self.tblTM.setDragEnabled(True)
        self.tblTM.setObjectName("tblTM")
        self.gridlayout.addWidget(self.tblTM,0,0,1,3)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,2,1,1)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.lblPath = QtGui.QLabel(Form)
        self.lblPath.setWindowModality(QtCore.Qt.NonModal)
        self.lblPath.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.lblPath.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblPath.setWordWrap(False)
        self.lblPath.setObjectName("lblPath")
        self.vboxlayout.addWidget(self.lblPath)

        self.lblTranslator = QtGui.QLabel(Form)
        self.lblTranslator.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblTranslator.setObjectName("lblTranslator")
        self.vboxlayout.addWidget(self.lblTranslator)

        self.lblDate = QtGui.QLabel(Form)
        self.lblDate.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblDate.setObjectName("lblDate")
        self.vboxlayout.addWidget(self.lblDate)
        self.gridlayout.addLayout(self.vboxlayout,1,1,1,1)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.vboxlayout1.addWidget(self.label)

        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.vboxlayout1.addWidget(self.label_3)

        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.vboxlayout1.addWidget(self.label_4)
        self.gridlayout.addLayout(self.vboxlayout1,1,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Lookup", None, QtGui.QApplication.UnicodeUTF8))
        self.tblTM.setWhatsThis(QtGui.QApplication.translate("Form", "<h3>Search Results</h3>This table shows the results of searching in translation memory. Similarity tells you about the seach score. 100% means the source is identical in TM. At the buttom is displayed the location, translator, and translated date of each candidate, row. This table is automatically hiden if the option \" Automatically lookup translation in TM\" under Settings/Preference/TM-Glossary is unchecked.", None, QtGui.QApplication.UnicodeUTF8))
        self.tblTM.setRowCount(0)
        self.tblTM.setColumnCount(2)
        self.tblTM.clear()
        self.tblTM.setColumnCount(2)
        self.tblTM.setRowCount(0)
        self.label.setText(QtGui.QApplication.translate("Form", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Found in:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Translator:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Date:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
