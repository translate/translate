# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/NewProject.ui'
#
# Created: Fri Jun  8 10:59:48 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(QtCore.QSize(QtCore.QRect(0,0,373,279).size()).expandedTo(NewProject.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(NewProject)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,0,1,4)

        self.stackedWidget = QtGui.QStackedWidget(NewProject)
        self.stackedWidget.setEnabled(True)
        self.stackedWidget.setObjectName("stackedWidget")

        self.page1 = QtGui.QWidget()
        self.page1.setObjectName("page1")

        self.gridlayout1 = QtGui.QGridLayout(self.page1)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.frame = QtGui.QFrame(self.page1)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout2 = QtGui.QGridLayout(self.frame)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.cbxProject = QtGui.QComboBox(self.frame)
        self.cbxProject.setObjectName("cbxProject")
        self.gridlayout2.addWidget(self.cbxProject,3,1,1,2)

        self.lblConfigurationfile = QtGui.QLabel(self.frame)
        self.lblConfigurationfile.setObjectName("lblConfigurationfile")
        self.gridlayout2.addWidget(self.lblConfigurationfile,1,0,1,1)

        self.lblprojecttype = QtGui.QLabel(self.frame)
        self.lblprojecttype.setObjectName("lblprojecttype")
        self.gridlayout2.addWidget(self.lblprojecttype,3,0,1,1)

        self.lbllabel = QtGui.QLabel(self.frame)
        self.lbllabel.setObjectName("lbllabel")
        self.gridlayout2.addWidget(self.lbllabel,0,0,1,1)

        self.lbllanguage = QtGui.QLabel(self.frame)
        self.lbllanguage.setObjectName("lbllanguage")
        self.gridlayout2.addWidget(self.lbllanguage,2,0,1,1)

        self.btnBrowse = QtGui.QPushButton(self.frame)
        self.btnBrowse.setIcon(QtGui.QIcon("../images/open.png"))
        self.btnBrowse.setIconSize(QtCore.QSize(24,24))
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridlayout2.addWidget(self.btnBrowse,1,2,1,1)

        self.cbxLanguages = QtGui.QComboBox(self.frame)
        self.cbxLanguages.setObjectName("cbxLanguages")
        self.gridlayout2.addWidget(self.cbxLanguages,2,1,1,2)

        self.projectName = QtGui.QLineEdit(self.frame)
        self.projectName.setObjectName("projectName")
        self.gridlayout2.addWidget(self.projectName,0,1,1,2)

        self.configurationFile = QtGui.QLineEdit(self.frame)
        self.configurationFile.setReadOnly(False)
        self.configurationFile.setObjectName("configurationFile")
        self.gridlayout2.addWidget(self.configurationFile,1,1,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,2,3,2,1)
        self.gridlayout1.addWidget(self.frame,1,0,1,1)

        self.lblProjectwizard = QtGui.QLabel(self.page1)

        font = QtGui.QFont()
        font.setFamily("DejaVu Serif Condensed")
        font.setPointSize(12)
        font.setWeight(75)
        font.setBold(True)
        self.lblProjectwizard.setFont(font)
        self.lblProjectwizard.setAlignment(QtCore.Qt.AlignCenter)
        self.lblProjectwizard.setObjectName("lblProjectwizard")
        self.gridlayout1.addWidget(self.lblProjectwizard,0,0,1,1)
        self.stackedWidget.addWidget(self.page1)

        self.page11 = QtGui.QWidget()
        self.page11.setObjectName("page11")

        self.frame_2 = QtGui.QFrame(self.page11)
        self.frame_2.setGeometry(QtCore.QRect(0,30,349,171))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.gridlayout3 = QtGui.QGridLayout(self.frame_2)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.btnAdd = QtGui.QPushButton(self.frame_2)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout3.addWidget(self.btnAdd,0,1,1,1)

        self.listWidget = QtGui.QListWidget(self.frame_2)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout3.addWidget(self.listWidget,0,0,4,1)

        self.btnClear = QtGui.QPushButton(self.frame_2)
        self.btnClear.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnClear.setObjectName("btnClear")
        self.gridlayout3.addWidget(self.btnClear,1,1,1,1)

        self.btnMoveDown = QtGui.QPushButton(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnMoveDown.sizePolicy().hasHeightForWidth())
        self.btnMoveDown.setSizePolicy(sizePolicy)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout3.addWidget(self.btnMoveDown,3,1,1,1)

        self.btnMoveUp = QtGui.QPushButton(self.frame_2)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout3.addWidget(self.btnMoveUp,2,1,1,1)

        self.chbDiveIntoSubfolders = QtGui.QCheckBox(self.frame_2)
        self.chbDiveIntoSubfolders.setObjectName("chbDiveIntoSubfolders")
        self.gridlayout3.addWidget(self.chbDiveIntoSubfolders,4,0,1,1)

        self.label_4 = QtGui.QLabel(self.page11)
        self.label_4.setGeometry(QtCore.QRect(0,0,291,31))

        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Condensed")
        font.setPointSize(12)
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.stackedWidget.addWidget(self.page11)
        self.gridlayout.addWidget(self.stackedWidget,0,0,1,4)

        self.btnBack = QtGui.QPushButton(NewProject)
        self.btnBack.setObjectName("btnBack")
        self.gridlayout.addWidget(self.btnBack,2,1,1,1)

        self.btnNext = QtGui.QPushButton(NewProject)
        self.btnNext.setObjectName("btnNext")
        self.gridlayout.addWidget(self.btnNext,2,2,1,1)

        self.btnFinish = QtGui.QPushButton(NewProject)
        self.btnFinish.setObjectName("btnFinish")
        self.gridlayout.addWidget(self.btnFinish,2,3,1,1)

        self.btnCancel = QtGui.QPushButton(NewProject)
        self.btnCancel.setObjectName("btnCancel")
        self.gridlayout.addWidget(self.btnCancel,2,0,1,1)

        self.retranslateUi(NewProject)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(QtGui.QApplication.translate("NewProject", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConfigurationfile.setStatusTip(QtGui.QApplication.translate("NewProject", "This is where your project is located. ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConfigurationfile.setText(QtGui.QApplication.translate("NewProject", "Project path:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblprojecttype.setText(QtGui.QApplication.translate("NewProject", "Project type:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbllabel.setText(QtGui.QApplication.translate("NewProject", "Project name:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbllanguage.setText(QtGui.QApplication.translate("NewProject", "Languages:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setWhatsThis(QtGui.QApplication.translate("NewProject", "Browse path of project for your locate.", None, QtGui.QApplication.UnicodeUTF8))
        self.cbxLanguages.setWhatsThis(QtGui.QApplication.translate("NewProject", "Choose the localized language into which your project is going to translate.", None, QtGui.QApplication.UnicodeUTF8))
        self.projectName.setWhatsThis(QtGui.QApplication.translate("NewProject", "Project name is an identification of project name for you. it is shown in project path.", None, QtGui.QApplication.UnicodeUTF8))
        self.configurationFile.setWhatsThis(QtGui.QApplication.translate("NewProject", "This is where your project is located. ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProjectwizard.setText(QtGui.QApplication.translate("NewProject", "Welcome pootling wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setToolTip(QtGui.QApplication.translate("NewProject", "Add TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can add po, xliff files or another folders of files on your local into listwidget.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("NewProject", " &Add", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.setWhatsThis(QtGui.QApplication.translate("NewProject", "Listwidget is displayed items from user add files or folders.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setToolTip(QtGui.QApplication.translate("NewProject", "clear list", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can clear everything in listwidget .", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClear.setText(QtGui.QApplication.translate("NewProject", " &Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setToolTip(QtGui.QApplication.translate("NewProject", "move down", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can move iterm in listwidget from down to up .", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveDown.setText(QtGui.QApplication.translate("NewProject", " Do&wn", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setToolTip(QtGui.QApplication.translate("NewProject", "move up", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setWhatsThis(QtGui.QApplication.translate("NewProject", "You can move iterm in listwidget from up to down ", None, QtGui.QApplication.UnicodeUTF8))
        self.btnMoveUp.setText(QtGui.QApplication.translate("NewProject", " &Up", None, QtGui.QApplication.UnicodeUTF8))
        self.chbDiveIntoSubfolders.setWhatsThis(QtGui.QApplication.translate("NewProject", "Checked/Unchecked of Dive into Subfolders to display files as sub of main folders", None, QtGui.QApplication.UnicodeUTF8))
        self.chbDiveIntoSubfolders.setText(QtGui.QApplication.translate("NewProject", "Dive into Subfolders", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("NewProject", "Add items into list", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBack.setText(QtGui.QApplication.translate("NewProject", "< &Back", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNext.setText(QtGui.QApplication.translate("NewProject", "Next >", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFinish.setText(QtGui.QApplication.translate("NewProject", "&Finish", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("NewProject", "Cancel", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    NewProject = QtGui.QDialog()
    ui = Ui_NewProject()
    ui.setupUi(NewProject)
    NewProject.show()
    sys.exit(app.exec_())
