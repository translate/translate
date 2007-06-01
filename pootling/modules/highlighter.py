#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Pootling
# Copyright 2007 WordForge Foundation
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

from pootling.modules import World
from PyQt4 import QtCore, QtGui

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        
        self.parent = parent
        
        # search format
        self.searchFormat = QtGui.QTextCharFormat()
        self.searchFormat.setFontWeight(QtGui.QFont.Bold)
        self.searchFormat.setForeground(QtCore.Qt.white)
        self.searchFormat.setBackground(QtCore.Qt.darkMagenta)
        
        # glossary format
        self.glossaryFormat = QtGui.QTextCharFormat()
        self.glossaryFormat.setFontWeight(QtGui.QFont.Bold)
        self.glossaryFormat.setForeground(QtCore.Qt.darkGreen)
        #self.glossaryFormat.setUnderlineStyle(QtGui.QTextCharFormat.DashDotDotLine)
        
        self.classFormat = self.glossaryFormat
        # avoid blank regular expression
        self.expression = QtCore.QRegExp(" ")
        self.searchExpression = None
    
    def highlightBlock(self, text):
        """
        highlight the text according to the self.expression
        @ param text: a document text.
        """
        index = text.indexOf(self.expression)
        while (index >= 0):
            length = self.expression.matchedLength()
            self.setFormat(index, length, self.classFormat)
            index = text.indexOf(self.expression, index + length);
        
        # highlight search
        if (self.searchExpression):
            index = text.indexOf(self.searchExpression)
            while (index >= 0):
                length = self.searchExpression.matchedLength()
                self.setFormat(index, length, self.searchFormat)
                index = text.indexOf(self.searchExpression, index + length)
                if (index):
                    self.searchExpression = None
                    break
    
    def setPattern(self, patternList):
        """
        build self.expression base on given pattern.
        @param patternList: list of string.
        """
        pattern = " | ".join(unicode(p) for p in patternList)
        pattern = QtCore.QString(pattern)
        self.expression = QtCore.QRegExp(pattern)
        self.expression.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    
    def setSearchString(self, searchString):
        """
        set searchExpression and make document() dirty then it will
        re highlightBlock().
        """
        # DOTO: fix search only highlight first found...
        if (not searchString):
            self.searchExpression = None
        else:
            self.searchExpression = QtCore.QRegExp(QtCore.QString(searchString))
            self.searchExpression.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.parent.document().markContentsDirty(0, len(self.parent.document().toPlainText()))
        
        
