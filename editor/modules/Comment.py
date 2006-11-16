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
#       Keo Sophon (keosophon@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on any comments of current TU.

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_Comment import Ui_frmComment
from modules.World import World

class CommentDock(QtGui.QDockWidget):
    # FIXME: comment this list the signals
    
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Comment"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_frmComment()
        self.ui.setupUi(self.form)        
        self.setWidget(self.form)
        self.layout = QtGui.QTextLayout ()
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)
        self.applySettings()

        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowComment")
        self._actionShow.setText(self.tr("Hide Comment"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)
        self.connect(self.ui.txtComment, QtCore.SIGNAL("textChanged ()"), self.setReadyForSave)
        self.connect(self.ui.txtComment, QtCore.SIGNAL("copyAvailable(bool)"), self._copyAvailable)

        # create highlight font
        self.highlightFormat = QtGui.QTextCharFormat()
        self.highlightFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightFormat.setForeground(QtCore.Qt.white)
        self.highlightFormat.setBackground(QtCore.Qt.darkMagenta)
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.highlightFormat

    def closeEvent(self, event):
        # FIXME: comment this
        self._actionShow.setText(self.tr("Show Comment"))
        # FIXME: you need to call the parents implementation here. Jens

    def actionShow(self):
        # FIXME: comment this there is a return value
        return self._actionShow

    def show(self):
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Comment"))
        else:
            self._actionShow.setText(self.tr("Show Comment"))
        self.setHidden(not self.isHidden())

    def updateView(self, currentUnit):
        if (currentUnit):
            comment = currentUnit.getnotes()
        else:
            comment = ""

        self.ui.txtComment.setPlainText(unicode(comment))
    
    def checkModified(self):
        if self.ui.txtComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), self.ui.txtComment.toPlainText())

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        if (textField != self.world.comment):
            return
        textField = self.ui.txtComment
        if (position >= 0):
            block = textField.document().findBlock(position)
            self.highlightRange.start = position
            self.highlightRange.length = length
        else:
            block = textField.document().begin()
            self.highlightRange.length = 0
            self.layout.clearAdditionalFormats()
            textField.update()
        block.layout().setAdditionalFormats([self.highlightRange])

    def setReadyForSave(self):
      self.emit(QtCore.SIGNAL("readyForSave"), True)

    def applySettings(self):
        font = self.settings.value("commentFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.txtComment.setFont(fontObj)

    def _copyAvailable(self, bool):
        self.emit(QtCore.SIGNAL("copyAvailable(bool)"), bool)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock()
    comment.show()
    sys.exit(app.exec_())
