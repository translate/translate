# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Feb  9 16:12:47 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,566,404).size()).expandedTo(tmsetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(tmsetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tabOptions = QtGui.QTabWidget(tmsetting)
        self.tabOptions.setObjectName("tabOptions")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.progressBar = QtGui.QProgressBar(self.tab)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout1.addWidget(self.progressBar,8,0,1,2)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,9,0,1,1)

        self.checkBox = QtGui.QCheckBox(self.tab)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout1.addWidget(self.checkBox,6,0,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.gridlayout1.addWidget(self.label_5,7,0,1,1)

        self.listWidget = QtGui.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,5,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setIconSize(QtCore.QSize(16,16))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)

        self.btnRemove = QtGui.QPushButton(self.tab)
        self.btnRemove.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnRemove.setIconSize(QtCore.QSize(16,16))
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout1.addWidget(self.btnRemove,2,1,1,1)

        self.btnRemoveAll = QtGui.QPushButton(self.tab)
        self.btnRemoveAll.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnRemoveAll.setIconSize(QtCore.QSize(16,16))
        self.btnRemoveAll.setObjectName("btnRemoveAll")
        self.gridlayout1.addWidget(self.btnRemoveAll,3,1,1,1)

        self.btnMoveUp = QtGui.QPushButton(self.tab)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setIconSize(QtCore.QSize(16,16))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout1.addWidget(self.btnMoveUp,4,1,1,1)

        self.btnMoveDown = QtGui.QPushButton(self.tab)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setIconSize(QtCore.QSize(16,16))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout1.addWidget(self.btnMoveDown,5,1,1,1)
        self.tabOptions.addTab(self.tab, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabOptions.addTab(self.tab_3, "")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_4)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.label_3 = QtGui.QLabel(self.tab_4)
        self.label_3.setObjectName("label_3")
        self.gridlayout2.addWidget(self.label_3,2,0,1,1)

        self.spinMaxLen = QtGui.QSpinBox(self.tab_4)
        self.spinMaxLen.setMaximum(100)
        self.spinMaxLen.setMinimum(1)
        self.spinMaxLen.setProperty("value",QtCore.QVariant(70))
        self.spinMaxLen.setObjectName("spinMaxLen")
        self.gridlayout2.addWidget(self.spinMaxLen,2,1,1,1)

        self.chkIgnorFuzzy = QtGui.QCheckBox(self.tab_4)
        self.chkIgnorFuzzy.setObjectName("chkIgnorFuzzy")
        self.gridlayout2.addWidget(self.chkIgnorFuzzy,4,0,1,1)

        self.spinSimilarity = QtGui.QSpinBox(self.tab_4)
        self.spinSimilarity.setMaximum(100)
        self.spinSimilarity.setMinimum(1)
        self.spinSimilarity.setSingleStep(1)
        self.spinSimilarity.setProperty("value",QtCore.QVariant(75))
        self.spinSimilarity.setObjectName("spinSimilarity")
        self.gridlayout2.addWidget(self.spinSimilarity,0,1,1,1)

        self.label = QtGui.QLabel(self.tab_4)
        self.label.setObjectName("label")
        self.gridlayout2.addWidget(self.label,0,0,1,1)

        self.chkCaseSensitive = QtGui.QCheckBox(self.tab_4)
        self.chkCaseSensitive.setObjectName("chkCaseSensitive")
        self.gridlayout2.addWidget(self.chkCaseSensitive,3,0,1,1)

        self.spinMaxCandidate = QtGui.QSpinBox(self.tab_4)
        self.spinMaxCandidate.setMaximum(100)
        self.spinMaxCandidate.setMinimum(1)
        self.spinMaxCandidate.setProperty("value",QtCore.QVariant(10))
        self.spinMaxCandidate.setObjectName("spinMaxCandidate")
        self.gridlayout2.addWidget(self.spinMaxCandidate,1,1,1,1)

        self.label_2 = QtGui.QLabel(self.tab_4)
        self.label_2.setObjectName("label_2")
        self.gridlayout2.addWidget(self.label_2,1,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,5,0,1,1)
        self.tabOptions.addTab(self.tab_4, "")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,4)

        spacerItem2 = QtGui.QSpacerItem(281,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,1,0,1,1)

        self.btnCancel = QtGui.QPushButton(tmsetting)
        self.btnCancel.setObjectName("btnCancel")
        self.gridlayout.addWidget(self.btnCancel,1,3,1,1)

        self.btnCreateTM = QtGui.QPushButton(tmsetting)
        self.btnCreateTM.setObjectName("btnCreateTM")
        self.gridlayout.addWidget(self.btnCreateTM,1,1,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,2,1,1)

        self.retranslateUi(tmsetting)
        self.tabOptions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)
        tmsetting.setTabOrder(self.tabOptions,self.listWidget)
        tmsetting.setTabOrder(self.listWidget,self.btnAdd)
        tmsetting.setTabOrder(self.btnAdd,self.btnRemove)
        tmsetting.setTabOrder(self.btnRemove,self.btnRemoveAll)
        tmsetting.setTabOrder(self.btnRemoveAll,self.btnMoveUp)
        tmsetting.setTabOrder(self.btnMoveUp,self.btnMoveDown)
        tmsetting.setTabOrder(self.btnMoveDown,self.checkBox)
        tmsetting.setTabOrder(self.checkBox,self.btnOk)
        tmsetting.setTabOrder(self.btnOk,self.spinSimilarity)
        tmsetting.setTabOrder(self.spinSimilarity,self.chkCaseSensitive)
        tmsetting.setTabOrder(self.chkCaseSensitive,self.spinMaxLen)
        tmsetting.setTabOrder(self.spinMaxLen,self.spinMaxCandidate)
        tmsetting.setTabOrder(self.spinMaxCandidate,self.chkIgnorFuzzy)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory Settings"))
        self.checkBox.setText(self.tr("Dive into Subfolders"))
        self.label_4.setText(self.tr("Locations:"))
        self.label_5.setText(self.tr("Progress"))
        self.btnAdd.setToolTip(self.tr("Add TM"))
        self.btnAdd.setText(self.tr(" &Add"))
        self.btnRemove.setToolTip(self.tr("remove TM"))
        self.btnRemove.setText(self.tr(" De&lete"))
        self.btnRemoveAll.setToolTip(self.tr("clear list"))
        self.btnRemoveAll.setText(self.tr(" &Clear"))
        self.btnMoveUp.setToolTip(self.tr("move up"))
        self.btnMoveUp.setText(self.tr(" &Up"))
        self.btnMoveDown.setToolTip(self.tr("move down"))
        self.btnMoveDown.setText(self.tr(" Do&wn"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&File"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), self.tr("&Database"))
        self.label_3.setText(self.tr("Maximum string length"))
        self.chkIgnorFuzzy.setText(self.tr(" Ignor fuzzy strings"))
        self.label.setText(self.tr("Similarity"))
        self.chkCaseSensitive.setText(self.tr("Case Sensitive"))
        self.label_2.setText(self.tr("Maximum candidates"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_4), self.tr("O&ptions"))
        self.btnCancel.setText(self.tr("Ca&ncel"))
        self.btnCreateTM.setText(self.tr("Create &TM"))
        self.btnOk.setText(self.tr("&OK"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
