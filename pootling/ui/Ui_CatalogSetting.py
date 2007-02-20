# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Tue Feb 20 15:45:32 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_catalogSetting(object):
    def setupUi(self, catalogSetting):
        catalogSetting.setObjectName("catalogSetting")
        catalogSetting.resize(QtCore.QSize(QtCore.QRect(0,0,406,331).size()).expandedTo(catalogSetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(catalogSetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tabOptions = QtGui.QTabWidget(catalogSetting)
        self.tabOptions.setObjectName("tabOptions")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,7,0,1,1)

        self.checkBox = QtGui.QCheckBox(self.tab)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout1.addWidget(self.checkBox,6,0,1,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)

        self.listWidget = QtGui.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,5,1)

        self.btnMoveUp = QtGui.QPushButton(self.tab)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout1.addWidget(self.btnMoveUp,4,1,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.btnRemoveAll = QtGui.QPushButton(self.tab)
        self.btnRemoveAll.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnRemoveAll.setObjectName("btnRemoveAll")
        self.gridlayout1.addWidget(self.btnRemoveAll,3,1,1,1)

        self.btnMoveDown = QtGui.QPushButton(self.tab)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout1.addWidget(self.btnMoveDown,5,1,1,1)

        self.btnRemove = QtGui.QPushButton(self.tab)
        self.btnRemove.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnRemove.setObjectName("btnRemove")
        self.gridlayout1.addWidget(self.btnRemove,2,1,1,1)
        self.tabOptions.addTab(self.tab, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_3)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,2,0,1,1)

        self.label = QtGui.QLabel(self.tab_3)
        self.label.setObjectName("label")
        self.gridlayout2.addWidget(self.label,0,0,1,1)

        self.frame = QtGui.QFrame(self.tab_3)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout3 = QtGui.QGridLayout(self.frame)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.chbtotal = QtGui.QCheckBox(self.frame)
        self.chbtotal.setChecked(True)
        self.chbtotal.setObjectName("chbtotal")
        self.gridlayout3.addWidget(self.chbtotal,0,1,1,1)

        self.chbtranslator = QtGui.QCheckBox(self.frame)
        self.chbtranslator.setChecked(True)
        self.chbtranslator.setObjectName("chbtranslator")
        self.gridlayout3.addWidget(self.chbtranslator,0,2,1,1)

        self.chbuntranslated = QtGui.QCheckBox(self.frame)
        self.chbuntranslated.setChecked(True)
        self.chbuntranslated.setObjectName("chbuntranslated")
        self.gridlayout3.addWidget(self.chbuntranslated,2,0,1,1)

        self.chbfuzzy = QtGui.QCheckBox(self.frame)
        self.chbfuzzy.setChecked(True)
        self.chbfuzzy.setObjectName("chbfuzzy")
        self.gridlayout3.addWidget(self.chbfuzzy,1,0,1,1)

        self.chbname = QtGui.QCheckBox(self.frame)
        self.chbname.setChecked(True)
        self.chbname.setObjectName("chbname")
        self.gridlayout3.addWidget(self.chbname,0,0,1,1)

        self.chblastrevision = QtGui.QCheckBox(self.frame)
        self.chblastrevision.setChecked(True)
        self.chblastrevision.setObjectName("chblastrevision")
        self.gridlayout3.addWidget(self.chblastrevision,2,1,1,2)

        self.chbSVN = QtGui.QCheckBox(self.frame)
        self.chbSVN.setChecked(True)
        self.chbSVN.setObjectName("chbSVN")
        self.gridlayout3.addWidget(self.chbSVN,1,1,1,1)
        self.gridlayout2.addWidget(self.frame,1,0,1,1)
        self.tabOptions.addTab(self.tab_3, "")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,2)

        spacerItem2 = QtGui.QSpacerItem(311,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,1,0,2,1)

        self.btnOk = QtGui.QPushButton(catalogSetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,2,1,1,1)

        self.retranslateUi(catalogSetting)
        self.tabOptions.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(catalogSetting)
        catalogSetting.setTabOrder(self.tabOptions,self.listWidget)
        catalogSetting.setTabOrder(self.listWidget,self.btnAdd)
        catalogSetting.setTabOrder(self.btnAdd,self.btnRemove)
        catalogSetting.setTabOrder(self.btnRemove,self.btnRemoveAll)
        catalogSetting.setTabOrder(self.btnRemoveAll,self.btnMoveUp)
        catalogSetting.setTabOrder(self.btnMoveUp,self.btnMoveDown)
        catalogSetting.setTabOrder(self.btnMoveDown,self.checkBox)
        catalogSetting.setTabOrder(self.checkBox,self.btnOk)

    def tr(self, string):
        return QtGui.QApplication.translate("catalogSetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, catalogSetting):
        catalogSetting.setWindowTitle(self.tr("Catalog Settings"))
        self.checkBox.setText(self.tr("Dive into Subfolders"))
        self.btnAdd.setToolTip(self.tr("Add TM"))
        self.btnAdd.setText(self.tr(" &Add"))
        self.btnMoveUp.setToolTip(self.tr("move up"))
        self.btnMoveUp.setText(self.tr(" &Up"))
        self.label_4.setText(self.tr("Locations:"))
        self.btnRemoveAll.setToolTip(self.tr("clear list"))
        self.btnRemoveAll.setText(self.tr(" &Clear"))
        self.btnMoveDown.setToolTip(self.tr("move down"))
        self.btnMoveDown.setText(self.tr(" Do&wn"))
        self.btnRemove.setToolTip(self.tr("remove TM"))
        self.btnRemove.setText(self.tr(" De&lete"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&File"))
        self.label.setText(self.tr("Show Columns:"))
        self.chbtotal.setText(self.tr("Total"))
        self.chbtranslator.setText(self.tr("Last Translator"))
        self.chbuntranslated.setText(self.tr("Untranslated"))
        self.chbfuzzy.setText(self.tr("Fuzzy"))
        self.chbname.setText(self.tr("Name"))
        self.chblastrevision.setText(self.tr("Last Revision"))
        self.chbSVN.setText(self.tr("CVS/SVN Status"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), self.tr("Catalog &View"))
        self.btnOk.setText(self.tr("&OK"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    catalogSetting = QtGui.QWidget()
    ui = Ui_catalogSetting()
    ui.setupUi(catalogSetting)
    catalogSetting.show()
    sys.exit(app.exec_())
