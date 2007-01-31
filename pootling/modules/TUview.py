#!/usr/bin/python
# -*- coding: utf8 -*-

# Pootling
# Copyright 2006 WordForge Foundation
#
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
from pootling.ui.Ui_TUview import Ui_TUview
from translate.storage import po
from pootling.modules import World

class MyHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self.tagFormat = QtGui.QTextCharFormat()
        self.tagFormat.setFontWeight(QtGui.QFont.Bold)
        self.tagFormat.setForeground(QtCore.Qt.blue)
        
        self.quoteFormat = QtGui.QTextCharFormat()
        self.quoteFormat.setForeground(QtCore.Qt.darkGreen)
        
        self.accelFormat = QtGui.QTextCharFormat()
        self.accelFormat.setForeground(QtCore.Qt.darkMagenta)

    def highlightBlock(self, text):
        # tag
        pattern = QtCore.QString("%\d+|%s|%d")
        expression = QtCore.QRegExp(pattern)
        index = text.indexOf(expression)
        while (index >= 0):
            length = expression.matchedLength()
            self.setFormat(index, length, self.tagFormat)
            index = text.indexOf(expression, index + length)
        
        # quote
##        pattern = QtCore.QString("\".+\"")
        pattern = QtCore.QString("<.+>|</.+>")
        expression = QtCore.QRegExp(pattern)
        index = text.indexOf(expression)
        while (index >= 0):
            length = expression.matchedLength()
            self.setFormat(index, length, self.quoteFormat)
            index = text.indexOf(expression, index + length)
        
        # accelerator
        pattern = QtCore.QString("&\S")
        expression = QtCore.QRegExp(pattern)
        index = text.indexOf(expression)
        while (index >= 0):
            length = expression.matchedLength()
            self.setFormat(index, length, self.accelFormat)
            index = text.indexOf(expression, index + length)
        

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
        self.ui.lblComment.hide()
        self.ui.txtTarget.setReadOnly(True)
        #support only qt4.2
##        self.ui.txtTarget.moveCursor(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor )
        self.ui.txtTarget.setWhatsThis("<h3>Translated String</h3>This editor displays and lets you edit the translation of the currently displayed string.")
        self.ui.txtSource.setWhatsThis("<h3>Original String</h3>This part of the window shows you the original string of the currently displayed entry. <br>You can not edit this string.")
        self.ui.lblComment.setWhatsThis("<h3>Important Comment</h3>Hints from the developer to the translator are displayed in this area. This area will be hidden if there is no hint. ")
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
        self.tabForPlural()
        
        MyHighlighter(self.ui.txtSource)
        MyHighlighter(self.ui.txtTarget)
        
    def tabForPlural(self):
        self.tabSourcePlurals = []
        self.tabTargetPlurals = []
        self.gridlayoutSList = []
        self.gridlayoutTarList = []
        self.txtSourceList = []
        self.txtTargetList = []
        # tab for plural
        self.tabSource = QtGui.QTabWidget(self.form)
        self.tabSource.setObjectName("tabSource")
        self.ui.gridlayout.addWidget(self.tabSource,0,0,1,1)

        self.tabTarget = QtGui.QTabWidget(self.form)
        self.tabTarget.setObjectName("tabTarget")
        self.ui.gridlayout.addWidget(self.tabTarget,1,0,1,1)
        
        self.tabSource.hide()
        self.tabTarget.hide()

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
        """emit "scrollToRow" signal with value as row start from 0.
        @param value: current row."""
        self.emit(QtCore.SIGNAL("scrollToRow"), value)
    
    def updateView(self, unit):
        """Update the text in source and target, set the scrollbar position,
        remove a value from scrollbar if the unit is not in filter.
        Then recalculate scrollbar maximum value.
        @param unit: unit to set in target and source.
        @param index: value in the scrollbar to be removed."""
        self.disconnect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)
        if (not unit) or (not hasattr(unit, "x_editor_filterIndex")):
            self.ui.lblComment.hide()
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
            self.ui.txtSource.setEnabled(False)
            self.ui.txtTarget.setEnabled(False)
            return
        self.ui.txtTarget.setReadOnly(False)

        comment = ""
        if isinstance(unit, po.pounit):
            comment = unit.getcontext()
        comment += unit.getnotes("developer")
        if (comment == ""):
            self.ui.lblComment.hide()
        else:
            self.ui.lblComment.show()
            self.ui.lblComment.setText(unicode(comment))
        if unit.hasplural():
            self.unitPlural(unit)
        else:
            self.unitSingle(unit)
        # set the scrollbar position
        self.setScrollbarValue(unit.x_editor_filterIndex)
     
    def unitPlural(self, unit):
        """ This will be call when unit is plural"""
        self.tabSource.show()
        self.tabTarget.show()
        self.ui.txtSource.hide()
        self.ui.txtTarget.hide()
        if (self.tabSource.count() == len(unit.source.strings)):
            print self.tabSource.count()
            print len(unit.source.strings)
            for i in range(len(unit.source.strings)):
                self.txtSourceList[i].setPlainText(unit.source.strings[i])
        else:
            for i in range(len(unit.source.strings)):
                print "hi"
                tabSourcePlural = QtGui.QWidget(self.tabSource)
                self.tabSourcePlurals.append(tabSourcePlural)
                self.tabSourcePlurals[i].setObjectName("tabSourcePlural%d" % i)
                
                self.gridlayoutS = QtGui.QGridLayout(self.tabSourcePlurals[i])
                self.gridlayoutSList.append(self.gridlayoutS)
                self.gridlayoutSList[i].setMargin(0)
                self.gridlayoutSList[i].setSpacing(0)
                self.gridlayoutSList[i].setObjectName("gridlayoutS%d" % i)
                
                self.txtSource = QtGui.QTextEdit(self.tabSourcePlurals[i])
                self.txtSourceList.append(self.txtSource)
                self.txtSourceList[i].setObjectName("txtSource%d" % i)
                self.txtSourceList[i].setTabChangesFocus(True)
                self.txtSourceList[i].setUndoRedoEnabled(False)
                self.txtSourceList[i].setReadOnly(True)
                self.gridlayoutSList[i].addWidget(self.txtSourceList[i],0,0,1,1)
                self.txtSourceList[i].setPlainText(unit.source.strings[i])
                
                self.tabSource.addTab(self.tabSourcePlurals[i], "")
                self.tabSource.setTabText(self.tabSource.indexOf(self.tabSourcePlurals[i]), self.tr("Plural%d" % i))
                self.ui.gridlayout.addWidget(self.ui.fileScrollBar,0,2,1,1)

                # target
            nplurals = 2  # nplurals will be adapted to the language set in preference.
            for i in range(nplurals):
                tabTargetPlural = QtGui.QWidget(self.tabTarget)
                self.tabTargetPlurals.append(tabTargetPlural)
                self.tabTargetPlurals[i].setObjectName("tabTargetPlural%d" % i)
                
                self.gridlayoutTar = QtGui.QGridLayout(self.tabTargetPlurals[i])
                self.gridlayoutTarList.append(self.gridlayoutTar)
                self.gridlayoutTarList[i].setMargin(0)
                self.gridlayoutTarList[i].setSpacing(0)
                self.gridlayoutTarList[i].setObjectName("gridlayoutTar%d" % i)
                
                self.tabTarget.addTab(self.tabTargetPlurals[i], "")
                self.tabTarget.setTabText(self.tabTarget.indexOf(self.tabTargetPlurals[i]), self.tr("Plural%d"% i))
                
                self.txtTarget = QtGui.QTextEdit(self.tabTargetPlurals[i])
                self.txtTargetList.append(self.txtTarget)
                self.txtTargetList[i].setObjectName("txtTarget%d"% i)
                self.gridlayoutTarList[i].addWidget(self.txtTargetList[i],0,0,1,1)
                self.txtTargetList[i].setPlainText(unit.target.strings[1])
                self.connect(self.txtTargetList[i], QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)

    def unitSingle(self, unit):
        """This will be called when unit is singular"""
        self.tabSource.hide()
        self.tabTarget.hide()
        self.ui.txtSource.show()
        self.ui.txtTarget.show()
        self.ui.txtSource.setPlainText(unit.source)
        self.ui.txtTarget.setPlainText(unit.target)
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)

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
        self.checkModified()

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
            self.ui.txtSource.setTabStopWidth(QtGui.QFontMetrics(fontObj).width("m"*8))

        targetfont = World.settings.value("tuTargetFont")
        if (targetfont.isValid() and fontObj.fromString(targetfont.toString())):
            self.ui.txtTarget.setFont(fontObj)
            self.ui.txtTarget.setTabStopWidth(QtGui.QFontMetrics(fontObj).width("m"*8))
            
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    Form = TUview(None)
    Form.show()
    sys.exit(app.exec_())
