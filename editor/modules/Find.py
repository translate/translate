#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
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
