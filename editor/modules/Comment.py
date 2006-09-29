#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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
        self.layout = QtGui.QTextLayout ()
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowComment")
        self._actionShow.setText(self.tr("Hide Comment"))    
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)
        self.connect(self.ui.txtComment, QtCore.SIGNAL("textChanged ()"), self.setReadyForSave)

        
    def closeEvent(self, event):            
        self._actionShow.setText(self.tr("Show Comment"))
        # FIXME you need to call the parents implementation here. Jens
        
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
        self.ui.txtComment.setPlainText(unicode(comment))
    
    def checkModified(self):
        if self.ui.txtComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), self.ui.txtComment.toPlainText())

    def getCommentToHighLight(self):                        
        self.emit(QtCore.SIGNAL("highLight"), self.ui.txtComment.document())
  
    def setHighLightComment(self, location):
        '''HighLight on comment depending on location (offset, and length)'''             
        offsetindoc = location[0]
        length = location[1]
        overrides = []        
        charformat = QtGui.QTextCharFormat()
        charformat.setFontWeight(QtGui.QFont.Bold)
        charformat.setForeground(QtCore.Qt.darkMagenta)        
        block = self.ui.txtComment.document().findBlock(offsetindoc)        
        offsetinblock = offsetindoc - block.position()
        range = QtGui.QTextLayout.FormatRange()
        range.start = offsetinblock
        range.length = length
        range.format = charformat
        self.layout = block.layout()
        text = block.text()
        overrides.append(range)
        self.layout.setAdditionalFormats(overrides)
        block.document().markContentsDirty(block.position(), block.length())

    def clearHighLight(self):
        try:
            self.layout. clearAdditionalFormats()
        except:
            pass
            
    def setReadyForSave(self):
      self.emit(QtCore.SIGNAL("readyForSave"), True)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock()
    comment.show()
    sys.exit(app.exec_())
