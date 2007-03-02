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

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        
        self.index = None
        self.searchFormat = QtGui.QTextCharFormat()
        self.searchFormat.setFontWeight(QtGui.QFont.Bold)
        self.searchFormat.setForeground(QtCore.Qt.white)
        self.searchFormat.setBackground(QtCore.Qt.darkMagenta)
        
        tagFormat = QtGui.QTextCharFormat()
        tagFormat.setFontWeight(QtGui.QFont.Bold)
        tagFormat.setForeground(QtCore.Qt.blue)
        quoteFormat = QtGui.QTextCharFormat()
        quoteFormat.setForeground(QtCore.Qt.darkGreen)
        accelFormat = QtGui.QTextCharFormat()
        accelFormat.setForeground(QtCore.Qt.darkMagenta)
        
        tagPattern = QtCore.QRegExp("%\d+|%s|%d")
        accelPattern = QtCore.QRegExp("&\S")
        quotePattern = QtCore.QRegExp("<.+>|</.+>")
        
        self.formats = [tagFormat, accelFormat, quoteFormat]
        self.patterns = [tagPattern, accelPattern, quotePattern]
        self.expression = QtCore.QRegExp(tagPattern.pattern() + "|" + \
                accelPattern.pattern() + "|" + \
                quotePattern.pattern())
        
    def highlightBlock(self, text):
        index = text.indexOf(self.expression)
        charFormat = self.formats[0]
        while (index >= 0):
            length = self.expression.matchedLength()
            # format the found text
            cap = self.expression.cap()
            for i in range(len(self.patterns)):
                if (cap.indexOf(self.patterns[i]) > -1):
                    charFormat = self.formats[i]
            self.setFormat(index, length, charFormat)
            index = text.indexOf(self.expression, index + length)
        
        if (self.index >= 0):
            self.setFormat(self.index, self.length, self.searchFormat)
            self.index = None
    
    def initSearch(self, index, length):
        self.index = index
        self.length = length

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
        self.applySettings()
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        
        # create highlight font
        self.highlightFormat = QtGui.QTextCharFormat()
        self.highlightFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightFormat.setForeground(QtCore.Qt.white)
        self.highlightFormat.setBackground(QtCore.Qt.darkMagenta)
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.highlightFormat
        
        self.sourceLength = 0
        
        self.sourceHighlight = Highlighter(self.ui.txtSource)
        self.targetHighlight = Highlighter(self.ui.txtTarget)

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
        self.disconnect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
        if (not unit) or (not hasattr(unit, "x_editor_filterIndex")):
            self.ui.lblComment.hide()
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
            self.ui.txtSource.setEnabled(False)
            self.ui.txtTarget.setEnabled(False)
            return
        self.ui.txtTarget.setReadOnly(False)

        comment = unit.getcontext()
        comment += unit.getnotes("developer")
        if (comment == ""):
            self.ui.lblComment.hide()
        else:
            self.ui.lblComment.show()
            self.ui.lblComment.setText(unicode(comment))
        self.showUnit(unit)
        # set the scrollbar position
        self.setScrollbarValue(unit.x_editor_filterIndex)
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
    
    def showUnit(self, unit):
        if (not unit.hasplural()):
            """This will be called when unit is singular.
        @param unit: unit to consider if signal or not."""
            #hide tab for plural unit and show the normal text boxes for signal unit.
            self.secondpage = False
            self.ui.sourceStacked.setCurrentIndex(0)
            self.ui.targetStacked.setCurrentIndex(0)
            self.ui.txtSource.setPlainText(unit.source)
            if (unicode(unit.target) !=  unicode(self.ui.txtTarget.toPlainText())):
                self.ui.txtTarget.setPlainText(unit.target)
        else:
            # create source tab
            self.ui.sourceStacked.setCurrentIndex(1)
            self.addRemoveTabWidget(self.ui.tabWidgetSource, len(unit.source.strings), unit.source.strings)
            
            # create target tab
            nplurals = World.settings.value("nPlural").toInt()[0]
            self.ui.targetStacked.setCurrentIndex((nplurals > 1) and 1 or 0)
            # TODO: when nplurals changed in Preference Translated String Viw also changes
            # TODO: reset min and max of nplural spinbox in Preference, otherwise it will cause bugs here
            if (not (nplurals > 1)):
                if (unicode(unit.target) !=  unicode(self.ui.txtTarget.toPlainText())):
                    self.ui.txtTarget.setPlainText(unit.target)
                self.secondpage = False
            else:
                self.secondpage = True
                self.addRemoveTabWidget(self.ui.tabWidgetTarget, nplurals, unit.target.strings)
                for i in range(self.ui.tabWidgetTarget.count()):
                    # make sure it is not emit signal targetchanged everytime when unit is updated.
                    textbox = self.ui.tabWidgetTarget.widget(i).children()[1]
                    textbox.setReadOnly(False)
                    self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
                    # everytime display a unit, connect signal
                    self.connect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
    
    def addRemoveTabWidget(self, tabWidget, length, msg_strings):
        '''Add or remove tab to a Tab widget.
        
        @param tabWidget: QTabWidget
        @param length: amount of tab as int type
        @param msg_strings: list of strings to set to textbox in each tab of tabWidget
        
        '''
        count = tabWidget.count()
        if (not (count  == length)):
            while (count > length):
                count -= 1
                tabWidget.removeTab(count)
            while (count < length):
                count += 1
                widget = QtGui.QWidget()
                gridlayout = QtGui.QGridLayout(widget)
                gridlayout.setMargin(0)
                gridlayout.setSpacing(0)
                textedit = QtGui.QTextEdit()
                gridlayout.addWidget(textedit)
                tabWidget.addTab(widget, "Plural " + str(count))
            # add each source string of a unit to widget
        minloop = min(count, len(msg_strings))
        for i in range(minloop):
            textbox = tabWidget.widget(i).children()[1]
            if (unicode(msg_strings[i]) != unicode(textbox.toPlainText())):
                textbox.setText(msg_strings[i])
            textbox.setReadOnly(True)
    
    def emitTargetChanged(self):
        if ((not hasattr(self, "secondpage")) or  (not self.secondpage)):
            self.emit(QtCore.SIGNAL("targetChanged"), unicode(self.ui.txtTarget.toPlainText()))
        else:
            list = []
            for i in range(self.ui.tabWidgetTarget.count()):
                textbox = self.ui.tabWidgetTarget.widget(i).children()[1]
                list.append(unicode(textbox.toPlainText()))
                # prevent infinit loop of textchanged signal everytime a plural unit target string is changed.
                self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
            self.emit(QtCore.SIGNAL("targetChanged"), list)
            
    def source2target(self):
        """Copy the text from source to target."""
        self.ui.txtTarget.setText(self.ui.txtSource.toPlainText())

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        self.sourceHighlight.initSearch(position, length)
##        if ((textField != World.source and textField != World.target)  or position == None):
##            if (not getattr(self, "highlightBlock", None)):
##                return
##            self.highlightRange.length = 0
##        else:
##            if (textField == World.source):
##                textField = self.ui.txtSource
##            else:
##                textField = self.ui.txtTarget
##            self.highlightBlock = textField.document().findBlock(position)
##            self.highlightRange.start = position - self.highlightBlock.position()
##            self.highlightRange.length = length
##        self.highlightBlock.layout().setAdditionalFormats([self.highlightRange])
##        self.highlightBlock.document().markContentsDirty(self.highlightBlock.position(), self.highlightBlock.length())

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
        
        self.emitTargetChanged()

if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    Form = TUview(None)
    Form.show()
    sys.exit(app.exec_())
