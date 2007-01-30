# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Jan 26 14:34:22 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_tmsetting(object):
    def setupUi(self, tmsetting):
        tmsetting.setObjectName("tmsetting")
        tmsetting.resize(QtCore.QSize(QtCore.QRect(0,0,350,340).size()).expandedTo(tmsetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(tmsetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tabXliff = QtGui.QTabWidget(tmsetting)
        self.tabXliff.setObjectName("tabXliff")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem = QtGui.QSpacerItem(301,221,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,4,0,1,2)

        self.line = QtGui.QFrame(self.tab)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridlayout1.addWidget(self.line,3,0,1,2)

        self.label = QtGui.QLabel(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

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
        self.gridlayout1.addWidget(self.label,0,0,1,2)

        self.linePOfile = QtGui.QLineEdit(self.tab)
        self.linePOfile.setReadOnly(False)
        self.linePOfile.setObjectName("linePOfile")
        self.gridlayout1.addWidget(self.linePOfile,1,0,1,1)

        self.btnPOfile = QtGui.QPushButton(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPOfile.sizePolicy().hasHeightForWidth())
        self.btnPOfile.setSizePolicy(sizePolicy)
        self.btnPOfile.setObjectName("btnPOfile")
        self.gridlayout1.addWidget(self.btnPOfile,1,1,1,1)

        self.poLookup = QtGui.QCheckBox(self.tab)
        self.poLookup.setAutoFillBackground(False)
        self.poLookup.setChecked(False)
        self.poLookup.setObjectName("poLookup")
        self.gridlayout1.addWidget(self.poLookup,2,0,1,1)
        self.tabXliff.addTab(self.tab, "")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        spacerItem1 = QtGui.QSpacerItem(301,221,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,4,0,1,2)

        self.line_3 = QtGui.QFrame(self.tab_2)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridlayout2.addWidget(self.line_3,3,0,1,2)

        self.btnTMXfile = QtGui.QPushButton(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnTMXfile.sizePolicy().hasHeightForWidth())
        self.btnTMXfile.setSizePolicy(sizePolicy)
        self.btnTMXfile.setObjectName("btnTMXfile")
        self.gridlayout2.addWidget(self.btnTMXfile,1,1,1,1)

        self.tmxLookup = QtGui.QCheckBox(self.tab_2)
        self.tmxLookup.setAutoFillBackground(False)
        self.tmxLookup.setChecked(False)
        self.tmxLookup.setObjectName("tmxLookup")
        self.gridlayout2.addWidget(self.tmxLookup,2,0,1,1)

        self.lineTMXfile = QtGui.QLineEdit(self.tab_2)
        self.lineTMXfile.setReadOnly(False)
        self.lineTMXfile.setObjectName("lineTMXfile")
        self.gridlayout2.addWidget(self.lineTMXfile,1,0,1,1)

        self.label_4 = QtGui.QLabel(self.tab_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label_4.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridlayout2.addWidget(self.label_4,0,0,1,1)
        self.tabXliff.addTab(self.tab_2, "")

        self.tabXliff1 = QtGui.QWidget()
        self.tabXliff1.setObjectName("tabXliff1")

        self.gridlayout3 = QtGui.QGridLayout(self.tabXliff1)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        spacerItem2 = QtGui.QSpacerItem(301,221,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout3.addItem(spacerItem2,4,0,1,2)

        self.lineXliffFile = QtGui.QLineEdit(self.tabXliff1)
        self.lineXliffFile.setReadOnly(False)
        self.lineXliffFile.setObjectName("lineXliffFile")
        self.gridlayout3.addWidget(self.lineXliffFile,1,0,1,1)

        self.xliffLookup = QtGui.QCheckBox(self.tabXliff1)
        self.xliffLookup.setAutoFillBackground(False)
        self.xliffLookup.setChecked(False)
        self.xliffLookup.setObjectName("xliffLookup")
        self.gridlayout3.addWidget(self.xliffLookup,2,0,1,1)

        self.btnXLiffFile = QtGui.QPushButton(self.tabXliff1)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnXLiffFile.sizePolicy().hasHeightForWidth())
        self.btnXLiffFile.setSizePolicy(sizePolicy)
        self.btnXLiffFile.setObjectName("btnXLiffFile")
        self.gridlayout3.addWidget(self.btnXLiffFile,1,1,1,1)

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
        self.gridlayout3.addWidget(self.label_6,0,0,1,1)

        self.line_5 = QtGui.QFrame(self.tabXliff1)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridlayout3.addWidget(self.line_5,3,0,1,2)
        self.tabXliff.addTab(self.tabXliff1, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabXliff.addTab(self.tab_3, "")
        self.gridlayout.addWidget(self.tabXliff,0,0,1,3)

        spacerItem3 = QtGui.QSpacerItem(332,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem3,1,0,1,3)

        spacerItem4 = QtGui.QSpacerItem(231,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem4,2,0,2,1)

        self.btnClose = QtGui.QPushButton(tmsetting)
        self.btnClose.setObjectName("btnClose")
        self.gridlayout.addWidget(self.btnClose,2,2,2,1)

        self.retranslateUi(tmsetting)
        self.tabXliff.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(tmsetting)

    def tr(self, string):
        return QtGui.QApplication.translate("tmsetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, tmsetting):
        tmsetting.setWindowTitle(self.tr("Form"))
        self.label.setText(self.tr("Path to PO translated file"))
        self.btnPOfile.setText(self.tr("&Browse..."))
        self.poLookup.setText(self.tr("LookUp"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab), self.tr("&PO"))
        self.btnTMXfile.setText(self.tr("&Browse..."))
        self.tmxLookup.setText(self.tr("LookUp"))
        self.label_4.setText(self.tr("Path to TMX translated file"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab_2), self.tr("&TMX"))
        self.xliffLookup.setText(self.tr("LookUp"))
        self.btnXLiffFile.setText(self.tr("&Browse..."))
        self.label_6.setText(self.tr("Path to XLiff translated file"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tabXliff1), self.tr("&Xliff"))
        self.tabXliff.setTabText(self.tabXliff.indexOf(self.tab_3), self.tr("&Database"))
        self.btnClose.setText(self.tr("&Close"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmsetting = QtGui.QWidget()
    ui = Ui_tmsetting()
    ui.setupUi(tmsetting)
    tmsetting.show()
    sys.exit(app.exec_())
