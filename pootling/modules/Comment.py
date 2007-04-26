#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on any comments of current TU.

from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_Comment import Ui_frmComment
import pootling.modules.World as World
from translate.storage import po
from translate.storage import xliff
from pootling.modules import highlighter

class CommentDock(QtGui.QDockWidget):
    """
    Code for Comment View
    
    @signal commentChanged(): emitted when Comment view's document is modified.
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
        self.ui.txtLocationComment.hide()
        # create highlighter
        self.highlighter = highlighter.Highlighter(None)
        self.applySettings()
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Comment' before closing Comment View
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)

    def updateView(self, unit):
        """Update the comments view
        @param unit: class unit."""
        self.disconnect(self.ui.txtTranslatorComment, QtCore.SIGNAL("textChanged()"), self.checkModified)
        self.viewSetting(unit)
        if (not unit):
            return
        translatorComment = ""
        locationComment = ""
        translatorComment = unit.getnotes("translator")
        locationComments = unit.getlocations()
        locationComment = "\n".join([location for location in locationComments])
        if (locationComment == ""):
            self.ui.txtLocationComment.hide()
        else:
            self.ui.txtLocationComment.show()
            self.ui.txtLocationComment.setPlainText(locationComment)
        if (unicode(self.ui.txtTranslatorComment.toPlainText()) != unicode(translatorComment)):
            self.ui.txtTranslatorComment.setPlainText(translatorComment)
        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("textChanged()"), self.checkModified)

    def checkModified(self):
        if self.ui.txtTranslatorComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), unicode(self.ui.txtTranslatorComment.toPlainText()))
            self.ui.txtTranslatorComment.document().setModified(False)

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        
        if ((textField == World.comment) and position != None):
            textField = self.ui.txtTranslatorComment
            block = textField.document().findBlock(position)
            self.highlighter.clearSearchFormats()
            self.highlighter.setHighLight(block, position - block.position(), length, World.searchFormat)
        else:
            self.highlighter.clearSearchFormats()

    def applySettings(self):
        """ set color and font to txtTranslatorComment"""
        commentColor = World.settings.value("commentColor")
        if (commentColor.isValid()):
            colorObj = QtGui.QColor(commentColor.toString())
            palette = QtGui.QPalette(self.ui.txtTranslatorComment.palette())
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            if (self.ui.txtTranslatorComment.isEnabled()):
                self.ui.txtTranslatorComment.setPalette(palette)
            else:
                # we need to enable the widget otherwise it will not use the new palette
                self.ui.txtTranslatorComment.setEnabled(True)
                self.ui.txtTranslatorComment.setPalette(palette)
                self.ui.txtTranslatorComment.setEnabled(False)

        font = World.settings.value("commentFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.txtTranslatorComment.setFont(fontObj)
                
    def replaceText(self, textField, position, length, replacedText):
        """replace the string (at position and length) with replacedText in txtTarget.
        @param textField: source or target text box.
        @param position: old string's start point.
        @param length: old string's length.
        @param replacedText: string to replace."""
        if (textField != World.comment):
            return
        text = self.ui.txtTranslatorComment.toPlainText()
        text.replace(position, length, replacedText)
        self.ui.txtTranslatorComment.setPlainText(text)
        self.ui.txtTranslatorComment.document().setModified()
        self.checkModified()
    
    def viewSetting(self, argc):
        bool = (argc and True or False)
        self.ui.txtTranslatorComment.setEnabled(bool)
        if (bool == False):
            self.ui.txtLocationComment.hide()
            self.ui.txtTranslatorComment.clear()
            return

if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock(None)
    comment.show()
    sys.exit(app.exec_())
