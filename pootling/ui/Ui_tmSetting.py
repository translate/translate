# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Jan 31 16:28:29 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,350,350).size()).expandedTo(tmsetting.minimumSizeHint()))

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

        self.groupBox_3 = QtGui.QGroupBox(self.tab)
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox_3)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.radPOFolder_sub = QtGui.QRadioButton(self.groupBox_3)
        self.radPOFolder_sub.setObjectName("radPOFolder_sub")
        self.gridlayout2.addWidget(self.radPOFolder_sub,2,0,1,1)

        self.radPOFolder = QtGui.QRadioButton(self.groupBox_3)
        self.radPOFolder.setObjectName("radPOFolder")
        self.gridlayout2.addWidget(self.radPOFolder,1,0,1,1)

        self.radPOFile = QtGui.QRadioButton(self.groupBox_3)
        self.radPOFile.setChecked(True)
        self.radPOFile.setObjectName("radPOFile")
        self.gridlayout2.addWidget(self.radPOFile,0,0,1,1)
        self.gridlayout1.addWidget(self.groupBox_3,0,0,1,1)

        self.poLookup = QtGui.QCheckBox(self.tab)
        self.poLookup.setAutoFillBackground(False)
        self.poLookup.setChecked(False)
        self.poLookup.setObjectName("poLookup")
        self.gridlayout1.addWidget(self.poLookup,3,0,1,1)

        self.btnPOFile = QtGui.QPushButton(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPOFile.sizePolicy().hasHeightForWidth())
        self.btnPOFile.setSizePolicy(sizePolicy)
        self.btnPOFile.setObjectName("btnPOFile")
        self.gridlayout1.addWidget(self.btnPOFile,2,1,1,1)

        self.label_11 = QtGui.QLabel(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_11.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridlayout1.addWidget(self.label_11,1,0,1,1)

        self.linePOFile = QtGui.QLineEdit(self.tab)
        self.linePOFile.setReadOnly(False)
        self.linePOFile.setObjectName("linePOFile")
        self.gridlayout1.addWidget(self.linePOFile,2,0,1,1)
        self.tabOptions.addTab(self.tab, "")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.gridlayout3 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.groupBox = QtGui.QGroupBox(self.tab_2)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout4 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout4.setMargin(9)
        self.gridlayout4.setSpacing(6)
        self.gridlayout4.setObjectName("gridlayout4")

        self.radTMXFile = QtGui.QRadioButton(self.groupBox)
        self.radTMXFile.setChecked(True)
        self.radTMXFile.setObjectName("radTMXFile")
        self.gridlayout4.addWidget(self.radTMXFile,0,0,1,1)

        self.radTMXFolder = QtGui.QRadioButton(self.groupBox)
        self.radTMXFolder.setObjectName("radTMXFolder")
        self.gridlayout4.addWidget(self.radTMXFolder,1,0,1,1)

        self.radTMXFolder_sub = QtGui.QRadioButton(self.groupBox)
        self.radTMXFolder_sub.setObjectName("radTMXFolder_sub")
        self.gridlayout4.addWidget(self.radTMXFolder_sub,2,0,1,1)
        self.gridlayout3.addWidget(self.groupBox,0,0,1,1)

        self.label_9 = QtGui.QLabel(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_9.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridlayout3.addWidget(self.label_9,1,0,1,1)

        self.tmxLookup = QtGui.QCheckBox(self.tab_2)
        self.tmxLookup.setAutoFillBackground(False)
        self.tmxLookup.setChecked(False)
        self.tmxLookup.setObjectName("tmxLookup")
        self.gridlayout3.addWidget(self.tmxLookup,3,0,1,1)

        self.lineTMXFile = QtGui.QLineEdit(self.tab_2)
        self.lineTMXFile.setReadOnly(False)
        self.lineTMXFile.setObjectName("lineTMXFile")
        self.gridlayout3.addWidget(self.lineTMXFile,2,0,1,1)

        self.btnTMXFile = QtGui.QPushButton(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnTMXFile.sizePolicy().hasHeightForWidth())
        self.btnTMXFile.setSizePolicy(sizePolicy)
        self.btnTMXFile.setObjectName("btnTMXFile")
        self.gridlayout3.addWidget(self.btnTMXFile,2,1,1,1)
        self.tabOptions.addTab(self.tab_2, "")

        self.tabXliff = QtGui.QWidget()
        self.tabXliff.setObjectName("tabXliff")

        self.gridlayout5 = QtGui.QGridLayout(self.tabXliff)
        self.gridlayout5.setMargin(9)
        self.gridlayout5.setSpacing(6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.groupBox_2 = QtGui.QGroupBox(self.tabXliff)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridlayout6 = QtGui.QGridLayout(self.groupBox_2)
        self.gridlayout6.setMargin(9)
        self.gridlayout6.setSpacing(6)
        self.gridlayout6.setObjectName("gridlayout6")

        self.radXLiffFolder_sub = QtGui.QRadioButton(self.groupBox_2)
        self.radXLiffFolder_sub.setObjectName("radXLiffFolder_sub")
        self.gridlayout6.addWidget(self.radXLiffFolder_sub,2,0,1,1)

        self.radXLiffFolder = QtGui.QRadioButton(self.groupBox_2)
        self.radXLiffFolder.setObjectName("radXLiffFolder")
        self.gridlayout6.addWidget(self.radXLiffFolder,1,0,1,1)

        self.radXLiffFile = QtGui.QRadioButton(self.groupBox_2)
        self.radXLiffFile.setChecked(True)
        self.radXLiffFile.setObjectName("radXLiffFile")
        self.gridlayout6.addWidget(self.radXLiffFile,0,0,1,1)
        self.gridlayout5.addWidget(self.groupBox_2,0,0,1,1)

        self.lineXliffFile = QtGui.QLineEdit(self.tabXliff)
        self.lineXliffFile.setReadOnly(False)
        self.lineXliffFile.setObjectName("lineXliffFile")
        self.gridlayout5.addWidget(self.lineXliffFile,2,0,1,1)

        self.btnXLiffFile = QtGui.QPushButton(self.tabXliff)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnXLiffFile.sizePolicy().hasHeightForWidth())
        self.btnXLiffFile.setSizePolicy(sizePolicy)
        self.btnXLiffFile.setObjectName("btnXLiffFile")
        self.gridlayout5.addWidget(self.btnXLiffFile,2,1,1,1)

        self.label_6 = QtGui.QLabel(self.tabXliff)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_6.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridlayout5.addWidget(self.label_6,1,0,1,1)

        self.xliffLookup = QtGui.QCheckBox(self.tabXliff)
        self.xliffLookup.setAutoFillBackground(False)
        self.xliffLookup.setChecked(False)
        self.xliffLookup.setObjectName("xliffLookup")
        self.gridlayout5.addWidget(self.xliffLookup,3,0,1,1)
        self.tabOptions.addTab(self.tabXliff, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabOptions.addTab(self.tab_3, "")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.gridlayout7 = QtGui.QGridLayout(self.tab_4)
        self.gridlayout7.setMargin(9)
        self.gridlayout7.setSpacing(6)
        self.gridlayout7.setObjectName("gridlayout7")

        self.chkCaseSensitive = QtGui.QCheckBox(self.tab_4)
        self.chkCaseSensitive.setObjectName("chkCaseSensitive")
        self.gridlayout7.addWidget(self.chkCaseSensitive,3,0,1,1)

        self.chkIgnorFuzzy = QtGui.QCheckBox(self.tab_4)
        self.chkIgnorFuzzy.setObjectName("chkIgnorFuzzy")
        self.gridlayout7.addWidget(self.chkIgnorFuzzy,4,0,1,1)

        self.label_3 = QtGui.QLabel(self.tab_4)
        self.label_3.setObjectName("label_3")
        self.gridlayout7.addWidget(self.label_3,2,0,1,1)

        self.spinMaxLen = QtGui.QSpinBox(self.tab_4)
        self.spinMaxLen.setObjectName("spinMaxLen")
        self.gridlayout7.addWidget(self.spinMaxLen,2,1,1,1)

        self.label_2 = QtGui.QLabel(self.tab_4)
        self.label_2.setObjectName("label_2")
        self.gridlayout7.addWidget(self.label_2,1,0,1,1)

        self.spinMaxCandidate = QtGui.QSpinBox(self.tab_4)
        self.spinMaxCandidate.setObjectName("spinMaxCandidate")
        self.gridlayout7.addWidget(self.spinMaxCandidate,1,1,1,1)

        self.spinSimilarity = QtGui.QSpinBox(self.tab_4)
        self.spinSimilarity.setObjectName("spinSimilarity")
        self.gridlayout7.addWidget(self.spinSimilarity,0,1,1,1)

        self.label = QtGui.QLabel(self.tab_4)
        self.label.setObjectName("label")
        self.gridlayout7.addWidget(self.label,0,0,1,1)
        self.tabOptions.addTab(self.tab_4, "")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,3)

        spacerItem = QtGui.QSpacerItem(332,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,1,0,1,3)

        spacerItem1 = QtGui.QSpacerItem(141,46,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1,2,0,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,2,1,1,1)

        self.btnClose = QtGui.QPushButton(tmsetting)
        self.btnClose.setObjectName("btnClose")
        self.gridlayout.addWidget(self.btnClose,2,2,1,1)

        self.retranslateUi(tmsetting)
        self.tabOptions.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory Settings"))
        self.groupBox_3.setTitle(self.tr("Scan"))
        self.radPOFolder_sub.setText(self.tr("Folders and subfolders"))
        self.radPOFolder.setText(self.tr("Folders"))
        self.radPOFile.setText(self.tr("Files"))
        self.poLookup.setText(self.tr("LookUp"))
        self.btnPOFile.setText(self.tr("&Browse..."))
        self.label_11.setText(self.tr("Path to XLiff translated file"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&PO"))
        self.groupBox.setTitle(self.tr("Scan"))
        self.radTMXFile.setText(self.tr("Files"))
        self.radTMXFolder.setText(self.tr("Folders"))
        self.radTMXFolder_sub.setText(self.tr("Folders and subfolders"))
        self.label_9.setText(self.tr("Path to XLiff translated file"))
        self.tmxLookup.setText(self.tr("LookUp"))
        self.btnTMXFile.setText(self.tr("&Browse..."))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_2), self.tr("&TMX"))
        self.groupBox_2.setTitle(self.tr("Scan"))
        self.radXLiffFolder_sub.setText(self.tr("Folders and subfolders"))
        self.radXLiffFolder.setText(self.tr("Folders"))
        self.radXLiffFile.setText(self.tr("Files"))
        self.btnXLiffFile.setText(self.tr("&Browse..."))
        self.label_6.setText(self.tr("Path to XLiff translated file"))
        self.xliffLookup.setText(self.tr("LookUp"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tabXliff), self.tr("&Xliff"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), self.tr("&Database"))
        self.chkCaseSensitive.setText(self.tr("Case Sensitive"))
        self.chkIgnorFuzzy.setText(self.tr(" Ignor fuzzy strings"))
        self.label_3.setText(self.tr("Maximum string length"))
        self.label_2.setText(self.tr("Maximum candidates"))
        self.label.setText(self.tr("Similarity"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_4), self.tr("Options"))
        self.btnOk.setText(self.tr("&Ok"))
        self.btnClose.setText(self.tr("&Close"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
