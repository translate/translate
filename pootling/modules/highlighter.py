from PyQt4 import QtCore, QtGui

class Highlighter(QtCore.QObject):
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        
        # highlight search
        self.searchFormat = QtGui.QTextCharFormat()
        self.searchFormat.setFontWeight(QtGui.QFont.Bold)
        self.searchFormat.setForeground(QtCore.Qt.white)
        self.searchFormat.setBackground(QtCore.Qt.darkMagenta)
        
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.searchFormat
        self.block = None
        
#        # highlight tage
#        tagFormat = QtGui.QTextCharFormat()
#        tagFormat.setFontWeight(QtGui.QFont.Bold)
#        tagFormat.setForeground(QtCore.Qt.blue)
#        
#        quoteFormat = QtGui.QTextCharFormat()
#        quoteFormat.setForeground(QtCore.Qt.darkGreen)
#        accelFormat = QtGui.QTextCharFormat()
#        accelFormat.setForeground(QtCore.Qt.darkMagenta)
#        
#        tagPattern = QtCore.QRegExp("%\d+|%s|%d")
#        accelPattern = QtCore.QRegExp("&\S")
#        quotePattern = QtCore.QRegExp("<.+>|</.+>")
#        
#        self.formats = [tagFormat, accelFormat, quoteFormat]
#        self.patterns = [tagPattern, accelPattern, quotePattern]
#        self.expression = QtCore.QRegExp(tagPattern.pattern() + "|" + \
#                accelPattern.pattern() + "|" + \
#                quotePattern.pattern())
        
#    def highlightBlock(self, text):
#        index = text.indexOf(self.expression)
#        charFormat = self.formats[0]
#        while (index >= 0):
#            length = self.expression.matchedLength()
#            # format the found text
#            cap = self.expression.cap()
#            for i in range(len(self.patterns)):
#                if (cap.indexOf(self.patterns[i]) > -1):
#                    charFormat = self.formats[i]
#            self.setFormat(index, length, charFormat)
#            index = text.indexOf(self.expression, index + length)
#        
#        if (self.index >= 0):
#            self.setFormat(self.index, self.length, self.searchFormat)
#            self.index = None
#    
#    def initSearch(self, index, length):
#        self.index = index
#        self.length = length
    
    def highlightBlock(self, block):
        self.block = block
        if(self.block):
            self.block.layout().setAdditionalFormats([self.highlightRange])
            self.block.document().markContentsDirty(self.highlightRange.start, self.highlightRange.length)
    
    def setHighlightRange(self, start = 0, length = 0):
        self.highlightRange.start = start
        self.highlightRange.length = length
        
    def clearAdditionalFormats(self):
        self.setHighlightRange()
        self.highlightBlock(self.block)
        
        
