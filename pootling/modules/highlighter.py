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
        
        # var format
        self.varFormat = QtGui.QTextCharFormat()
        self.varFormat.setForeground(QtCore.Qt.blue)
        self.vars = "%\\d+|&\\w+;"
        self.varExpression = QtCore.QRegExp(self.vars)
        # tag format
        self.tagFormat = QtGui.QTextCharFormat()
        self.tagFormat.setForeground(QtCore.Qt.darkMagenta)
        self.tags = "<b>.+</b>"
        self.tagExpression = QtCore.QRegExp(self.tags)
        
        # glossary format
        self.glsFormat = QtGui.QTextCharFormat()
        self.glsFormat.setFontWeight(QtGui.QFont.Bold)
        self.glsFormat.setForeground(QtCore.Qt.darkGreen)
        self.glsFormat.setUnderlineStyle(QtGui.QTextCharFormat.DotLine)
##        self.glsFormat.setFontUnderline(True)
##        self.glsFormat.setUnderlineColor(QtCore.Qt.darkGreen)
        self.highlightGlossary = True
        self.glsExpression = None

        # search format
        self.searchFormat = QtGui.QTextCharFormat()
        self.searchFormat.setFontWeight(QtGui.QFont.Bold)
        self.searchFormat.setForeground(QtCore.Qt.white)
        self.searchFormat.setBackground(QtCore.Qt.darkMagenta)
                
        self.searchExpression = None
    
    def highlightBlock(self, text):
        """
        highlight the text according to the self.expression
        @ param text: a document text.
        """
        # highlight arguments, variable
        varIndex = text.indexOf(self.varExpression)
        tagIndex = text.indexOf(self.tagExpression)
        if (self.glsExpression):
            glsIndex = text.indexOf(self.glsExpression)
        else:
            glsIndex = -1
        
        while (tagIndex >= 0) or (varIndex >= 0) or (glsIndex >= 0):
            length = self.tagExpression.matchedLength()
            self.setFormat(tagIndex, length, self.tagFormat)
            tagIndex = text.indexOf(self.tagExpression, tagIndex + length)
            length = self.varExpression.matchedLength()
            self.setFormat(varIndex, length, self.varFormat)
            varIndex = text.indexOf(self.varExpression, varIndex + length)
            
            # highlight glossary
            if (self.highlightGlossary) and (self.glsExpression):
                length = self.glsExpression.matchedLength()
                self.setFormat(glsIndex, length, self.glsFormat)
                glsIndex = text.indexOf(self.glsExpression, glsIndex + length)
        
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
        build self.glsExpression base on given pattern.
        @param patternList: list of string.
        """
        pattern = "\\b(" + "|".join(unicode(p) for p in patternList) + ")\\b"
#        pattern = QtCore.QString(pattern)
        self.glsExpression = QtCore.QRegExp(pattern)
        self.glsExpression.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    
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
        
    def setHighlightGlossary(self, bool):
        self.highlightGlossary = bool
    
