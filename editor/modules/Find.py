#!/usr/bin/python
# -*- coding: utf8 -*-
#WordForge Translation Editor
# (c) 2006 Open Forum of Cambodia, all rights reserved.
#
# Version 1.0
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details.
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)
#
# This module is working on source and target of current TU.

import sys
from PyQt4 import QtCore, QtGui
from FindUI import Ui_Form

class Find(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)        
        self.form = QtGui.QWidget(self)             
        self.ui = Ui_Form()
        self.ui.setupUi(self.form)  
        self.setWidget(self.form)        
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowOverview")
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)

    def actionShow(self):  
        return self._actionShow
        
    def show(self):
        self.setHidden(not self.isHidden())              
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = Find()
    Form.show()
    sys.exit(app.exec_())
