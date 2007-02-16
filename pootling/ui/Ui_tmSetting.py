# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ks/programming/wordforge/trunk/pootling/ui/tmSetting.ui'
#
# Created: Fri Feb 16 10:37:11 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,484,404).size()).expandedTo(tmsetting.minimumSizeHint()))

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

        self.checkBox = QtGui.QCheckBox(self.tab)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout1.addWidget(self.checkBox,6,0,1,1)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,10,0,1,1)

        self.btnRemove = QtGui.QPushButton(self.tab)
        self.btnRemove.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnRemove.setIconSize(QtCore.QSize(16,16))
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout1.addWidget(self.btnRemove,2,1,1,1)

        self.btnDisable = QtGui.QPushButton(self.tab)
        self.btnDisable.setIconSize(QtCore.QSize(16,16))
        self.btnDisable.setObjectName("btnDisable")
        self.gridlayout1.addWidget(self.btnDisable,5,1,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.btnRemoveAll = QtGui.QPushButton(self.tab)
        self.btnRemoveAll.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnRemoveAll.setIconSize(QtCore.QSize(16,16))
        self.btnRemoveAll.setObjectName("btnRemoveAll")
        self.gridlayout1.addWidget(self.btnRemoveAll,3,1,1,1)

        self.listWidget = QtGui.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,5,1)

        self.btnEnable = QtGui.QPushButton(self.tab)
        self.btnEnable.setIconSize(QtCore.QSize(16,16))
        self.btnEnable.setObjectName("btnEnable")
        self.gridlayout1.addWidget(self.btnEnable,4,1,1,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setIconSize(QtCore.QSize(16,16))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)

        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.gridlayout1.addWidget(self.label_5,8,0,1,1)

        self.progressBar = QtGui.QProgressBar(self.tab)
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout1.addWidget(self.progressBar,9,0,1,2)

        self.chbrefreshAllTMs = QtGui.QCheckBox(self.tab)
        self.chbrefreshAllTMs.setObjectName("chbrefreshAllTMs")
        self.gridlayout1.addWidget(self.chbrefreshAllTMs,7,0,1,1)
        self.tabOptions.addTab(self.tab,"")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabOptions.addTab(self.tab_3,"")

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
        self.tabOptions.addTab(self.tab_4,"")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,3)

        spacerItem2 = QtGui.QSpacerItem(281,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,1,0,1,1)

        self.btnCancel = QtGui.QPushButton(tmsetting)
        self.btnCancel.setObjectName("btnCancel")
        self.gridlayout.addWidget(self.btnCancel,1,2,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,1,1,1)

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
        tmsetting.setTabOrder(self.btnOk,self.spinSimilarity)
        tmsetting.setTabOrder(self.spinSimilarity,self.chkCaseSensitive)
        tmsetting.setTabOrder(self.chkCaseSensitive,self.spinMaxLen)
        tmsetting.setTabOrder(self.spinMaxLen,self.spinMaxCandidate)
        tmsetting.setTabOrder(self.spinMaxCandidate,self.chkIgnorFuzzy)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(QtGui.QApplication.translate("tmsetting", "Translation Memory Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("tmsetting", "Dive into Subfolders", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setToolTip(QtGui.QApplication.translate("tmsetting", "remove TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("tmsetting", " De&lete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDisable.setToolTip(QtGui.QApplication.translate("tmsetting", "Disable Translation Memory", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDisable.setText(QtGui.QApplication.translate("tmsetting", "Di&sable", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("tmsetting", "Locations:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemoveAll.setToolTip(QtGui.QApplication.translate("tmsetting", "clear list", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemoveAll.setText(QtGui.QApplication.translate("tmsetting", " &Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEnable.setToolTip(QtGui.QApplication.translate("tmsetting", "Enabel Translation Memory", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEnable.setText(QtGui.QApplication.translate("tmsetting", " &Enable", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setToolTip(QtGui.QApplication.translate("tmsetting", "Add TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("tmsetting", " &Add", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("tmsetting", "Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.chbrefreshAllTMs.setText(QtGui.QApplication.translate("tmsetting", "refresh all TMs", None, QtGui.QApplication.UnicodeUTF8))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), QtGui.QApplication.translate("tmsetting", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), QtGui.QApplication.translate("tmsetting", "&Database", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("tmsetting", "Maximum string length", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIgnorFuzzy.setText(QtGui.QApplication.translate("tmsetting", " Ignor fuzzy strings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("tmsetting", "Similarity", None, QtGui.QApplication.UnicodeUTF8))
        self.chkCaseSensitive.setText(QtGui.QApplication.translate("tmsetting", "Case Sensitive", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("tmsetting", "Maximum candidates", None, QtGui.QApplication.UnicodeUTF8))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_4), QtGui.QApplication.translate("tmsetting", "O&ptions", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("tmsetting", "Ca&ncel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOk.setText(QtGui.QApplication.translate("tmsetting", "&OK", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
