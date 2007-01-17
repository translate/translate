#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
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
# This module is providing an translation memory dialog

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.pootlingdic.ui.Ui_TM import Ui_Dialog
from translate.storage import po
from translate.convert import po2tmx
from translate.storage import tmx
from translate.misc import wStringIO

class tm(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.subscan = None
    
    def showDialog(self):
        #lazy init
        if (not self.ui):
            self.ui = Ui_Dialog()
            self.ui.setupUi(self)
            self.setWindowTitle(self.tr("Translation Database"))
            self.setMinimumSize(400, 400)
            self.setModal(True)
            self.ui.btnBrowseFile.setObjectName("browsefilepath")
            self.ui.btnBrowseDatabase.setObjectName("browsedbpath")
            self.connect(self.ui.btnBrowseFile, QtCore.SIGNAL("clicked(bool)"), self.getPath)
            self.connect(self.ui.btnBrowseDatabase, QtCore.SIGNAL("clicked(bool)"), self.getPath)
            self.connect(self.ui.btncancel, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
            self.connect(self.ui.btnGenerate, QtCore.SIGNAL("clicked(bool)"), self.generateDB)
            self.connect(self.ui.radio_file, QtCore.SIGNAL("clicked(bool)"), self.ui.lineFile.clear)
            self.connect(self.ui.radio_folder, QtCore.SIGNAL("clicked(bool)"), self.ui.lineFile.clear)
            self.connect(self.ui.radio_folder_sub, QtCore.SIGNAL("clicked(bool)"), self.ui.lineFile.clear)
        self.show()
    
    def getPath(self):
        '''get path of translated file(s) to convert to tbx, tmx or databse'''
        if (self.sender().objectName() == "browsefilepath"):
            if (self.ui.radio_file.isChecked()):
                path = QtGui.QFileDialog.getOpenFileName(
                             self,
                             "Select one or more files to open",
                             QtCore.QDir.homePath(),
                             "All Files (*.*)")
            else:
                if (self.ui.radio_folder_sub.isChecked()):
                    self.subscan = True
                path = self.getExistingDirectory()
                
            if (path):
                self.ui.lineFile.setText(path)
        
        if (self.sender().objectName() == "browsedbpath"):
            path = self.getExistingDirectory()
            if (path):
                self.ui.lineDatabase.setText(path)
                
    def getExistingDirectory(self):
        return QtGui.QFileDialog.getExistingDirectory(self, self.tr("Get Directory"),
                                                 QtCore.QDir.homePath(),
                                                 QtGui.QFileDialog.ShowDirsOnly
                                                 | QtGui.QFileDialog.DontResolveSymlinks)
        
    def generateDB(self):
        path = str(self.ui.lineFile.text())
        if (os.path.isfile(path)):
            output = os.path.join(str(self.ui.lineDatabase.text()) + os.path.splitext(os.path.split(path)[1])[0] + '.tmx')
            self.process(path, output)
        
        if (os.path.isdir(path)):
            if (not self.subscan):
                self.workOnFiles(path)
            else:
                for roots, dirs, files, in os.walk(path):
                    if(not roots.endswith('/')):
                        roots = roots + '/'
                    self.workOnFiles(roots)
                self.subscan = None
                
    def workOnFiles(self, path):
        for roots, dirs, files in os.walk(path):
            if (roots != path):
                break
            else:
                for file in files:
                    if (file.endswith('po') or file.endswith('xliff') or file.endswith('xlf')):
                        # TODO: add subdir to path if there is
                        output = os.path.join(str(self.ui.lineDatabase.text()) + os.path.splitext(file)[0] + '.tmx')
                        self.process(os.path.join(roots + file), output)
                
    def process(self, path, output):
        source = self.getSource(path)
        tmxfile_obj = tmx.tmxfile()
        po2tmx.po2tmx().convertfiles(source, tmxfile_obj, targetlanguage = 'km')
        fout = open(output, 'w')
        fout.write(str(tmxfile_obj))
        fout.close()
        return
        
    def getSource(self, path):
        fin = open(path, 'r')
        if (path.endswith('po')):
            outputpo = po.pofile(fin)
        if (path.endswith('xlf') or path.endswith('xliff')):
            from translate.convert import xliff2po
            outputpo = xliff2po.xliff2po().convertfile(fin)
        buffer = wStringIO.StringIO(outputpo)
        fin.close()
        return buffer
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tmdialog = tm(None)
    tmdialog.showDialog()
    sys.exit(tmdialog.exec_())

 
