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
#       Hok Kakada (hokkakada@khmeros.info)
#
# This module is working on any comments of current TU.

import sys
from PyQt4 import QtCore, QtGui
from CommentUI import Ui_frmComment

class CommentDock(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Comment"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_frmComment()
        self.ui.setupUi(self.form)        
        self.setWidget(self.form)
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowComment")
        self._actionShow.setText(self.tr("Hide Comment"))    
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)           
        
    def closeEvent(self, event):            
        self._actionShow.setText(self.tr("Show Comment"))
        
    def actionShow(self):
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Comment"))    
        else:
            self._actionShow.setText(self.tr("Show Comment"))    
        self.setHidden(not self.isHidden()) 
 
    def updateComment(self, currentUnit):
        comment = currentUnit.getnotes()
        self.ui.txtComment.setPlainText(comment)
    
    def checkModified(self):
        if self.ui.txtComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), self.ui.txtComment.toPlainText())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock()
    comment.show()
    sys.exit(app.exec_())
