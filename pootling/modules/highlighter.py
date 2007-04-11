from pootling.modules import World
from PyQt4 import QtCore, QtGui

class Highlighter(QtCore.QObject):
    '''highlight terms in glossary, search found, and tags'''
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        
        # search format
        self.searchFormat = QtGui.QTextCharFormat()
        self.searchFormat.setFontWeight(QtGui.QFont.Bold)
        self.searchFormat.setForeground(QtCore.Qt.white)
        self.searchFormat.setBackground(QtCore.Qt.darkMagenta)
        
        #        # glossary format
        self.glossaryFormat = QtGui.QTextCharFormat()
        self.glossaryFormat.setFontWeight(QtGui.QFont.Bold)
        self.glossaryFormat.setForeground(QtCore.Qt.darkGreen)
        self.glossaryFormat.setUnderlineStyle(QtGui.QTextCharFormat.DashDotDotLine)
            
        self.currentblock = None
        self.highlightRangeList = []
    
    def highlightBlock(self, block):
        if (not block):
            return
        block.layout().setAdditionalFormats(self.highlightRangeList)
        block.document().markContentsDirty(block.position(), block.length())
        self.currentblock = block
    
    def setHighlightRange(self, format, start = 0, length = 0):
        highlightRange = QtGui.QTextLayout.FormatRange()
        highlightRange.start = start
        highlightRange.length = length
        if (format == World.searchFormat):
            highlightRange.format = self.searchFormat
        if (format == World.glossaryFormat):
            highlightRange.format = self.glossaryFormat
        self.highlightRangeList.append(highlightRange)
        
    def clearAdditionalFormats(self):
        '''clear format from current block'''
        #TODO current block of which TextBox (txtSource or txtTarget)
        for list in self.highlightRangeList:
            if list.format == self.searchFormat:
                self.highlightRangeList.remove(list)
        self.highlightBlock(self.currentblock)
