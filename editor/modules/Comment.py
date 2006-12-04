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
import modules.World as World

class CommentDock(QtGui.QDockWidget):
    """
    Code for Comment View
    
    @signal commentChanged(): emitted when Comment view's document is modified.
    @signal readyForSave(True): emitted when Comment view's text is changed.
    @signal copyAvailable(bool): emitted when text is selected or de-selected in the Comment view.
    """
    
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("commentDock")
        self.setWindowTitle(self.tr("Comment"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_frmComment()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.layout = QtGui.QTextLayout()
        self.applySettings()

        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("textChanged()"), self.setReadyForSave)
        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("copyAvailable(bool)"), self.copyAvailable)
        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("undoAvailable(bool)"), self.undoAvailable)
        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("redoAvailable(bool)"), self.redoAvailable)

        # create highlight font
        self.highlightFormat = QtGui.QTextCharFormat()
        self.highlightFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightFormat.setForeground(QtCore.Qt.white)
        self.highlightFormat.setBackground(QtCore.Qt.darkMagenta)
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.highlightFormat

    def closeEvent(self, event):
        """
        set text of action object to 'show Comment' before closing Comment View
        @param QCloseEvent Object: received close event when closing widget
        """        
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)

    def updateView(self, currentUnit):
        if (currentUnit):
            comment = currentUnit.getnotes()
            self.ui.txtTranslatorComment.setPlainText(unicode(comment))
            self.ui.txtTranslatorComment.setEnabled(True)
        else:
            self.ui.txtTranslatorComment.clear()
            self.ui.txtTranslatorComment.setEnabled(False)
            
    def checkModified(self):
        if self.ui.txtTranslatorComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), self.ui.txtTranslatorComment.toPlainText())

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        if (textField != World.comment):
            return
        textField = self.ui.txtTranslatorComment
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
        """ set color and font to txtTranslatorComment"""
        commentColor = World.settings.value("commentColor")
        if (commentColor.isValid()):
            colorObj = QtGui.QColor(commentColor.toString())
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtTranslatorComment.setPalette(palette)
            
        font = World.settings.value("commentFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.txtTranslatorComment.setFont(fontObj)

    def copyAvailable(self, bool):
        self.emit(QtCore.SIGNAL("copyAvailable(bool)"), bool)
        
    def undoAvailable(self, bool):
        self.emit(QtCore.SIGNAL("undoAvailable(bool)"), bool)

    def redoAvailable(self, bool):
        self.emit(QtCore.SIGNAL("redoAvailable(bool)"), bool)
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock()
    comment.show()
    sys.exit(app.exec_())
