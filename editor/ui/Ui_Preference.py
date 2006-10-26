# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Thu Oct 26 15:51:00 2006
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_frmPreference(object):
    def setupUi(self, frmPreference):
        frmPreference.setObjectName("frmPreference")
        frmPreference.resize(QtCore.QSize(QtCore.QRect(0,0,483,460).size()).expandedTo(frmPreference.minimumSizeHint()))

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

        self.frame2 = QtGui.QFrame(self.tab1)
        self.frame2.setGeometry(QtCore.QRect(10,260,441,51))
        self.frame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame2.setObjectName("frame2")

        self.spinBox = QtGui.QSpinBox(self.frame2)
        self.spinBox.setGeometry(QtCore.QRect(215,10,216,31))
        self.spinBox.setFocusPolicy(QtCore.Qt.TabFocus)
        self.spinBox.setObjectName("spinBox")

        self.label = QtGui.QLabel(self.frame2)
        self.label.setGeometry(QtCore.QRect(10,18,181,18))
        self.label.setObjectName("label")

        self.frame = QtGui.QFrame(self.tab1)
        self.frame.setGeometry(QtCore.QRect(10,20,441,231))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.UserName = QtGui.QTextEdit(self.frame)
        self.UserName.setGeometry(QtCore.QRect(130,20,302,30))
        self.UserName.setFocusPolicy(QtCore.Qt.TabFocus)
        self.UserName.setTabChangesFocus(True)
        self.UserName.setObjectName("UserName")

        self.EmailAddress = QtGui.QTextEdit(self.frame)
        self.EmailAddress.setGeometry(QtCore.QRect(130,60,302,30))
        self.EmailAddress.setFocusPolicy(QtCore.Qt.TabFocus)
        self.EmailAddress.setTabChangesFocus(True)
        self.EmailAddress.setObjectName("EmailAddress")

        self.cbxFullLanguage = QtGui.QComboBox(self.frame)
        self.cbxFullLanguage.setEnabled(True)
        self.cbxFullLanguage.setGeometry(QtCore.QRect(130,100,121,31))
        self.cbxFullLanguage.setFocusPolicy(QtCore.Qt.TabFocus)
        self.cbxFullLanguage.setAcceptDrops(True)
        self.cbxFullLanguage.setEditable(True)
        self.cbxFullLanguage.setObjectName("cbxFullLanguage")

        self.cbxLanguageCode = QtGui.QComboBox(self.frame)
        self.cbxLanguageCode.setEnabled(True)
        self.cbxLanguageCode.setGeometry(QtCore.QRect(350,100,81,31))
        self.cbxLanguageCode.setFocusPolicy(QtCore.Qt.TabFocus)
        self.cbxLanguageCode.setAcceptDrops(False)
        self.cbxLanguageCode.setEditable(True)
        self.cbxLanguageCode.setObjectName("cbxLanguageCode")

        self.SupportTeam = QtGui.QTextEdit(self.frame)
        self.SupportTeam.setGeometry(QtCore.QRect(130,140,301,30))
        self.SupportTeam.setFocusPolicy(QtCore.Qt.TabFocus)
        self.SupportTeam.setTabChangesFocus(True)
        self.SupportTeam.setObjectName("SupportTeam")

        self.cbxTimeZone = QtGui.QComboBox(self.frame)
        self.cbxTimeZone.setEnabled(True)
        self.cbxTimeZone.setGeometry(QtCore.QRect(130,180,301,31))
        self.cbxTimeZone.setFocusPolicy(QtCore.Qt.TabFocus)
        self.cbxTimeZone.setEditable(True)
        self.cbxTimeZone.setObjectName("cbxTimeZone")

        self.label1 = QtGui.QLabel(self.frame)
        self.label1.setGeometry(QtCore.QRect(10,30,71,18))
        self.label1.setObjectName("label1")

        self.label2 = QtGui.QLabel(self.frame)
        self.label2.setGeometry(QtCore.QRect(10,69,81,18))
        self.label2.setObjectName("label2")

        self.label6 = QtGui.QLabel(self.frame)
        self.label6.setGeometry(QtCore.QRect(10,190,61,18))
        self.label6.setObjectName("label6")

        self.label4 = QtGui.QLabel(self.frame)
        self.label4.setGeometry(QtCore.QRect(260,109,91,18))
        self.label4.setObjectName("label4")

        self.label3 = QtGui.QLabel(self.frame)
        self.label3.setGeometry(QtCore.QRect(10,110,118,18))
        self.label3.setObjectName("label3")

        self.label5 = QtGui.QLabel(self.frame)
        self.label5.setGeometry(QtCore.QRect(10,150,81,18))
        self.label5.setObjectName("label5")

        self.chkHeaderAuto = QtGui.QCheckBox(self.tab1)
        self.chkHeaderAuto.setGeometry(QtCore.QRect(10,330,231,20))
        self.chkHeaderAuto.setObjectName("chkHeaderAuto")
        self.tabWidget.addTab(self.tab1, "")

        self.tab2 = QtGui.QWidget()
        self.tab2.setObjectName("tab2")

        self.bntDefaults = QtGui.QPushButton(self.tab2)
        self.bntDefaults.setGeometry(QtCore.QRect(340,230,91,21))
        self.bntDefaults.setObjectName("bntDefaults")

        self.frame21 = QtGui.QFrame(self.tab2)
        self.frame21.setGeometry(QtCore.QRect(20,20,411,201))
        self.frame21.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame21.setFrameShadow(QtGui.QFrame.Raised)
        self.frame21.setObjectName("frame21")

        self.lblComment = QtGui.QLabel(self.frame21)
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

        self.lblTarget = QtGui.QLabel(self.frame21)
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

        self.lblSource = QtGui.QLabel(self.frame21)
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

        self.lblOverView = QtGui.QLabel(self.frame21)
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

        self.bntOverview = QtGui.QPushButton(self.frame21)
        self.bntOverview.setGeometry(QtCore.QRect(330,30,61,21))
        self.bntOverview.setObjectName("bntOverview")

        self.bntSource = QtGui.QPushButton(self.frame21)
        self.bntSource.setGeometry(QtCore.QRect(330,70,61,21))
        self.bntSource.setObjectName("bntSource")

        self.bntTarget = QtGui.QPushButton(self.frame21)
        self.bntTarget.setGeometry(QtCore.QRect(330,110,61,21))
        self.bntTarget.setObjectName("bntTarget")

        self.bntComment = QtGui.QPushButton(self.frame21)
        self.bntComment.setGeometry(QtCore.QRect(330,150,61,21))
        self.bntComment.setObjectName("bntComment")

        self.label21 = QtGui.QLabel(self.frame21)
        self.label21.setGeometry(QtCore.QRect(20,30,61,19))

        font = QtGui.QFont(self.label21.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label21.setFont(font)
        self.label21.setObjectName("label21")

        self.Source = QtGui.QLabel(self.frame21)
        self.Source.setGeometry(QtCore.QRect(20,70,48,17))

        font = QtGui.QFont(self.Source.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.Source.setFont(font)
        self.Source.setObjectName("Source")

        self.label41 = QtGui.QLabel(self.frame21)
        self.label41.setGeometry(QtCore.QRect(20,110,48,17))

        font = QtGui.QFont(self.label41.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label41.setFont(font)
        self.label41.setObjectName("label41")

        self.lblsupportteam = QtGui.QLabel(self.frame21)
        self.lblsupportteam.setGeometry(QtCore.QRect(20,150,61,19))

        font = QtGui.QFont(self.lblsupportteam.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblsupportteam.setFont(font)
        self.lblsupportteam.setObjectName("lblsupportteam")
        self.tabWidget.addTab(self.tab2, "")
        self.gridlayout.addWidget(self.tabWidget,0,0,1,1)

        self.retranslateUi(frmPreference)
        self.cbxFullLanguage.setCurrentIndex(-1)
        QtCore.QObject.connect(self.okButton,QtCore.SIGNAL("clicked()"),frmPreference.accept)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),frmPreference.reject)
        QtCore.QMetaObject.connectSlotsByName(frmPreference)
        frmPreference.setTabOrder(self.UserName,self.EmailAddress)
        frmPreference.setTabOrder(self.EmailAddress,self.cbxFullLanguage)
        frmPreference.setTabOrder(self.cbxFullLanguage,self.cbxLanguageCode)
        frmPreference.setTabOrder(self.cbxLanguageCode,self.SupportTeam)
        frmPreference.setTabOrder(self.SupportTeam,self.cbxTimeZone)
        frmPreference.setTabOrder(self.cbxTimeZone,self.spinBox)
        frmPreference.setTabOrder(self.spinBox,self.okButton)
        frmPreference.setTabOrder(self.okButton,self.cancelButton)
        frmPreference.setTabOrder(self.cancelButton,self.tabWidget)
        frmPreference.setTabOrder(self.tabWidget,self.bntComment)
        frmPreference.setTabOrder(self.bntComment,self.bntTarget)
        frmPreference.setTabOrder(self.bntTarget,self.bntSource)
        frmPreference.setTabOrder(self.bntSource,self.bntDefaults)
        frmPreference.setTabOrder(self.bntDefaults,self.bntOverview)

    def tr(self, string):
        return QtGui.QApplication.translate("frmPreference", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, frmPreference):
        frmPreference.setWindowTitle(self.tr("Preference"))
        self.okButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
        self.label.setText(self.tr("Number of singular/plural forms:"))
        self.label1.setText(self.tr("User name:"))
        self.label2.setText(self.tr("Email address:"))
        self.label6.setText(self.tr("Time zone:"))
        self.label4.setText(self.tr("Language code:"))
        self.label3.setText(self.tr("Language name:"))
        self.label5.setText(self.tr("Support team:"))
        self.chkHeaderAuto.setText(self.tr("Automatically update header on save"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), self.tr("Personalize"))
        self.bntDefaults.setText(self.tr("Defaults"))
        self.bntOverview.setText(self.tr("Choose"))
        self.bntSource.setText(self.tr("Choose"))
        self.bntTarget.setText(self.tr("Choose"))
        self.bntComment.setText(self.tr("Choose"))
        self.label21.setText(self.tr("Overview:"))
        self.Source.setText(self.tr("Source:"))
        self.label41.setText(self.tr("Target:"))
        self.lblsupportteam.setText(self.tr("Comment:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), self.tr("Font"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    frmPreference = QtGui.QDialog()
    ui = Ui_frmPreference()
    ui.setupUi(frmPreference)
    frmPreference.show()
    sys.exit(app.exec_())
