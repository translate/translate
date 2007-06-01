from pootling.modules import World
from PyQt4 import QtCore, QtGui

class MyHighlighter(QtGui.QSyntaxHighlighter):
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
        pattern = QtCore.QString("not")
        self.expression = QtCore.QRegExp(pattern)
        
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
                index = text.indexOf(self.searchExpression, index + length);
        
    
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
        set searchExpression and call highlightBlock()
        """
        if (not searchString):
            self.searchExpression = None
            return
            
        self.searchExpression = QtCore.QRegExp(QtCore.QString(searchString))
        self.searchExpression.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.highlightBlock(self.parent.toPlainText())
        
    
class Highlighter(QtCore.QObject):
    '''highlight terms in glossary, search found, and tags'''
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
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
            
        self.currentBlock = None
        self.blockHighLightPair = {}
    
    def highlightBlock(self, block):
        '''highlight on the given block
        
        @ param block: block of a text document to highlight
        '''
        if (not block):
            return
        block.layout().setAdditionalFormats(self.blockHighLightPair[block.position()])
        block.document().markContentsDirty(block.position(), block.length())
        self.currentBlock = block
    
    def setHighlightRange(self, format, start = 0, length = 0):
        '''create a higlightRange for a block 
        
        @ param format: range highlight Format
        @ param start: start of range
        @ param length: length of range
        @ return highlightRange: highlightRange of a block
        '''
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.start = start
        self.highlightRange.length = length
        if (format == World.searchFormat):
            self.highlightRange.format = self.searchFormat
        if (format == World.glossaryFormat):
            self.highlightRange.format = self.glossaryFormat
        return self.highlightRange
    
    def setHighLight(self, block, start, length, format):
        '''set Highlight to a block'
        
        @ param block: block to highlight
        @ param start: start of range
        @ param length: length of range
        @ param format: range highlight Format
        '''
        highlightRange = self.setHighlightRange(format, start, length)
        if self.blockHighLightPair.has_key(block.position()):
            self.blockHighLightPair[block.position()].append(highlightRange)
        else:
            highlightRangeList = []
            highlightRangeList.append(highlightRange)
            self.blockHighLightPair[block.position()] = highlightRangeList
        self.highlightBlock(block)
    
    def clearSearchFormats(self):
        '''clear search format from current block'''
        if (self.currentBlock):
            blockHighlightRangeList = self.blockHighLightPair[self.currentBlock.position()]
            for list in blockHighlightRangeList:
                if list.format == self.searchFormat:
                    blockHighlightRangeList.remove(list)
            self.blockHighLightPair[self.currentBlock.position()] = blockHighlightRangeList
            self.highlightBlock(self.currentBlock)
