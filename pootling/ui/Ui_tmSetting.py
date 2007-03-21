# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Mar 21 10:51:24 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,484,404).size()).expandedTo(tmsetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(tmsetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.btnCancel = QtGui.QPushButton(tmsetting)
        self.btnCancel.setObjectName("btnCancel")
        self.gridlayout.addWidget(self.btnCancel,1,2,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,1,1,1)

        spacerItem = QtGui.QSpacerItem(251,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,0,1,1)

        self.tabOptions = QtGui.QTabWidget(tmsetting)
        self.tabOptions.setObjectName("tabOptions")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.chkGlossary = QtGui.QCheckBox(self.tab)
        self.chkGlossary.setObjectName("chkGlossary")
        self.gridlayout1.addWidget(self.chkGlossary,7,0,1,1)

        self.progressBar = QtGui.QProgressBar(self.tab)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout1.addWidget(self.progressBar,9,0,1,2)

        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.gridlayout1.addWidget(self.label_5,8,0,1,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setIconSize(QtCore.QSize(16,16))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)

        self.btnEnable = QtGui.QPushButton(self.tab)
        self.btnEnable.setIconSize(QtCore.QSize(16,16))
        self.btnEnable.setObjectName("btnEnable")
        self.gridlayout1.addWidget(self.btnEnable,4,1,1,1)

        self.listWidget = QtGui.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,5,1)

        self.btnRemoveAll = QtGui.QPushButton(self.tab)
        self.btnRemoveAll.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnRemoveAll.setIconSize(QtCore.QSize(16,16))
        self.btnRemoveAll.setObjectName("btnRemoveAll")
        self.gridlayout1.addWidget(self.btnRemoveAll,3,1,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.btnDisable = QtGui.QPushButton(self.tab)
        self.btnDisable.setIconSize(QtCore.QSize(16,16))
        self.btnDisable.setObjectName("btnDisable")
        self.gridlayout1.addWidget(self.btnDisable,5,1,1,1)

        self.btnRemove = QtGui.QPushButton(self.tab)
        self.btnRemove.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnRemove.setIconSize(QtCore.QSize(16,16))
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout1.addWidget(self.btnRemove,2,1,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,10,0,1,1)

        self.checkBox = QtGui.QCheckBox(self.tab)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout1.addWidget(self.checkBox,6,0,1,1)
        self.tabOptions.addTab(self.tab, "")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_4)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.groupBox = QtGui.QGroupBox(self.tab_4)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout3 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridlayout3.addWidget(self.label_3,2,0,1,1)

        self.spinMaxLen = QtGui.QSpinBox(self.groupBox)
        self.spinMaxLen.setMaximum(100)
        self.spinMaxLen.setMinimum(1)
        self.spinMaxLen.setProperty("value",QtCore.QVariant(70))
        self.spinMaxLen.setObjectName("spinMaxLen")
        self.gridlayout3.addWidget(self.spinMaxLen,2,1,1,1)

        self.spinSimilarity = QtGui.QSpinBox(self.groupBox)
        self.spinSimilarity.setMaximum(100)
        self.spinSimilarity.setMinimum(75)
        self.spinSimilarity.setSingleStep(1)
        self.spinSimilarity.setProperty("value",QtCore.QVariant(75))
        self.spinSimilarity.setObjectName("spinSimilarity")
        self.gridlayout3.addWidget(self.spinSimilarity,0,1,1,1)

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridlayout3.addWidget(self.label,0,0,1,1)

        self.spinMaxCandidate = QtGui.QSpinBox(self.groupBox)
        self.spinMaxCandidate.setMaximum(10)
        self.spinMaxCandidate.setMinimum(1)
        self.spinMaxCandidate.setProperty("value",QtCore.QVariant(10))
        self.spinMaxCandidate.setObjectName("spinMaxCandidate")
        self.gridlayout3.addWidget(self.spinMaxCandidate,1,1,1,1)

        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridlayout3.addWidget(self.label_2,1,0,1,1)
        self.gridlayout2.addWidget(self.groupBox,0,0,1,1)

        spacerItem2 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem2,1,0,1,1)
        self.tabOptions.addTab(self.tab_4, "")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,3)

        self.retranslateUi(tmsetting)
        self.tabOptions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)
        tmsetting.setTabOrder(self.tabOptions,self.listWidget)
        tmsetting.setTabOrder(self.listWidget,self.btnAdd)
        tmsetting.setTabOrder(self.btnAdd,self.btnRemove)
        tmsetting.setTabOrder(self.btnRemove,self.btnRemoveAll)
        tmsetting.setTabOrder(self.btnRemoveAll,self.btnEnable)
        tmsetting.setTabOrder(self.btnEnable,self.btnDisable)
        tmsetting.setTabOrder(self.btnDisable,self.checkBox)
        tmsetting.setTabOrder(self.checkBox,self.btnOk)
        tmsetting.setTabOrder(self.btnOk,self.btnCancel)
        tmsetting.setTabOrder(self.btnCancel,self.spinSimilarity)
        tmsetting.setTabOrder(self.spinSimilarity,self.spinMaxCandidate)
        tmsetting.setTabOrder(self.spinMaxCandidate,self.spinMaxLen)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory Settings"))
        self.btnCancel.setText(self.tr("&Cancel"))
        self.btnOk.setText(self.tr("&OK"))
        self.chkGlossary.setWhatsThis(self.tr("<h3>Glossary</h3> If this option is checked, then the selected path is a kind of glossary file(units as word), not normal file(units as strings). Check this can make translation memory run faster."))
        self.chkGlossary.setText(self.tr("Glossary"))
        self.label_5.setText(self.tr("Progress"))
        self.btnAdd.setToolTip(self.tr("Add TM"))
        self.btnAdd.setText(self.tr(" &Add"))
        self.btnEnable.setToolTip(self.tr("Enabel Translation Memory"))
        self.btnEnable.setText(self.tr(" &Enable"))
        self.listWidget.setToolTip(self.tr("Translation Memory(s)"))
        self.listWidget.setStatusTip(self.tr("List of Translation Memory Location(s)"))
        self.listWidget.setWhatsThis(self.tr("<h3>Translation Memory</h3> List of TMs. You can specify TMs which will be used and not used."))
        self.btnRemoveAll.setToolTip(self.tr("clear list"))
        self.btnRemoveAll.setText(self.tr(" Clea&r"))
        self.label_4.setText(self.tr("Locations:"))
        self.btnDisable.setToolTip(self.tr("Disable Translation Memory"))
        self.btnDisable.setText(self.tr("Di&sable"))
        self.btnRemove.setToolTip(self.tr("remove TM"))
        self.btnRemove.setText(self.tr(" De&lete"))
        self.checkBox.setWhatsThis(self.tr("<h3>Dive into subfolders</h3>If it is checked the process will include subfolders for translation memory scaning."))
        self.checkBox.setText(self.tr("Dive into Subfolders"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&File"))
        self.label_3.setText(self.tr("Maximum string length"))
        self.label.setText(self.tr("Similarity"))
        self.label_2.setText(self.tr("Maximum candidates"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_4), self.tr("O&ptions"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
