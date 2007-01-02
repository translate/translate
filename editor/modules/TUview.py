#!/usr/bin/python
# -*- coding: utf8 -*-

# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
# This program is free sofware; you can redistribute it and/or
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
# This module is working on source and target of current TU.

from PyQt4 import QtCore, QtGui
from editor.ui.Ui_TUview import Ui_TUview
from translate.storage import po
from editor.modules import World

class TUview(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("detailDock")
        self.setWindowTitle(self.tr("Detail"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_TUview()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.ui.txtComment.hide()
        self.ui.txtTarget.setReadOnly(True)
        self.ui.txtTarget.setWhatsThis("<h3>Translated String</h3>This editor displays and lets you edit the translation of the currently displayed string.")
        self.ui.txtSource.setWhatsThis("<h3>Original String</h3>This part of the window shows you the original string of the currently displayed entry. <br>You can not edit this string.")
        self.ui.txtComment.setWhatsThis("<h3>Important Comment</h3>Hints from the developer to the translator are displayed in this area. This area will be hidden if there is no hint. ")
        self.ui.fileScrollBar.setWhatsThis("<h3>Navigation Scrollbar</h3>It allows you do navigate in the current file. If you filter your strings you get only the filtered list. <br>It also gives you visual feedback about the postion of the current entry. The Tooltip also shows you the current number and the total numbers of strings.")
        self.applySettings()
        
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        
        # create highlight font
        self.highlightFormat = QtGui.QTextCharFormat()
        self.highlightFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightFormat.setForeground(QtCore.Qt.white)
        self.highlightFormat.setBackground(QtCore.Qt.darkMagenta)
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.highlightFormat
        
    def closeEvent(self, event):
        """
        set text of action object to 'show Detail' before closing TUview
        @param QCloseEvent Object: received close event when closing widget
        """        
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
        
    def setScrollbarMaxValue(self, value):
        """Set scrollbar maximum value according to number of index."""
        self.ui.fileScrollBar.setMaximum(max(value - 1, 0))

    def setScrollbarValue(self, value):
        """@param value: the new value for the scrollbar"""
        if (value < 0):
            value = 0
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setValue(value)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setToolTip("%s / %s" % (value + 1,  self.ui.fileScrollBar.maximum() + 1))

    def filterChanged(self, filter, lenFilter):
        """Adjust the scrollbar maximum according to lenFilter.
        @param filter: helper constants for filtering
        @param lenFilter: len of filtered items."""
        if (lenFilter):
            self.ui.fileScrollBar.setEnabled(True)
            self.ui.txtSource.setEnabled(True)
            self.ui.txtTarget.setEnabled(True)
        else:
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
            self.ui.txtSource.setEnabled(False)
            self.ui.txtTarget.setEnabled(False)
        self.filter = filter
        self.setScrollbarMaxValue(lenFilter)
    
    @QtCore.pyqtSignature("int")
    def emitCurrentIndex(self, value):
        """emit "currentIndex" signal with current index value.
        @param index: current index in the units."""
        self.emit(QtCore.SIGNAL("filteredIndex"), value)
    
    def updateView(self, unit):
        """Update the text in source and target, set the scrollbar position,
        remove a value from scrollbar if the unit is not in filter.
        Then recalculate scrollbar maximum value.
        @param unit: unit to set in target and source.
        @param index: value in the scrollbar to be removed."""
        if (not unit) or (not hasattr(unit, "x_editor_filterIndex")):
            self.ui.txtComment.hide()
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
            self.ui.txtSource.setEnabled(False)
            self.ui.txtTarget.setEnabled(False)
            return
        self.ui.txtTarget.setReadOnly(False)
        if isinstance(unit, po.pounit):
            comment = "".join([comment for comment in unit.msgidcomments])
            comment = comment.lstrip('"_:')
            comment = comment.rstrip('"')
            comment= comment.rstrip('\\n')
            comment += unit.getnotes("developer")
            if (comment == ""):
                self.ui.txtComment.hide()
            else:
                self.ui.txtComment.show()
                self.ui.txtComment.setPlainText(unicode(comment))
        self.ui.txtSource.setPlainText(unit.source)
        self.ui.txtTarget.setPlainText(unit.target)
        self.ui.txtTarget.setFocus
        # set the scrollbar position
        self.setScrollbarValue(unit.x_editor_filterIndex)
    
    def checkModified(self):
        if self.ui.txtTarget.document().isModified():
            self.emit(QtCore.SIGNAL("targetChanged"), self.ui.txtTarget.toPlainText())
            self.ui.txtTarget.document().setModified(False)

    def emitReadyForSave(self):
        self.emit(QtCore.SIGNAL("readyForSave"), True)

    def source2target(self):
        """Copy the text from source to target."""
        self.ui.txtTarget.selectAll()
        self.ui.txtTarget.insertPlainText(self.ui.txtSource.toPlainText())
        self.ui.txtTarget.document().setModified()

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        if ((textField != World.source and textField != World.target)  or position == None):
            if (not getattr(self, "highlightBlock", None)):
                return
            self.highlightRange.length = 0
        else:
            if (textField == World.source):
                textField = self.ui.txtSource
            else:
                textField = self.ui.txtTarget
            self.highlightBlock = textField.document().findBlock(position)
            self.highlightRange.start = position - self.highlightBlock.position()
            self.highlightRange.length = length
        self.highlightBlock.layout().setAdditionalFormats([self.highlightRange])
        self.highlightBlock.document().markContentsDirty(self.highlightBlock.position(), self.highlightBlock.length())

    def replaceText(self, textField, position, length, replacedText):
        """replace the string (at position and length) with replacedText in txtTarget.
        @param textField: source or target text box.
        @param position: old string's start point.
        @param length: old string's length.
        @param replacedText: string to replace."""
        if (textField != World.target):
            return
        text = self.ui.txtTarget.toPlainText()
        text.replace(position, length, replacedText);
        self.ui.txtTarget.setPlainText(text)
        self.ui.txtTarget.document().setModified()
        self.checkModified()

    def applySettings(self):
        """ set font and color to txtSource and txtTarget"""
        sourceColor = World.settings.value("tuSourceColor")
        if (sourceColor.isValid()):
            colorObj = QtGui.QColor(sourceColor.toString())
            palette = QtGui.QPalette(self.ui.txtSource.palette())
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtSource.setPalette(palette)

        targetColor = World.settings.value("tuTargetColor")
        if (targetColor.isValid()):
            colorObj = QtGui.QColor(targetColor.toString())
            palette = QtGui.QPalette(self.ui.txtTarget.palette())
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtTarget.setPalette(palette)

        fontObj = QtGui.QFont()
        sourcefont = World.settings.value("tuSourceFont")
        if (sourcefont.isValid() and fontObj.fromString(sourcefont.toString())):
            self.ui.txtSource.setFont(fontObj)

        targetfont = World.settings.value("tuTargetFont")
        if (targetfont.isValid() and fontObj.fromString(targetfont.toString())):
            self.ui.txtTarget.setFont(fontObj)
        
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    Form = TUview(None)
    Form.show()
    sys.exit(app.exec_())
