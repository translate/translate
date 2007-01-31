# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Jan 31 15:37:28 2007
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

        self.btnClose = QtGui.QPushButton(tmsetting)
        self.btnClose.setObjectName("btnClose")
        self.gridlayout.addWidget(self.btnClose,2,2,1,1)

        self.btnOk = QtGui.QPushButton(tmsetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,2,1,1,1)

        spacerItem = QtGui.QSpacerItem(141,46,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,2,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(332,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1,1,0,1,3)

        self.tabXliff = QtGui.QTabWidget(tmsetting)
        self.tabXliff.setObjectName("tabXliff")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.frame_3 = QtGui.QFrame(self.tab)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")

        self.gridlayout2 = QtGui.QGridLayout(self.frame_3)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.radPOFolder = QtGui.QRadioButton(self.frame_3)
        self.radPOFolder.setObjectName("radPOFolder")
        self.gridlayout2.addWidget(self.radPOFolder,1,0,1,1)

        self.radPOFile = QtGui.QRadioButton(self.frame_3)
        self.radPOFile.setChecked(True)
        self.radPOFile.setObjectName("radPOFile")
        self.gridlayout2.addWidget(self.radPOFile,0,0,1,1)

        self.radPOFolder_sub = QtGui.QRadioButton(self.frame_3)
        self.radPOFolder_sub.setObjectName("radPOFolder_sub")
        self.gridlayout2.addWidget(self.radPOFolder_sub,2,0,1,1)
        self.gridlayout1.addWidget(self.frame_3,1,0,1,1)

        self.linePOFile = QtGui.QLineEdit(self.tab)
        self.linePOFile.setReadOnly(False)
        self.linePOFile.setObjectName("linePOFile")
        self.gridlayout1.addWidget(self.linePOFile,3,0,1,1)

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
        self.gridlayout1.addWidget(self.label_11,2,0,1,1)

        self.label_10 = QtGui.QLabel(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_10.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridlayout1.addWidget(self.label_10,0,0,1,1)

        self.btnPOFile = QtGui.QPushButton(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPOFile.sizePolicy().hasHeightForWidth())
        self.btnPOFile.setSizePolicy(sizePolicy)
        self.btnPOFile.setObjectName("btnPOFile")
        self.gridlayout1.addWidget(self.btnPOFile,3,1,1,1)

        self.poLookup = QtGui.QCheckBox(self.tab)
        self.poLookup.setAutoFillBackground(False)
        self.poLookup.setChecked(False)
        self.poLookup.setObjectName("poLookup")
        self.gridlayout1.addWidget(self.poLookup,4,0,1,1)
        self.tabXliff.addTab(self.tab, "")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.gridlayout3 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.btnTMXFile = QtGui.QPushButton(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnTMXFile.sizePolicy().hasHeightForWidth())
        self.btnTMXFile.setSizePolicy(sizePolicy)
        self.btnTMXFile.setObjectName("btnTMXFile")
        self.gridlayout3.addWidget(self.btnTMXFile,3,1,1,1)

        self.lineTMXFile = QtGui.QLineEdit(self.tab_2)
        self.lineTMXFile.setReadOnly(False)
        self.lineTMXFile.setObjectName("lineTMXFile")
        self.gridlayout3.addWidget(self.lineTMXFile,3,0,1,1)

        self.tmxLookup = QtGui.QCheckBox(self.tab_2)
        self.tmxLookup.setAutoFillBackground(False)
        self.tmxLookup.setChecked(False)
        self.tmxLookup.setObjectName("tmxLookup")
        self.gridlayout3.addWidget(self.tmxLookup,4,0,1,1)

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
        self.gridlayout3.addWidget(self.label_9,2,0,1,1)

        self.label_8 = QtGui.QLabel(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_8.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridlayout3.addWidget(self.label_8,0,0,1,1)

        self.frame_2 = QtGui.QFrame(self.tab_2)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.gridlayout4 = QtGui.QGridLayout(self.frame_2)
        self.gridlayout4.setMargin(9)
        self.gridlayout4.setSpacing(6)
        self.gridlayout4.setObjectName("gridlayout4")

        self.radTMXFolder = QtGui.QRadioButton(self.frame_2)
        self.radTMXFolder.setObjectName("radTMXFolder")
        self.gridlayout4.addWidget(self.radTMXFolder,1,0,1,1)

        self.radTMXFile = QtGui.QRadioButton(self.frame_2)
        self.radTMXFile.setChecked(True)
        self.radTMXFile.setObjectName("radTMXFile")
        self.gridlayout4.addWidget(self.radTMXFile,0,0,1,1)

        self.radTMXFolder_sub = QtGui.QRadioButton(self.frame_2)
        self.radTMXFolder_sub.setObjectName("radTMXFolder_sub")
        self.gridlayout4.addWidget(self.radTMXFolder_sub,2,0,1,1)
        self.gridlayout3.addWidget(self.frame_2,1,0,1,1)
        self.tabXliff.addTab(self.tab_2, "")

        self.tabXliff1 = QtGui.QWidget()
        self.tabXliff1.setObjectName("tabXliff1")

        self.gridlayout5 = QtGui.QGridLayout(self.tabXliff1)
        self.gridlayout5.setMargin(9)
        self.gridlayout5.setSpacing(6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.xliffLookup = QtGui.QCheckBox(self.tabXliff1)
        self.xliffLookup.setAutoFillBackground(False)
        self.xliffLookup.setChecked(False)
        self.xliffLookup.setObjectName("xliffLookup")
        self.gridlayout5.addWidget(self.xliffLookup,4,0,1,1)

        self.label_6 = QtGui.QLabel(self.tabXliff1)

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
        self.gridlayout5.addWidget(self.label_6,2,0,1,1)

        self.btnXLiffFile = QtGui.QPushButton(self.tabXliff1)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnXLiffFile.sizePolicy().hasHeightForWidth())
        self.btnXLiffFile.setSizePolicy(sizePolicy)
        self.btnXLiffFile.setObjectName("btnXLiffFile")
        self.gridlayout5.addWidget(self.btnXLiffFile,3,1,1,1)

        self.lineXliffFile = QtGui.QLineEdit(self.tabXliff1)
        self.lineXliffFile.setReadOnly(False)
        self.lineXliffFile.setObjectName("lineXliffFile")
        self.gridlayout5.addWidget(self.lineXliffFile,3,0,1,1)

        self.label_7 = QtGui.QLabel(self.tabXliff1)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_7.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridlayout5.addWidget(self.label_7,0,0,1,1)

        self.frame = QtGui.QFrame(self.tabXliff1)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout6 = QtGui.QGridLayout(self.frame)
        self.gridlayout6.setMargin(9)
        self.gridlayout6.setSpacing(6)
        self.gridlayout6.setObjectName("gridlayout6")

        self.radXLiffFolder = QtGui.QRadioButton(self.frame)
        self.radXLiffFolder.setObjectName("radXLiffFolder")
        self.gridlayout6.addWidget(self.radXLiffFolder,1,0,1,1)

        self.radXLiffFile = QtGui.QRadioButton(self.frame)
        self.radXLiffFile.setChecked(True)
        self.radXLiffFile.setObjectName("radXLiffFile")
        self.gridlayout6.addWidget(self.radXLiffFile,0,0,1,1)

        self.radXLiffFolder_sub = QtGui.QRadioButton(self.frame)
        self.radXLiffFolder_sub.setObjectName("radXLiffFolder_sub")
        self.gridlayout6.addWidget(self.radXLiffFolder_sub,2,0,1,1)
        self.gridlayout5.addWidget(self.frame,1,0,1,1)
        self.tabXliff.addTab(self.tabXliff1, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabXliff.addTab(self.tab_3, "")
        self.gridlayout.addWidget(self.tabXliff,0,0,1,3)

        self.retranslateUi(tmsetting)
        self.tabXliff.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Translation Memory Settings"))
        self.btnClose.setText(self.tr("&Close"))
        self.btnOk.setText(self.tr("&Ok"))
        self.radPOFolder.setText(self.tr("Folders"))
        self.radPOFile.setText(self.tr("Files"))
        self.radPOFolder_sub.setText(self.tr("Folders and subfolders"))
        self.label_11.setText(self.tr("Path to XLiff translated file"))
        self.label_10.setText(self.tr("Scan options"))
        self.btnPOFile.setText(self.tr("&Browse..."))
        self.poLookup.setText(self.tr("LookUp"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab), self.tr("&PO"))
        self.btnTMXFile.setText(self.tr("&Browse..."))
        self.tmxLookup.setText(self.tr("LookUp"))
        self.label_9.setText(self.tr("Path to XLiff translated file"))
        self.label_8.setText(self.tr("Scan options"))
        self.radTMXFolder.setText(self.tr("Folders"))
        self.radTMXFile.setText(self.tr("Files"))
        self.radTMXFolder_sub.setText(self.tr("Folders and subfolders"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab_2), self.tr("&TMX"))
        self.xliffLookup.setText(self.tr("LookUp"))
        self.label_6.setText(self.tr("Path to XLiff translated file"))
        self.btnXLiffFile.setText(self.tr("&Browse..."))
        self.label_7.setText(self.tr("Scan options"))
        self.radXLiffFolder.setText(self.tr("Folders"))
        self.radXLiffFile.setText(self.tr("Files"))
        self.radXLiffFolder_sub.setText(self.tr("Folders and subfolders"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tabXliff1), self.tr("&Xliff"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab_3), self.tr("&Database"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
