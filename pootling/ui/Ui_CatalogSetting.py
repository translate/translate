# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Jul 27 14:08:44 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_catalogSetting(object):
    def setupUi(self, catalogSetting):
        catalogSetting.setObjectName("catalogSetting")
        catalogSetting.resize(QtCore.QSize(QtCore.QRect(0,0,406,309).size()).expandedTo(catalogSetting.minimumSizeHint()))

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

        self.listWidget = QtGui.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,6,1)

        self.chbDiveIntoSubfolders = QtGui.QCheckBox(self.tab)
        self.chbDiveIntoSubfolders.setObjectName("chbDiveIntoSubfolders")
        self.gridlayout1.addWidget(self.chbDiveIntoSubfolders,7,0,1,1)

        self.label_4 = QtGui.QLabel(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,0,0,1,1)

        self.btnAdd = QtGui.QPushButton(self.tab)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,1,1,1)

        self.btnDelete = QtGui.QPushButton(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDelete.sizePolicy().hasHeightForWidth())
        self.btnDelete.setSizePolicy(sizePolicy)
        self.btnDelete.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnDelete.setObjectName("btnDelete")
        self.gridlayout1.addWidget(self.btnDelete,2,1,1,1)

        self.btnClear = QtGui.QPushButton(self.tab)
        self.btnClear.setIcon(QtGui.QIcon("../images/eraser.png"))
        self.btnClear.setObjectName("btnClear")
        self.gridlayout1.addWidget(self.btnClear,3,1,1,1)

        self.btnMoveUp = QtGui.QPushButton(self.tab)
        self.btnMoveUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.gridlayout1.addWidget(self.btnMoveUp,4,1,1,1)

        self.btnMoveDown = QtGui.QPushButton(self.tab)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnMoveDown.sizePolicy().hasHeightForWidth())
        self.btnMoveDown.setSizePolicy(sizePolicy)
        self.btnMoveDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.gridlayout1.addWidget(self.btnMoveDown,5,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,31,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,6,1,2,1)
        self.tabOptions.addTab(self.tab, "")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_3)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,2,0,1,1)

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
        self.gridlayout3.addWidget(self.chbtotal,1,1,1,1)

        self.chbtranslated = QtGui.QCheckBox(self.frame)
        self.chbtranslated.setChecked(True)
        self.chbtranslated.setObjectName("chbtranslated")
        self.gridlayout3.addWidget(self.chbtranslated,1,0,1,1)

        self.chbfuzzy = QtGui.QCheckBox(self.frame)
        self.chbfuzzy.setChecked(True)
        self.chbfuzzy.setObjectName("chbfuzzy")
        self.gridlayout3.addWidget(self.chbfuzzy,2,0,1,1)

        self.chbuntranslated = QtGui.QCheckBox(self.frame)
        self.chbuntranslated.setChecked(True)
        self.chbuntranslated.setObjectName("chbuntranslated")
        self.gridlayout3.addWidget(self.chbuntranslated,0,1,1,1)

        self.chbSVN = QtGui.QCheckBox(self.frame)
        self.chbSVN.setChecked(True)
        self.chbSVN.setObjectName("chbSVN")
        self.gridlayout3.addWidget(self.chbSVN,2,1,1,1)

        self.chblastrevision = QtGui.QCheckBox(self.frame)
        self.chblastrevision.setChecked(True)
        self.chblastrevision.setObjectName("chblastrevision")
        self.gridlayout3.addWidget(self.chblastrevision,0,2,1,1)

        self.chbtranslator = QtGui.QCheckBox(self.frame)
        self.chbtranslator.setChecked(True)
        self.chbtranslator.setObjectName("chbtranslator")
        self.gridlayout3.addWidget(self.chbtranslator,1,2,1,1)

        self.chbname = QtGui.QCheckBox(self.frame)
        self.chbname.setChecked(True)
        self.chbname.setObjectName("chbname")
        self.gridlayout3.addWidget(self.chbname,0,0,1,1)
        self.gridlayout2.addWidget(self.frame,1,0,1,1)

        self.label = QtGui.QLabel(self.tab_3)
        self.label.setObjectName("label")
        self.gridlayout2.addWidget(self.label,0,0,1,1)
        self.tabOptions.addTab(self.tab_3, "")
        self.gridlayout.addWidget(self.tabOptions,0,0,1,2)

        self.btnOk = QtGui.QPushButton(catalogSetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,1,1,1)

        spacerItem2 = QtGui.QSpacerItem(191,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2,1,0,1,1)

        self.retranslateUi(catalogSetting)
        self.tabOptions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(catalogSetting)
        catalogSetting.setTabOrder(self.tabOptions,self.listWidget)
        catalogSetting.setTabOrder(self.listWidget,self.btnAdd)
        catalogSetting.setTabOrder(self.btnAdd,self.btnDelete)
        catalogSetting.setTabOrder(self.btnDelete,self.btnClear)
        catalogSetting.setTabOrder(self.btnClear,self.btnMoveUp)
        catalogSetting.setTabOrder(self.btnMoveUp,self.btnMoveDown)
        catalogSetting.setTabOrder(self.btnMoveDown,self.chbDiveIntoSubfolders)
        catalogSetting.setTabOrder(self.chbDiveIntoSubfolders,self.chbname)
        catalogSetting.setTabOrder(self.chbname,self.chbtranslated)
        catalogSetting.setTabOrder(self.chbtranslated,self.chbfuzzy)
        catalogSetting.setTabOrder(self.chbfuzzy,self.chbuntranslated)
        catalogSetting.setTabOrder(self.chbuntranslated,self.chbtotal)
        catalogSetting.setTabOrder(self.chbtotal,self.chbSVN)
        catalogSetting.setTabOrder(self.chbSVN,self.chblastrevision)
        catalogSetting.setTabOrder(self.chblastrevision,self.chbtranslator)
        catalogSetting.setTabOrder(self.chbtranslator,self.btnOk)

    def tr(self, string):
        return QtGui.QApplication.translate("catalogSetting", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, catalogSetting):
        catalogSetting.setWindowTitle(self.tr("Catalog Settings"))
        self.tabOptions.setWhatsThis(self.tr("​"))
        self.listWidget.setToolTip(self.tr("Listwidget"))
        self.listWidget.setWhatsThis(self.tr("<h3>Listwidget</h3>Listwidget is displayed items from user add files or folders."))
        self.chbDiveIntoSubfolders.setToolTip(self.tr("Dive into subfolders"))
        self.chbDiveIntoSubfolders.setWhatsThis(self.tr("<h3>Dive into subfolders</h3>Use this to checked/unchecked to display sub\'s file under main folder."))
        self.chbDiveIntoSubfolders.setText(self.tr("Dive into subfolders"))
        self.label_4.setText(self.tr("Locations:"))
        self.btnAdd.setToolTip(self.tr("Add TM"))
        self.btnAdd.setWhatsThis(self.tr("<h3>Add TM</h3>Use this to add po, xliff files or another folders of file on your local into listwidget."))
        self.btnAdd.setText(self.tr(" &Add"))
        self.btnDelete.setToolTip(self.tr("Delete TM"))
        self.btnDelete.setWhatsThis(self.tr("<h3>Delete TM</h3>Use this to delete po, xliff files or another folders of files from listwidget."))
        self.btnDelete.setText(self.tr(" De&lete"))
        self.btnClear.setToolTip(self.tr("Clear List"))
        self.btnClear.setWhatsThis(self.tr("<h3>Clear List</h3>Use this to clear everything in listwidget ."))
        self.btnClear.setText(self.tr(" &Clear"))
        self.btnMoveUp.setToolTip(self.tr("Move Up"))
        self.btnMoveUp.setWhatsThis(self.tr("<h3>Move Up</h3>Use this to move iterm in listwidget from up to down "))
        self.btnMoveUp.setText(self.tr(" &Up"))
        self.btnMoveDown.setToolTip(self.tr("Move Down"))
        self.btnMoveDown.setWhatsThis(self.tr("<h3>Move Down</h3>Use this to move iterm in listwidget from down to up ."))
        self.btnMoveDown.setText(self.tr(" Do&wn"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab), self.tr("&File"))
        self.chbtotal.setToolTip(self.tr("Total"))
        self.chbtotal.setWhatsThis(self.tr("<h3>Total</h3>Use this to checked/unchecked to display total number of strings in file on the catalog manager."))
        self.chbtotal.setText(self.tr("Total"))
        self.chbtranslated.setToolTip(self.tr("Translated"))
        self.chbtranslated.setWhatsThis(self.tr("<h3>Translated</h3>Use this to checked/unchecked to display number of string in file was translated on the catalog manager."))
        self.chbtranslated.setText(self.tr("Translated"))
        self.chbfuzzy.setToolTip(self.tr("Fuzzy"))
        self.chbfuzzy.setWhatsThis(self.tr("<h3>Fuzzy</h3>Use this to checked/unchecked to display fuzzy number in file on the catalog manager."))
        self.chbfuzzy.setText(self.tr("Fuzzy"))
        self.chbuntranslated.setToolTip(self.tr("Untranslated"))
        self.chbuntranslated.setWhatsThis(self.tr("<h3>Untranslated</h3>Use this to checked/unchecked to display number of string in file was untranslated on the catalog manager."))
        self.chbuntranslated.setText(self.tr("Untranslated"))
        self.chbSVN.setToolTip(self.tr("CVS/SVN Status"))
        self.chbSVN.setWhatsThis(self.tr("<h3>CVS/SVN Status</h3>Use this to checked/unchecked to display status of file in local or cvs/svn server on the catalog manager."))
        self.chbSVN.setText(self.tr("CVS/SVN Status"))
        self.chblastrevision.setToolTip(self.tr("Last Revision"))
        self.chblastrevision.setWhatsThis(self.tr("<h3>Last Revision</h3>Use this to checked/unchecked to display date/time in file was saved by the last translator on the catalog manager."))
        self.chblastrevision.setText(self.tr("Last Revision"))
        self.chbtranslator.setToolTip(self.tr("Last Translator"))
        self.chbtranslator.setWhatsThis(self.tr("<h3>Last Translator</h3>Use this to checked/unchecked to display last translator\'s name in file on the catalog manager."))
        self.chbtranslator.setText(self.tr("Last Translator"))
        self.chbname.setToolTip(self.tr("Name"))
        self.chbname.setWhatsThis(self.tr("<h3>Name</h3>Use this to checked/unchecked to display file name on the catalog manager."))
        self.chbname.setText(self.tr("Name"))
        self.label.setText(self.tr("Show Columns:"))
        self.tabOptions.setTabText(self.tabOptions.indexOf(self.tab_3), self.tr("Catalog &View"))
        self.btnOk.setText(self.tr("&OK"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    catalogSetting = QtGui.QWidget()
    ui = Ui_catalogSetting()
    ui.setupUi(catalogSetting)
    catalogSetting.show()
    sys.exit(app.exec_())
