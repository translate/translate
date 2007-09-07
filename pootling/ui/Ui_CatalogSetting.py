# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Fri Sep  7 17:00:15 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_catalogSetting(object):
    def setupUi(self, catalogSetting):
        catalogSetting.setObjectName("catalogSetting")
        catalogSetting.resize(QtCore.QSize(QtCore.QRect(0,0,359,250).size()).expandedTo(catalogSetting.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(catalogSetting)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.frame = QtGui.QFrame(catalogSetting)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,3,1,1,1)

        self.chbSVN = QtGui.QCheckBox(self.frame)
        self.chbSVN.setChecked(True)
        self.chbSVN.setObjectName("chbSVN")
        self.gridlayout1.addWidget(self.chbSVN,2,1,1,1)

        self.chbname = QtGui.QCheckBox(self.frame)
        self.chbname.setChecked(True)
        self.chbname.setObjectName("chbname")
        self.gridlayout1.addWidget(self.chbname,0,0,1,1)

        self.chbtranslator = QtGui.QCheckBox(self.frame)
        self.chbtranslator.setChecked(True)
        self.chbtranslator.setObjectName("chbtranslator")
        self.gridlayout1.addWidget(self.chbtranslator,1,2,1,1)

        self.chblastrevision = QtGui.QCheckBox(self.frame)
        self.chblastrevision.setChecked(True)
        self.chblastrevision.setObjectName("chblastrevision")
        self.gridlayout1.addWidget(self.chblastrevision,0,2,1,1)

        self.chbuntranslated = QtGui.QCheckBox(self.frame)
        self.chbuntranslated.setChecked(True)
        self.chbuntranslated.setObjectName("chbuntranslated")
        self.gridlayout1.addWidget(self.chbuntranslated,0,1,1,1)

        self.chbfuzzy = QtGui.QCheckBox(self.frame)
        self.chbfuzzy.setChecked(True)
        self.chbfuzzy.setObjectName("chbfuzzy")
        self.gridlayout1.addWidget(self.chbfuzzy,2,0,1,1)

        self.chbtranslated = QtGui.QCheckBox(self.frame)
        self.chbtranslated.setChecked(True)
        self.chbtranslated.setObjectName("chbtranslated")
        self.gridlayout1.addWidget(self.chbtranslated,1,0,1,1)

        self.chbtotal = QtGui.QCheckBox(self.frame)
        self.chbtotal.setChecked(True)
        self.chbtotal.setObjectName("chbtotal")
        self.gridlayout1.addWidget(self.chbtotal,1,1,1,1)
        self.gridlayout.addWidget(self.frame,1,0,1,2)

        spacerItem1 = QtGui.QSpacerItem(191,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1,2,0,1,1)

        self.label = QtGui.QLabel(catalogSetting)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,2)

        self.btnOk = QtGui.QPushButton(catalogSetting)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,2,1,1,1)

        self.retranslateUi(catalogSetting)
        QtCore.QMetaObject.connectSlotsByName(catalogSetting)
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
        self.chbSVN.setToolTip(self.tr("CVS/SVN Status"))
        self.chbSVN.setWhatsThis(self.tr("<h3>CVS/SVN Status</h3>Use this to checked/unchecked to display status of file in local or cvs/svn server on the catalog manager."))
        self.chbSVN.setText(self.tr("CVS/SVN Status"))
        self.chbname.setToolTip(self.tr("Name"))
        self.chbname.setWhatsThis(self.tr("<h3>Name</h3>Use this to checked/unchecked to display file name on the catalog manager."))
        self.chbname.setText(self.tr("Name"))
        self.chbtranslator.setToolTip(self.tr("Last Translator"))
        self.chbtranslator.setWhatsThis(self.tr("<h3>Last Translator</h3>Use this to checked/unchecked to display last translator\'s name in file on the catalog manager."))
        self.chbtranslator.setText(self.tr("Last Translator"))
        self.chblastrevision.setToolTip(self.tr("Last Revision"))
        self.chblastrevision.setWhatsThis(self.tr("<h3>Last Revision</h3>Use this to checked/unchecked to display date/time in file was saved by the last translator on the catalog manager."))
        self.chblastrevision.setText(self.tr("Last Revision"))
        self.chbuntranslated.setToolTip(self.tr("Untranslated"))
        self.chbuntranslated.setWhatsThis(self.tr("<h3>Untranslated</h3>Use this to checked/unchecked to display number of string in file was untranslated on the catalog manager."))
        self.chbuntranslated.setText(self.tr("Untranslated"))
        self.chbfuzzy.setToolTip(self.tr("Fuzzy"))
        self.chbfuzzy.setWhatsThis(self.tr("<h3>Fuzzy</h3>Use this to checked/unchecked to display fuzzy number in file on the catalog manager."))
        self.chbfuzzy.setText(self.tr("Fuzzy"))
        self.chbtranslated.setToolTip(self.tr("Translated"))
        self.chbtranslated.setWhatsThis(self.tr("<h3>Translated</h3>Use this to checked/unchecked to display number of string in file was translated on the catalog manager."))
        self.chbtranslated.setText(self.tr("Translated"))
        self.chbtotal.setToolTip(self.tr("Total"))
        self.chbtotal.setWhatsThis(self.tr("<h3>Total</h3>Use this to checked/unchecked to display total number of strings in file on the catalog manager."))
        self.chbtotal.setText(self.tr("Total"))
        self.label.setText(self.tr("Show Columns:"))
        self.btnOk.setText(self.tr("&OK"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    catalogSetting = QtGui.QWidget()
    ui = Ui_catalogSetting()
    ui.setupUi(catalogSetting)
    catalogSetting.show()
    sys.exit(app.exec_())
