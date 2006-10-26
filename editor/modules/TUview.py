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

import sys
from PyQt4 import QtCore, QtGui
from ui.TUviewUI import Ui_TUview

class TUview(QtGui.QDockWidget):
    def __init__(self):
        QtGui.QDockWidget.__init__(self)
        self.setWindowTitle(self.tr("Detail"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_TUview()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.layout = QtGui.QTextLayout ()
        self.settings = QtCore.QSettings("WordForge", "Translation Editor")
        self.applySettings()        
        
        # create action for show/hide
        self._actionShow = QtGui.QAction(self)
        self._actionShow.setObjectName("actionShowDetail")
        self._actionShow.setText(self.tr("Hide Detail"))
        self.connect(self._actionShow, QtCore.SIGNAL("triggered()"), self.show)        
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.setReadyForSave)

    def closeEvent(self, event):
        """when close button is click, change caption to "Show Detail"""
        self._actionShow.setText(self.tr("Show Detail"))
        # FIXME you need to call the parents implementation here. Jens
        
    def actionShow(self):
        return self._actionShow
        
    def show(self):
        """toggle hide/show detail caption"""
        if self.isHidden():
            self._actionShow.setText(self.tr("Hide Detail"))
        else:
            self._actionShow.setText(self.tr("Show Detail"))    
        self.setHidden(not self.isHidden())

    def setColor(self):
        """set color to txtSource and txtTarget"""
        color = QtGui.QColorDialog.getColor(QtCore.Qt.red, self)     
        if color.isValid():
            self.ui.txtSource.setTextColor(color)
            self.ui.txtTarget.setTextColor(color)
    
    @QtCore.pyqtSignature("int")
    def emitCurrentIndex(self, value):
        if (self.indexes) and (value < len(self.indexes)):
            index = self.indexes[value]
            self.emit(QtCore.SIGNAL("currentIndex"), index)

    def setScrollbarMaximum(self):
        """Set scrollbar maximum value according to number of index."""
        maximum = len(self.indexes) - 1
        if (maximum < 0):
            maximum = 0
        self.ui.fileScrollBar.setMaximum(maximum)
        
    def hideUnit(self, value):
        """Remove index from indexes, and recalculate scrollbar maximum."""
        # adjust the scrollbar
        try:
            self.indexes.remove(value)
        except ValueError:
            pass
        self.setScrollbarMaximum()
        self.ui.txtSource.setPlainText("")
        self.ui.txtTarget.setPlainText("")
        
    def slotNewUnits(self, units):
        """slot after new file was loaded"""
        if not units:
            self.ui.txtSource.setPlainText("")
            self.ui.txtTarget.setPlainText("")
        # self.indexes store the information of unit's index
        self.indexes = range(len(units))
        # adjust the scrollbar
        self.setScrollbarMaximum()
        self.ui.fileScrollBar.setEnabled(True)
        self.ui.fileScrollBar.setSliderPosition(0)
    
    def filteredList(self, fList):
        """Adjust the scrollbar maximum according to length of filtered list."""
        self.indexes = fList
        self.setScrollbarMaximum()
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setValue(0)
        self.ui.fileScrollBar.setSliderPosition(0)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
    
    def updateView(self, unit, index, state):
        """Update the text in source and target, and set the scrollbar position."""
        if (unit):
            self.ui.txtSource.setPlainText(unit.source)
            self.ui.txtTarget.setPlainText(unit.target)
        else:
            self.ui.txtSource.setPlainText("")
            self.ui.txtTarget.setPlainText("")
        self.ui.txtTarget.setFocus
        # set the scrollbar position
        try:
            value = self.indexes.index(index)
        except:
            return
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setValue(value)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)

    def setTarget(self, target):
        """Change the target text."""
        self.ui.txtTarget.setPlainText(target)
        
    def checkModified(self):
        if self.ui.txtTarget.document().isModified():
            self.emit(QtCore.SIGNAL("targetChanged"), self.ui.txtTarget.toPlainText())
            
    def setReadyForSave(self):
      self.emit(QtCore.SIGNAL("readyForSave"), True)

    def source2target(self):
        """Copy the text from source to target."""
        self.ui.txtTarget.setFocus()
        self.ui.txtTarget.selectAll()
        self.ui.txtTarget.insertPlainText(self.ui.txtSource.toPlainText())
        self.ui.txtTarget.document().setModified()

    def setHighLightSource(self, location):
        """call setHighLight by passing source document and location (offset, length)"""
        self.setHighLight(self.ui.txtSource.document(), location)        
        
    def setHighLightTarget(self, location):
        """call setHighLight by passing target document and location (offset, length)"""              
        self.setHighLight(self.ui.txtTarget.document(), location)        
    
    def setHighLight(self, doc, location):
        """HighLight on source or target depending on doc, and location (offset, and length)"""
        offsetindoc = location[0]
        length = location[1]
        overrides = []
        charformat = QtGui.QTextCharFormat()
        charformat.setFontWeight(QtGui.QFont.Bold)
        charformat.setForeground(QtCore.Qt.darkMagenta)                
        block = doc.findBlock(offsetindoc)        
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
            self.layout.clearAdditionalFormats()
            self.ui.txtSource.update()
            self.ui.txtTarget.update()
        except:
            pass        
        
    def selectCut(self):
        self.ui.txtSource.cut()        
                
    def applySettings(self):
        sourcefont = self.settings.value("tuSourceFont")
        if (sourcefont.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(sourcefont.toString())):
                self.ui.txtSource.setFont(fontObj)
        targetfont = self.settings.value("tuTargetFont")
        if (targetfont.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(targetfont.toString())):
                self.ui.txtTarget.setFont(fontObj)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = TUview()
    Form.show()
    sys.exit(app.exec_())
