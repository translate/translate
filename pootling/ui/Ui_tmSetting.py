# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon May 21 16:56:01 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,468,366).size()).expandedTo(tmsetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(tmsetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.checkBox = QtGui.QCheckBox(tmsetting)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout.addWidget(self.checkBox,5,0,1,2)

        self.listWidget = QtGui.QListWidget(tmsetting)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout.addWidget(self.listWidget,1,0,4,2)

        spacerItem = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,4,2,1,1)

        self.btnRemoveAll = QtGui.QPushButton(tmsetting)
        self.btnRemoveAll.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnRemoveAll.setIconSize(QtCore.QSize(16,16))
        self.btnRemoveAll.setObjectName("btnRemoveAll")
        self.gridlayout.addWidget(self.btnRemoveAll,3,2,1,1)

        self.btnRemove = QtGui.QPushButton(tmsetting)
        self.btnRemove.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnRemove.setIconSize(QtCore.QSize(16,16))
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout.addWidget(self.btnRemove,2,2,1,1)

        self.btnAdd = QtGui.QPushButton(tmsetting)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setIconSize(QtCore.QSize(16,16))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout.addWidget(self.btnAdd,1,2,1,1)

        self.btnCancel = QtGui.QPushButton(tmsetting)
        self.btnCancel.setObjectName("btnCancel")
        self.gridlayout.addWidget(self.btnCancel,8,2,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,8,1,1,1)

        self.groupBox = QtGui.QGroupBox(tmsetting)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridlayout1.addWidget(self.label_3,2,0,1,1)

        self.spinMaxLen = QtGui.QSpinBox(self.groupBox)
        self.spinMaxLen.setMaximum(100)
        self.spinMaxLen.setMinimum(1)
        self.spinMaxLen.setProperty("value",QtCore.QVariant(70))
        self.spinMaxLen.setObjectName("spinMaxLen")
        self.gridlayout1.addWidget(self.spinMaxLen,2,1,1,1)

        self.spinSimilarity = QtGui.QSpinBox(self.groupBox)
        self.spinSimilarity.setMaximum(100)
        self.spinSimilarity.setMinimum(75)
        self.spinSimilarity.setSingleStep(1)
        self.spinSimilarity.setProperty("value",QtCore.QVariant(75))
        self.spinSimilarity.setObjectName("spinSimilarity")
        self.gridlayout1.addWidget(self.spinSimilarity,0,1,1,1)

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,0,0,1,1)

        self.spinMaxCandidate = QtGui.QSpinBox(self.groupBox)
        self.spinMaxCandidate.setMaximum(10)
        self.spinMaxCandidate.setMinimum(1)
        self.spinMaxCandidate.setProperty("value",QtCore.QVariant(10))
        self.spinMaxCandidate.setObjectName("spinMaxCandidate")
        self.gridlayout1.addWidget(self.spinMaxCandidate,1,1,1,1)

        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridlayout1.addWidget(self.label_2,1,0,1,1)
        self.gridlayout.addWidget(self.groupBox,6,0,1,3)

        self.label_4 = QtGui.QLabel(tmsetting)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4,0,0,1,2)

        self.progressBar = QtGui.QProgressBar(tmsetting)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout.addWidget(self.progressBar,8,0,1,1)

        self.label_6 = QtGui.QLabel(tmsetting)
        self.label_6.setObjectName("label_6")
        self.gridlayout.addWidget(self.label_6,7,0,1,3)

        self.retranslateUi(tmsetting)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)
        tmsetting.setTabOrder(self.listWidget,self.btnAdd)
        tmsetting.setTabOrder(self.btnAdd,self.btnRemove)
        tmsetting.setTabOrder(self.btnRemove,self.btnRemoveAll)
        tmsetting.setTabOrder(self.btnRemoveAll,self.checkBox)
        tmsetting.setTabOrder(self.checkBox,self.spinSimilarity)
        tmsetting.setTabOrder(self.spinSimilarity,self.spinMaxCandidate)
        tmsetting.setTabOrder(self.spinMaxCandidate,self.spinMaxLen)
        tmsetting.setTabOrder(self.spinMaxLen,self.btnOk)
        tmsetting.setTabOrder(self.btnOk,self.btnCancel)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory and glossary Settings"))
        self.checkBox.setWhatsThis(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:large; font-weight:600;\"><span style=\" font-size:large;\">Dive into subfolders</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Check this option, translation memory will include subfolders of the above path(s).</p></body></html>"))
        self.checkBox.setText(self.tr("Dive into Subfolders"))
        self.listWidget.setToolTip(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Path for translation memory</p></body></html>"))
        self.listWidget.setStatusTip(self.tr("List of Translation Memory Location(s)"))
        self.listWidget.setWhatsThis(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:large; font-weight:600;\">Path for translation memory</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:large; font-weight:600;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of path to scan for translation memory. Paths which are checked will be used.</p></body></html>"))
        self.btnRemoveAll.setToolTip(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">clear path(s)</p></body></html>"))
        self.btnRemoveAll.setText(self.tr(" Clea&r"))
        self.btnRemove.setToolTip(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">delete selected path(s)</p></body></html>"))
        self.btnRemove.setText(self.tr(" De&lete"))
        self.btnAdd.setToolTip(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add path for TM</p></body></html>"))
        self.btnAdd.setText(self.tr(" &Add"))
        self.btnCancel.setText(self.tr("&Cancel"))
        self.btnOk.setText(self.tr("&OK"))
        self.groupBox.setTitle(self.tr("Options"))
        self.label_3.setText(self.tr("Maximum string length"))
        self.spinMaxLen.setWhatsThis(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Maximum string length</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Maximum number of source string to search from.</p></body></html>"))
        self.spinSimilarity.setWhatsThis(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Minimum similarity</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Minimum similarity of source string to be include in translation memory.</p></body></html>"))
        self.label.setText(self.tr("Minimum similarity"))
        self.spinMaxCandidate.setWhatsThis(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Maximum search result</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Number of result that will be shown in the TM lookup view.</p></body></html>"))
        self.label_2.setText(self.tr("Maximum search result"))
        self.label_4.setText(self.tr("Locations:"))
        self.label_6.setText(self.tr("Progress"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
