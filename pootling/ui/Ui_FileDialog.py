# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Feb 28 16:25:40 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,520,296).size()).expandedTo(Dialog.minimumSizeHint()))
        Dialog.setModal(False)

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.btnOK = QtGui.QPushButton(Dialog)
        self.btnOK.setObjectName("btnOK")
        self.gridlayout.addWidget(self.btnOK,2,3,1,1)

        spacerItem = QtGui.QSpacerItem(91,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,2,1,1,1)

        self.lineLocation = QtGui.QLineEdit(Dialog)
        self.lineLocation.setObjectName("lineLocation")
        self.gridlayout.addWidget(self.lineLocation,1,1,1,3)

        self.treeView = QtGui.QTreeView(Dialog)
        self.treeView.setObjectName("treeView")
        self.gridlayout.addWidget(self.treeView,0,1,1,3)

        self.btnAdd = QtGui.QPushButton(Dialog)
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout.addWidget(self.btnAdd,2,2,1,1)

        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,3,0,1,1)

        self.btnDesktop = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDesktop.sizePolicy().hasHeightForWidth())
        self.btnDesktop.setSizePolicy(sizePolicy)
        self.btnDesktop.setIcon(QtGui.QIcon("../images/desktop.png"))
        self.btnDesktop.setIconSize(QtCore.QSize(32,32))
        self.btnDesktop.setFlat(True)
        self.btnDesktop.setObjectName("btnDesktop")
        self.gridlayout1.addWidget(self.btnDesktop,1,0,1,1)

        self.btnHome = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnHome.sizePolicy().hasHeightForWidth())
        self.btnHome.setSizePolicy(sizePolicy)
        self.btnHome.setIcon(QtGui.QIcon("../images/folder_home.png"))
        self.btnHome.setIconSize(QtCore.QSize(32,32))
        self.btnHome.setFlat(True)
        self.btnHome.setObjectName("btnHome")
        self.gridlayout1.addWidget(self.btnHome,0,0,1,1)

        self.btnDoc = QtGui.QPushButton(self.frame)
        self.btnDoc.setIcon(QtGui.QIcon("../images/document.png"))
        self.btnDoc.setIconSize(QtCore.QSize(32,32))
        self.btnDoc.setAutoDefault(True)
        self.btnDoc.setFlat(True)
        self.btnDoc.setObjectName("btnDoc")
        self.gridlayout1.addWidget(self.btnDoc,2,0,1,1)
        self.gridlayout.addWidget(self.frame,0,0,2,1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.btnHome,self.btnDesktop)
        Dialog.setTabOrder(self.btnDesktop,self.treeView)
        Dialog.setTabOrder(self.treeView,self.lineLocation)
        Dialog.setTabOrder(self.lineLocation,self.btnAdd)
        Dialog.setTabOrder(self.btnAdd,self.btnOK)

    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Select a file or a location"))
        self.btnOK.setText(self.tr("&OK"))
        self.btnAdd.setText(self.tr("&Add"))
        self.btnDesktop.setToolTip(self.tr("go to Desktop folder"))
        self.btnDesktop.setText(self.tr(" &Desktop"))
        self.btnHome.setToolTip(self.tr("go to Home folder"))
        self.btnHome.setText(self.tr(" &Home"))
        self.btnDoc.setToolTip(self.tr("go to Document folder"))
        self.btnDoc.setText(self.tr(" Docu&ments"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
