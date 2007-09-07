# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Sep  7 16:34:05 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(QtCore.QSize(QtCore.QRect(0,0,468,439).size()).expandedTo(NewProject.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(NewProject)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.frame_2 = QtGui.QFrame(NewProject)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.gridlayout1 = QtGui.QGridLayout(self.frame_2)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        self.gridlayout1.addItem(spacerItem,4,1,1,1)

        self.btnAdd = QtGui.QPushButton(self.frame_2)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,5,3,1,1)

        self.listLocation = QtGui.QListWidget(self.frame_2)
        self.listLocation.setObjectName("listLocation")
        self.gridlayout1.addWidget(self.listLocation,5,1,6,2)

        self.comboLanguage = QtGui.QComboBox(self.frame_2)
        self.comboLanguage.setObjectName("comboLanguage")
        self.gridlayout1.addWidget(self.comboLanguage,2,1,1,2)

        self.lblprojecttype = QtGui.QLabel(self.frame_2)
        self.lblprojecttype.setObjectName("lblprojecttype")
        self.gridlayout1.addWidget(self.lblprojecttype,3,0,1,1)

        self.lbllabel = QtGui.QLabel(self.frame_2)
        self.lbllabel.setObjectName("lbllabel")
        self.gridlayout1.addWidget(self.lbllabel,0,0,1,1)

        self.comboProject = QtGui.QComboBox(self.frame_2)
        self.comboProject.setObjectName("comboProject")
        self.gridlayout1.addWidget(self.comboProject,3,1,1,2)

        self.lbllanguage = QtGui.QLabel(self.frame_2)
        self.lbllanguage.setObjectName("lbllanguage")
        self.gridlayout1.addWidget(self.lbllanguage,2,0,1,1)

        self.lblConfigurationfile = QtGui.QLabel(self.frame_2)
        self.lblConfigurationfile.setObjectName("lblConfigurationfile")
        self.gridlayout1.addWidget(self.lblConfigurationfile,1,0,1,1)

        self.entryName = QtGui.QLineEdit(self.frame_2)
        self.entryName.setObjectName("entryName")
        self.gridlayout1.addWidget(self.entryName,0,1,1,2)

        self.checkIncludeSub = QtGui.QCheckBox(self.frame_2)
        self.checkIncludeSub.setObjectName("checkIncludeSub")
        self.gridlayout1.addWidget(self.checkIncludeSub,11,1,1,2)

        self.entryPath = QtGui.QLineEdit(self.frame_2)
        self.entryPath.setReadOnly(False)
        self.entryPath.setObjectName("entryPath")
        self.gridlayout1.addWidget(self.entryPath,1,1,1,1)

        self.btnBrowse = QtGui.QPushButton(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowse.sizePolicy().hasHeightForWidth())
        self.btnBrowse.setSizePolicy(sizePolicy)
        self.btnBrowse.setIcon(QtGui.QIcon("../images/open.png"))
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridlayout1.addWidget(self.btnBrowse,1,2,1,1)

        self.label = QtGui.QLabel(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label.font())
        font.setWeight(50)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,5,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(65,31,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,10,3,2,1)

        self.btnMoveDown = QtGui.QPushButton(self.frame_2)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout1.addWidget(self.btnMoveDown,9,3,1,1)

        self.btnMoveUp = QtGui.QPushButton(self.frame_2)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout1.addWidget(self.btnMoveUp,8,3,1,1)

        self.btnDelete = QtGui.QPushButton(self.frame_2)
        self.btnDelete.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnDelete.setObjectName("btnDelete")
        self.gridlayout1.addWidget(self.btnDelete,6,3,1,1)

        self.btnClear = QtGui.QPushButton(self.frame_2)
        self.btnClear.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnClear.setObjectName("btnClear")
        self.gridlayout1.addWidget(self.btnClear,7,3,1,1)
        self.gridlayout.addWidget(self.frame_2,1,0,1,2)

        self.lblProjectwizard = QtGui.QLabel(NewProject)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProjectwizard.sizePolicy().hasHeightForWidth())
        self.lblProjectwizard.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblProjectwizard.font())
        font.setPointSize(12)
        self.lblProjectwizard.setFont(font)
        self.lblProjectwizard.setAlignment(QtCore.Qt.AlignCenter)
        self.lblProjectwizard.setObjectName("lblProjectwizard")
        self.gridlayout.addWidget(self.lblProjectwizard,0,0,1,2)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.btnOK = QtGui.QPushButton(NewProject)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOK.sizePolicy().hasHeightForWidth())
        self.btnOK.setSizePolicy(sizePolicy)
        self.btnOK.setObjectName("btnOK")
        self.hboxlayout.addWidget(self.btnOK)

        self.btnCancel = QtGui.QPushButton(NewProject)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCancel.sizePolicy().hasHeightForWidth())
        self.btnCancel.setSizePolicy(sizePolicy)
        self.btnCancel.setObjectName("btnCancel")
        self.hboxlayout.addWidget(self.btnCancel)
        self.gridlayout.addLayout(self.hboxlayout,2,1,1,1)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,2,0,1,1)

        self.retranslateUi(NewProject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)
        NewProject.setTabOrder(self.entryName,self.entryPath)
        NewProject.setTabOrder(self.entryPath,self.btnBrowse)
        NewProject.setTabOrder(self.btnBrowse,self.comboLanguage)
        NewProject.setTabOrder(self.comboLanguage,self.comboProject)
        NewProject.setTabOrder(self.comboProject,self.listLocation)
        NewProject.setTabOrder(self.listLocation,self.btnAdd)
        NewProject.setTabOrder(self.btnAdd,self.btnDelete)
        NewProject.setTabOrder(self.btnDelete,self.btnClear)
        NewProject.setTabOrder(self.btnClear,self.btnMoveUp)
        NewProject.setTabOrder(self.btnMoveUp,self.btnMoveDown)
        NewProject.setTabOrder(self.btnMoveDown,self.checkIncludeSub)
        NewProject.setTabOrder(self.checkIncludeSub,self.btnOK)
        NewProject.setTabOrder(self.btnOK,self.btnCancel)

    def tr(self, string):
        return QtGui.QApplication.translate("NewProject", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(self.tr("Dialog"))
        self.btnAdd.setToolTip(self.tr("Add catalog file or folder"))
        self.btnAdd.setText(self.tr(" &Add"))
        self.listLocation.setToolTip(self.tr("The locations contain files or folders of your project."))
        self.comboLanguage.setToolTip(self.tr("The language which you translate to."))
        self.lblprojecttype.setText(self.tr("Type:"))
        self.lbllabel.setText(self.tr("Name:"))
        self.lbllanguage.setText(self.tr("Language:"))
        self.lblConfigurationfile.setStatusTip(self.tr("This is where your project is located. "))
        self.lblConfigurationfile.setText(self.tr("Path:"))
        self.entryName.setToolTip(self.tr("The name of your project."))
        self.checkIncludeSub.setToolTip(self.tr("Check to include sub folders in each location."))
        self.checkIncludeSub.setText(self.tr("Dive into sub folders"))
        self.entryPath.setToolTip(self.tr("The place where you store your project file."))
        self.btnBrowse.setWhatsThis(self.tr("Browse path of project for your locate."))
        self.label.setText(self.tr("Location:"))
        self.btnMoveDown.setToolTip(self.tr("Move down"))
        self.btnMoveDown.setText(self.tr(" Do&wn"))
        self.btnMoveUp.setToolTip(self.tr("Move up"))
        self.btnMoveUp.setText(self.tr(" &Up"))
        self.btnDelete.setToolTip(self.tr("Delete catalog file or folder"))
        self.btnDelete.setText(self.tr(" &Delete"))
        self.btnClear.setToolTip(self.tr("Clear list"))
        self.btnClear.setText(self.tr(" &Clear"))
        self.lblProjectwizard.setText(self.tr("Configure Project"))
        self.btnOK.setText(self.tr("&OK"))
        self.btnCancel.setText(self.tr("&Cancel"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    NewProject = QtGui.QDialog()
    ui = Ui_NewProject()
    ui.setupUi(NewProject)
    NewProject.show()
    sys.exit(app.exec_())
