# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Thu Oct 12 15:32:21 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmPreference(object):
    def setupUi(self, frmPreference):
        frmPreference.setObjectName("frmPreference")
        frmPreference.resize(QtCore.QSize(QtCore.QRect(0,0,485,455).size()).expandedTo(frmPreference.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(frmPreference)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.okButton = QtGui.QPushButton(frmPreference)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton(frmPreference)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self.gridlayout.addLayout(self.hboxlayout,1,0,1,1)

        self.tabWidget = QtGui.QTabWidget(frmPreference)
        self.tabWidget.setEnabled(True)

        font = QtGui.QFont(self.tabWidget.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.tabWidget.setFont(font)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName("tabWidget")

        self.tab1 = QtGui.QWidget()
        self.tab1.setEnabled(True)
        self.tab1.setObjectName("tab1")

        self.frame = QtGui.QFrame(self.tab1)
        self.frame.setGeometry(QtCore.QRect(10,50,431,231))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.label4 = QtGui.QLabel(self.frame)
        self.label4.setGeometry(QtCore.QRect(240,110,101,18))
        self.label4.setObjectName("label4")

        self.label5 = QtGui.QLabel(self.frame)
        self.label5.setGeometry(QtCore.QRect(10,150,91,18))
        self.label5.setObjectName("label5")

        self.label6 = QtGui.QLabel(self.frame)
        self.label6.setGeometry(QtCore.QRect(10,190,97,17))
        self.label6.setObjectName("label6")

        self.EmailAddress = QtGui.QTextEdit(self.frame)
        self.EmailAddress.setGeometry(QtCore.QRect(140,60,275,30))
        self.EmailAddress.setTabChangesFocus(True)
        self.EmailAddress.setObjectName("EmailAddress")

        self.FullLanguage = QtGui.QTextEdit(self.frame)
        self.FullLanguage.setGeometry(QtCore.QRect(140,100,92,30))
        self.FullLanguage.setTabChangesFocus(True)
        self.FullLanguage.setObjectName("FullLanguage")

        self.Code = QtGui.QTextEdit(self.frame)
        self.Code.setGeometry(QtCore.QRect(340,100,75,30))
        self.Code.setTabChangesFocus(True)
        self.Code.setObjectName("Code")

        self.SupportTeam = QtGui.QTextEdit(self.frame)
        self.SupportTeam.setGeometry(QtCore.QRect(140,140,275,30))
        self.SupportTeam.setTabChangesFocus(True)
        self.SupportTeam.setObjectName("SupportTeam")

        self.TimeZone = QtGui.QTextEdit(self.frame)
        self.TimeZone.setGeometry(QtCore.QRect(140,180,275,30))
        self.TimeZone.setTabChangesFocus(True)
        self.TimeZone.setObjectName("TimeZone")

        self.label1 = QtGui.QLabel(self.frame)
        self.label1.setGeometry(QtCore.QRect(10,30,71,18))
        self.label1.setObjectName("label1")

        self.label2 = QtGui.QLabel(self.frame)
        self.label2.setGeometry(QtCore.QRect(10,70,121,18))
        self.label2.setObjectName("label2")

        self.label3 = QtGui.QLabel(self.frame)
        self.label3.setGeometry(QtCore.QRect(10,110,118,18))
        self.label3.setObjectName("label3")

        self.UserName = QtGui.QTextEdit(self.frame)
        self.UserName.setGeometry(QtCore.QRect(140,20,275,30))
        self.UserName.setTabChangesFocus(True)
        self.UserName.setObjectName("UserName")

        self.frame2 = QtGui.QFrame(self.tab1)
        self.frame2.setGeometry(QtCore.QRect(10,290,431,51))
        self.frame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame2.setObjectName("frame2")

        self.label = QtGui.QLabel(self.frame2)
        self.label.setGeometry(QtCore.QRect(10,20,181,18))
        self.label.setObjectName("label")

        self.spinBox = QtGui.QSpinBox(self.frame2)
        self.spinBox.setGeometry(QtCore.QRect(200,10,216,31))
        self.spinBox.setObjectName("spinBox")

        self.label0 = QtGui.QLabel(self.tab1)
        self.label0.setGeometry(QtCore.QRect(10,10,301,20))

        font = QtGui.QFont(self.label0.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label0.setFont(font)
        self.label0.setObjectName("label0")

        self.line = QtGui.QFrame(self.tab1)
        self.line.setGeometry(QtCore.QRect(10,30,431,16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget.addTab(self.tab1, "")

        self.tab2 = QtGui.QWidget()
        self.tab2.setObjectName("tab2")

        self.line_2 = QtGui.QFrame(self.tab2)
        self.line_2.setGeometry(QtCore.QRect(20,40,431,16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.label0_2 = QtGui.QLabel(self.tab2)
        self.label0_2.setGeometry(QtCore.QRect(20,20,91,20))

        font = QtGui.QFont(self.label0_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label0_2.setFont(font)
        self.label0_2.setObjectName("label0_2")

        self.frame_2 = QtGui.QFrame(self.tab2)
        self.frame_2.setGeometry(QtCore.QRect(20,80,431,221))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.label21 = QtGui.QLabel(self.frame_2)
        self.label21.setGeometry(QtCore.QRect(20,30,61,19))

        font = QtGui.QFont(self.label21.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label21.setFont(font)
        self.label21.setObjectName("label21")

        self.bntOverview = QtGui.QPushButton(self.frame_2)
        self.bntOverview.setGeometry(QtCore.QRect(330,30,61,21))
        self.bntOverview.setObjectName("bntOverview")

        self.label51 = QtGui.QLabel(self.frame_2)
        self.label51.setGeometry(QtCore.QRect(20,150,61,19))

        font = QtGui.QFont(self.label51.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label51.setFont(font)
        self.label51.setObjectName("label51")

        self.bntComment = QtGui.QPushButton(self.frame_2)
        self.bntComment.setGeometry(QtCore.QRect(330,150,61,21))
        self.bntComment.setObjectName("bntComment")

        self.label41 = QtGui.QLabel(self.frame_2)
        self.label41.setGeometry(QtCore.QRect(20,110,48,17))

        font = QtGui.QFont(self.label41.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label41.setFont(font)
        self.label41.setObjectName("label41")

        self.bntTarget = QtGui.QPushButton(self.frame_2)
        self.bntTarget.setGeometry(QtCore.QRect(330,110,61,21))
        self.bntTarget.setObjectName("bntTarget")

        self.Source = QtGui.QLabel(self.frame_2)
        self.Source.setGeometry(QtCore.QRect(20,70,48,17))

        font = QtGui.QFont(self.Source.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.Source.setFont(font)
        self.Source.setObjectName("Source")

        self.bntSource = QtGui.QPushButton(self.frame_2)
        self.bntSource.setGeometry(QtCore.QRect(330,70,61,21))
        self.bntSource.setObjectName("bntSource")

        self.lblOverView = QtGui.QLabel(self.frame_2)
        self.lblOverView.setGeometry(QtCore.QRect(100,30,211,23))

        font = QtGui.QFont(self.lblOverView.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblOverView.setFont(font)
        self.lblOverView.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblOverView.setObjectName("lblOverView")

        self.lblSource = QtGui.QLabel(self.frame_2)
        self.lblSource.setGeometry(QtCore.QRect(100,70,211,21))

        font = QtGui.QFont(self.lblSource.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblSource.setFont(font)
        self.lblSource.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblSource.setObjectName("lblSource")

        self.lblTarget = QtGui.QLabel(self.frame_2)
        self.lblTarget.setGeometry(QtCore.QRect(100,110,211,21))

        font = QtGui.QFont(self.lblTarget.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblTarget.setFont(font)
        self.lblTarget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblTarget.setObjectName("lblTarget")

        self.lblComment = QtGui.QLabel(self.frame_2)
        self.lblComment.setGeometry(QtCore.QRect(100,150,211,21))

        font = QtGui.QFont(self.lblComment.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblComment.setFont(font)
        self.lblComment.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblComment.setObjectName("lblComment")
        self.tabWidget.addTab(self.tab2, "")
        self.gridlayout.addWidget(self.tabWidget,0,0,1,1)

        self.retranslateUi(frmPreference)
        QtCore.QObject.connect(self.okButton,QtCore.SIGNAL("clicked()"),frmPreference.accept)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),frmPreference.reject)
        QtCore.QMetaObject.connectSlotsByName(frmPreference)
        frmPreference.setTabOrder(self.UserName,self.EmailAddress)
        frmPreference.setTabOrder(self.EmailAddress,self.FullLanguage)
        frmPreference.setTabOrder(self.FullLanguage,self.Code)
        frmPreference.setTabOrder(self.Code,self.SupportTeam)
        frmPreference.setTabOrder(self.SupportTeam,self.TimeZone)
        frmPreference.setTabOrder(self.TimeZone,self.spinBox)
        frmPreference.setTabOrder(self.spinBox,self.okButton)
        frmPreference.setTabOrder(self.okButton,self.cancelButton)
        frmPreference.setTabOrder(self.cancelButton,self.tabWidget)

    def tr(self, string):
        return QtGui.QApplication.translate("frmPreference", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmPreference):
        frmPreference.setWindowTitle(self.tr("Preference"))
        self.okButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
        self.label4.setText(self.tr("Language Code:"))
        self.label5.setText(self.tr("Support Team:"))
        self.label6.setText(self.tr("Time Zone:"))
        self.label1.setText(self.tr("UserName:"))
        self.label2.setText(self.tr("Your email address:"))
        self.label3.setText(self.tr("Full Language Name:"))
        self.label.setText(self.tr("Number of Singular/Plular Forms:"))
        self.label0.setText(self.tr("Information About You And Translation Team"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), self.tr("Personalize"))
        self.label0_2.setText(self.tr("Font Setting"))
        self.label21.setText(self.tr("Overview"))
        self.bntOverview.setText(self.tr("Choose"))
        self.label51.setText(self.tr("Comment"))
        self.bntComment.setText(self.tr("Choose"))
        self.label41.setText(self.tr("Target"))
        self.bntTarget.setText(self.tr("Choose"))
        self.Source.setText(self.tr("Source"))
        self.bntSource.setText(self.tr("Choose"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), self.tr("Font"))
