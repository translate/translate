# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Jan 17 15:48:35 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,433,393).size()).expandedTo(Dialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

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

        self.frame = QtGui.QFrame(Dialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.btnBrowseFile = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowseFile.sizePolicy().hasHeightForWidth())
        self.btnBrowseFile.setSizePolicy(sizePolicy)
        self.btnBrowseFile.setObjectName("btnBrowseFile")
        self.gridlayout1.addWidget(self.btnBrowseFile,2,1,1,1)

        self.lineDatabase = QtGui.QLineEdit(self.frame)
        self.lineDatabase.setReadOnly(False)
        self.lineDatabase.setObjectName("lineDatabase")
        self.gridlayout1.addWidget(self.lineDatabase,5,0,1,1)

        self.groupBox = QtGui.QGroupBox(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.radio_folder_sub = QtGui.QRadioButton(self.groupBox)
        self.radio_folder_sub.setObjectName("radio_folder_sub")
        self.gridlayout2.addWidget(self.radio_folder_sub,0,2,1,1)

        self.radio_file = QtGui.QRadioButton(self.groupBox)
        self.radio_file.setChecked(True)
        self.radio_file.setObjectName("radio_file")
        self.gridlayout2.addWidget(self.radio_file,0,0,1,1)

        self.radio_folder = QtGui.QRadioButton(self.groupBox)
        self.radio_folder.setObjectName("radio_folder")
        self.gridlayout2.addWidget(self.radio_folder,0,1,1,1)
        self.gridlayout1.addWidget(self.groupBox,0,0,1,1)

        self.label = QtGui.QLabel(self.frame)

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
        self.gridlayout1.addWidget(self.label,1,0,1,1)

        self.chkrepeated = QtGui.QCheckBox(self.frame)
        self.chkrepeated.setObjectName("chkrepeated")
        self.gridlayout1.addWidget(self.chkrepeated,6,0,1,1)

        self.proBar = QtGui.QProgressBar(self.frame)
        self.proBar.setProperty("value",QtCore.QVariant(0))
        self.proBar.setOrientation(QtCore.Qt.Horizontal)
        self.proBar.setObjectName("proBar")
        self.gridlayout1.addWidget(self.proBar,8,0,1,1)

        self.btnBrowseDatabase = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowseDatabase.sizePolicy().hasHeightForWidth())
        self.btnBrowseDatabase.setSizePolicy(sizePolicy)
        self.btnBrowseDatabase.setObjectName("btnBrowseDatabase")
        self.gridlayout1.addWidget(self.btnBrowseDatabase,5,1,1,1)

        self.btnGenerate = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnGenerate.sizePolicy().hasHeightForWidth())
        self.btnGenerate.setSizePolicy(sizePolicy)
        self.btnGenerate.setObjectName("btnGenerate")
        self.gridlayout1.addWidget(self.btnGenerate,8,1,1,1)

        self.lineFile = QtGui.QLineEdit(self.frame)
        self.lineFile.setObjectName("lineFile")
        self.gridlayout1.addWidget(self.lineFile,2,0,1,1)

        self.label_3 = QtGui.QLabel(self.frame)

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
        self.gridlayout1.addWidget(self.label_3,7,0,1,1)

        self.label_2 = QtGui.QLabel(self.frame)

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
        self.gridlayout1.addWidget(self.label_2,4,0,1,1)

        spacerItem2 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem2,9,0,1,1)
        self.gridlayout.addWidget(self.frame,0,0,2,2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Dialog"))
        self.btnok.setText(self.tr("OK"))
        self.btncancel.setText(self.tr("Cancel"))
        self.btnBrowseFile.setText(self.tr("Browse..."))
        self.groupBox.setTitle(self.tr("scan"))
        self.radio_folder_sub.setText(self.tr("folder and sub"))
        self.radio_file.setText(self.tr("file"))
        self.radio_folder.setText(self.tr("folder"))
        self.label.setText(self.tr("Path to translated file"))
        self.chkrepeated.setText(self.tr("Repeat source string"))
        self.btnBrowseDatabase.setText(self.tr("Browse..."))
        self.btnGenerate.setText(self.tr("Generate"))
        self.label_3.setText(self.tr("Total progress:"))
        self.label_2.setText(self.tr("Output Folder"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
