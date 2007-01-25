from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_TableTM import Ui_Form
import sys, os

class tableTM(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Found Translation")
        self.headerLabels = [self.tr("Source"), self.tr("Target")]
        self.ui.tblTM.setColumnCount(len(self.headerLabels))
        for i in range(len(self.headerLabels)):
            self.ui.tblTM.resizeColumnToContents(i)
            self.ui.tblTM.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
        self.ui.tblTM.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.normalState = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
        self.connect(self.ui.tblTM, QtCore.SIGNAL("currentCellChanged(int, int, int, int)"), self.getCurrentTarget)
        self.connect(self.ui.tblTM, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.emitTarget)
        
    def fillTable(self, foundlist):
        '''fill each found unit into table
        @param foundlist:list of pofile object'''
        self.ui.tblTM.clear()
        self.ui.tblTM.setHorizontalHeaderLabels(self.headerLabels)
        self.ui.tblTM.setSortingEnabled(False)
        self.ui.tblTM.setRowCount(0)
        for i in range(len(foundlist)):
            for unit in foundlist[i].units:
                row = self.ui.tblTM.rowCount()
                self.ui.tblTM.setRowCount(row + 1)
                item = QtGui.QTableWidgetItem(unit.source)
                item.setFlags(self.normalState)
                self.ui.tblTM.setItem(row, 0, item)
                
                item = QtGui.QTableWidgetItem(unit.target)
                self.ui.tblTM.setItem(row, 1, item)
        self.ui.tblTM.setSortingEnabled(True)
        self.ui.tblTM.sortItems(0)
        self.ui.tblTM.resizeRowsToContents()
        self.show()
    
    def getCurrentTarget(self, row, col, preRow, preCol):
        item = self.ui.tblTM.item(row, 1)
        if (item):
            self.target = item.text()
    
    def emitTarget(self):
        self.emit(QtCore.SIGNAL("targetChanged"), self.target)
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    table = tableTM(None)
    table.show()
    sys.exit(table.exec_())

