# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Thu Feb  1 15:09:21 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,426,297).size()).expandedTo(tmsetting.minimumSizeHint()))

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

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,3,1,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.listView = QtGui.QListView(self.tab)
        self.listView.setObjectName("listView")
        self.gridlayout1.addWidget(self.listView,1,0,3,1)

        self.checkBox = QtGui.QCheckBox(self.tab)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout1.addWidget(self.checkBox,4,0,1,1)

        self.btnRemove = QtGui.QPushButton(self.tab)
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout1.addWidget(self.btnRemove,2,1,1,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)
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
        self.gridlayout.addWidget(self.tabOptions,0,0,1,2)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,1,0,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,1,1,1)

        self.retranslateUi(tmsetting)
        self.tabOptions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory Settings"))
        self.label_4.setText(self.tr("Locations:"))
        self.checkBox.setText(self.tr("Dive into Subfolders"))
        self.btnRemove.setText(self.tr("&Remove"))
        self.btnAdd.setText(self.tr("&Add"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&File"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), self.tr("&Database"))
        self.label_3.setText(self.tr("Maximum string length"))
        self.chkIgnorFuzzy.setText(self.tr(" Ignor fuzzy strings"))
        self.label.setText(self.tr("Similarity"))
        self.chkCaseSensitive.setText(self.tr("Case Sensitive"))
        self.label_2.setText(self.tr("Maximum candidates"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_4), self.tr("Options"))
        self.btnOk.setText(self.tr("&OK"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
