# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/NewProject.ui'
#
# Created: Fri Sep  7 09:07:29 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(QtCore.QSize(QtCore.QRect(0,0,468,464).size()).expandedTo(NewProject.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(NewProject)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.btnFinish = QtGui.QPushButton(NewProject)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFinish.sizePolicy().hasHeightForWidth())
        self.btnFinish.setSizePolicy(sizePolicy)
        self.btnFinish.setObjectName("btnFinish")
        self.hboxlayout.addWidget(self.btnFinish)

        self.btnCancel = QtGui.QPushButton(NewProject)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCancel.sizePolicy().hasHeightForWidth())
        self.btnCancel.setSizePolicy(sizePolicy)
        self.btnCancel.setObjectName("btnCancel")
        self.hboxlayout.addWidget(self.btnCancel)
        self.gridlayout.addLayout(self.hboxlayout,1,1,1,1)

        self.frame_2 = QtGui.QFrame(NewProject)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.gridlayout1 = QtGui.QGridLayout(self.frame_2)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        self.gridlayout1.addItem(spacerItem1,6,1,1,1)

        self.btnMoveDown = QtGui.QPushButton(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnMoveDown.sizePolicy().hasHeightForWidth())
        self.btnMoveDown.setSizePolicy(sizePolicy)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout1.addWidget(self.btnMoveDown,10,3,1,1)

        self.btnAdd = QtGui.QPushButton(self.frame_2)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,7,3,1,1)

        self.btnClear = QtGui.QPushButton(self.frame_2)
        self.btnClear.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnClear.setObjectName("btnClear")
        self.gridlayout1.addWidget(self.btnClear,8,3,1,1)

        self.btnMoveUp = QtGui.QPushButton(self.frame_2)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout1.addWidget(self.btnMoveUp,9,3,1,1)

        spacerItem2 = QtGui.QSpacerItem(20,81,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem2,11,3,2,1)

        self.listWidget = QtGui.QListWidget(self.frame_2)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,7,1,5,2)

        self.cbxLanguages = QtGui.QComboBox(self.frame_2)
        self.cbxLanguages.setObjectName("cbxLanguages")
        self.gridlayout1.addWidget(self.cbxLanguages,4,1,1,2)

        self.lblprojecttype = QtGui.QLabel(self.frame_2)
        self.lblprojecttype.setObjectName("lblprojecttype")
        self.gridlayout1.addWidget(self.lblprojecttype,5,0,1,1)

        self.lbllabel = QtGui.QLabel(self.frame_2)
        self.lbllabel.setObjectName("lbllabel")
        self.gridlayout1.addWidget(self.lbllabel,2,0,1,1)

        self.cbxProject = QtGui.QComboBox(self.frame_2)
        self.cbxProject.setObjectName("cbxProject")
        self.gridlayout1.addWidget(self.cbxProject,5,1,1,2)

        self.lbllanguage = QtGui.QLabel(self.frame_2)
        self.lbllanguage.setObjectName("lbllanguage")
        self.gridlayout1.addWidget(self.lbllanguage,4,0,1,1)

        self.lblConfigurationfile = QtGui.QLabel(self.frame_2)
        self.lblConfigurationfile.setObjectName("lblConfigurationfile")
        self.gridlayout1.addWidget(self.lblConfigurationfile,3,0,1,1)

        self.projectName = QtGui.QLineEdit(self.frame_2)
        self.projectName.setObjectName("projectName")
        self.gridlayout1.addWidget(self.projectName,2,1,1,2)

        self.chbDiveIntoSubfolders = QtGui.QCheckBox(self.frame_2)
        self.chbDiveIntoSubfolders.setObjectName("chbDiveIntoSubfolders")
        self.gridlayout1.addWidget(self.chbDiveIntoSubfolders,12,1,1,2)

        self.configurationFile = QtGui.QLineEdit(self.frame_2)
        self.configurationFile.setReadOnly(False)
        self.configurationFile.setObjectName("configurationFile")
        self.gridlayout1.addWidget(self.configurationFile,3,1,1,1)

        self.btnBrowse = QtGui.QPushButton(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowse.sizePolicy().hasHeightForWidth())
        self.btnBrowse.setSizePolicy(sizePolicy)
        self.btnBrowse.setIcon(QtGui.QIcon("../images/open.png"))
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridlayout1.addWidget(self.btnBrowse,3,2,1,1)

        self.label = QtGui.QLabel(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,7,0,1,1)

        self.lblProjectwizard = QtGui.QLabel(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProjectwizard.sizePolicy().hasHeightForWidth())
        self.lblProjectwizard.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.lblProjectwizard.setFont(font)
        self.lblProjectwizard.setAlignment(QtCore.Qt.AlignCenter)
        self.lblProjectwizard.setObjectName("lblProjectwizard")
        self.gridlayout1.addWidget(self.lblProjectwizard,0,0,1,4)

        spacerItem3 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        self.gridlayout1.addItem(spacerItem3,1,1,1,1)
        self.gridlayout.addWidget(self.frame_2,0,0,1,2)

        self.retranslateUi(NewProject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(QtGui.QApplication.translate("NewProject", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFinish.setText(QtGui.QApplication.translate("NewProject", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("NewProject", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setToolTip(QtGui.QApplication.translate("NewProject", "move down", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can move iterm in listwidget from down to up .", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setText(QtGui.QApplication.translate("NewProject", " Do&wn", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setToolTip(QtGui.QApplication.translate("NewProject", "Add TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can add po, xliff files or another folders of files on your local into listwidget.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("NewProject", " &Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setToolTip(QtGui.QApplication.translate("NewProject", "clear list", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can clear everything in listwidget .", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setText(QtGui.QApplication.translate("NewProject", " &Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setToolTip(QtGui.QApplication.translate("NewProject", "move up", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can move iterm in listwidget from up to down ", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setText(QtGui.QApplication.translate("NewProject", " &Up", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.setWhatsThis(QtGui.QApplication.translate("NewProject", "Listwidget is displayed items from user add files or folders.", None, QtGui.QApplication.UnicodeUTF8))
        self.cbxLanguages.setWhatsThis(QtGui.QApplication.translate("NewProject", "Choose the localized language into which your project is going to translate.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblprojecttype.setText(QtGui.QApplication.translate("NewProject", "Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbllabel.setText(QtGui.QApplication.translate("NewProject", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbllanguage.setText(QtGui.QApplication.translate("NewProject", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConfigurationfile.setStatusTip(QtGui.QApplication.translate("NewProject", "This is where your project is located. ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConfigurationfile.setText(QtGui.QApplication.translate("NewProject", "Path:", None, QtGui.QApplication.UnicodeUTF8))
        self.projectName.setWhatsThis(QtGui.QApplication.translate("NewProject", "Project name is an identification of project name for you. it is shown in project path.", None, QtGui.QApplication.UnicodeUTF8))
        self.chbDiveIntoSubfolders.setWhatsThis(QtGui.QApplication.translate("NewProject", "Checked/Unchecked of Dive into Subfolders to display files as sub of main folders", None, QtGui.QApplication.UnicodeUTF8))
        self.chbDiveIntoSubfolders.setText(QtGui.QApplication.translate("NewProject", "Dive into sub folders", None, QtGui.QApplication.UnicodeUTF8))
        self.configurationFile.setWhatsThis(QtGui.QApplication.translate("NewProject", "This is where your project is located. ", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setWhatsThis(QtGui.QApplication.translate("NewProject", "Browse path of project for your locate.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("NewProject", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProjectwizard.setText(QtGui.QApplication.translate("NewProject", "Project properties", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    NewProject = QtGui.QDialog()
    ui = Ui_NewProject()
    ui.setupUi(NewProject)
    NewProject.show()
    sys.exit(app.exec_())
