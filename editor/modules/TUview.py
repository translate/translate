#!/usr/bin/python
# -*- coding: utf8 -*-

# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
# This program is free sofware; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on source and target of current TU.

if __name__ == "__main__":
    import sys
    import os.path
    sys.path.append(os.path.join(sys.path[0], ".."))

import sys
from PyQt4 import QtCore, QtGui
if __name__ == "__main__":
    import os.path
    sys.path.append(os.path.join(sys.path[0], ".."))
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))

from ui.Ui_TUview import Ui_TUview
from modules import World

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
        self.ui.txtTarget.setWhatsThis("Translation Editor\n\nThis editor displays and lets you edit the trasnslation of the currently displayed message")
        self.ui.txtSource.setWhatsThis("Original String\n\nThis part of the window shows you the original message of the currently displayed entry.")
        self.ui.txtComment.setWhatsThis("Important Comment\n\nThis part is very useful for translator during translation. Hints from the developer are contained in this area. This area will be hidden if there is no hints. ")
        self.applySettings()
        
        self.indexToUpdate = None
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.setReadyForSave)
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
        
    def setColor(self):
        """set color to txtSource and txtTarget"""
        color = QtGui.QColorDialog.getColor(QtCore.Qt.red, self)
        if color.isValid():
            self.ui.txtSource.setTextColor(color)
            self.ui.txtTarget.setTextColor(color)
    
    def setScrollbarMaximum(self):
        """Set scrollbar maximum value according to number of index."""
        maximum = max(len(self.indexes) - 1, 0)
        self.ui.fileScrollBar.setMaximum(maximum)
        
    def slotNewUnits(self, units):
        """slot after new file was loaded
        @param units: a list of translation units objects of an opened file
        """
        self.ui.txtSource.setEnabled(True)
        self.ui.txtTarget.setEnabled(True)
        if not units:
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
        # self.indexes store the information of unit's index
        self.indexes = range(len(units))
        self.filter = World.filterAll
        # adjust the scrollbar
        self.setScrollbarMaximum()
        self.ui.fileScrollBar.setEnabled(True)
        self.ui.fileScrollBar.setSliderPosition(0)
    
    def filteredList(self, fList, filter):
        """Adjust the scrollbar maximum according to length of filtered list.
        @param fList: Index list of units visible in the table after filtered
        @param filter: helper constants for filtering
        """
        self.indexes = fList
        self.filter = filter
        self.setScrollbarMaximum()
        self.ui.fileScrollBar.setValue(0)

    @QtCore.pyqtSignature("int")
    def emitCurrentIndex(self, value):
        """emit "currentIndex" signal with current index value.
        @param index: current index in the units."""
        # send the signal only index is new
        if (self.indexToUpdate != value):
            if (self.indexes) and (value < len(self.indexes)):
                index = self.indexes[value]
                self.emit(QtCore.SIGNAL("currentIndex"), index)
    
    def updateView(self, unit, index, state):
        """Update the text in source and target, set the scrollbar position,
        remove a value from scrollbar if the unit is not in filter.
        Then recalculate scrollbar maximum value.
        @param unit: unit to set in target and source.
        @param index: value in the scrollbar to be removed.
        @param state: state of unit defined in world.py."""
        try:
            value = self.indexes.index(index)
        except:
            return
        if (unit):
            self.ui.txtSource.setPlainText(unit.source)
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
            self.ui.txtTarget.setPlainText(unit.target)
            self.ui.txtTarget.setFocus
        if not (self.filter & state):
            try:
                self.indexes.remove(index)
            except:
                pass
            self.setScrollbarMaximum()
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
        # set the scrollbar position
        self.indexToUpdate = value
        self.ui.fileScrollBar.setValue(value)

    def setTarget(self, text):
        """Change the target text.
        @param text: text to set into target field."""
        self.ui.txtTarget.setPlainText(text)

    def checkModified(self):
        if self.ui.txtTarget.document().isModified():
            self.emit(QtCore.SIGNAL("targetChanged"), self.ui.txtTarget.toPlainText())
            self.ui.txtTarget.document().setModified(False)

    def setReadyForSave(self):
        self.emit(QtCore.SIGNAL("readyForSave"), True)

    def source2target(self):
        """Copy the text from source to target."""
        self.ui.txtTarget.setPlainText(self.ui.txtSource.toPlainText())
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

    def applySettings(self):
        """ set font and color to txtSource and txtTarget"""
        sourceColor = World.settings.value("tuSourceColor")
        if (sourceColor.isValid()):
            colorObj = QtGui.QColor(sourceColor.toString())
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtSource.setPalette(palette)
            
        targetColor = World.settings.value("tuTargetColor")
        if (targetColor.isValid()):
            colorObj = QtGui.QColor(targetColor.toString())
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtTarget.setPalette(palette)
            
        fontObj = QtGui.QFont()
        sourcefont = World.settings.value("tuSourceFont")
        if (sourcefont.isValid() and fontObj.fromString(sourcefont.toString())):
            self.ui.txtSource.setFont(fontObj)

        targetfont = World.settings.value("tuTargetFont")
        if (targetfont.isValid() and fontObj.fromString(targetfont.toString())):
            self.ui.txtTarget.setFont(fontObj)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = TUview(None)
    Form.show()
    sys.exit(app.exec_())
