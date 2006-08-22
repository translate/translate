#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 1.0 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)about:blank
#

from PyQt4 import QtCore
from translate.storage import factory

class status:
    def __init__(self, units):
        self.numFuzzy = 0
        self.numTranslated = 0
        self.numTotal = len(units)
        for i in range(self.numTotal):
            #count fuzzy TU
            if units[i].isfuzzy():
                self.numFuzzy += 1
            #cound translated TU
            if units[i].istranslated():
                self.numTranslated += 1                
        self.numUntranslated  = self.numTotal - self.numTranslated
        
    def status(self):
        self.numUntranslated = self.numTotal - self.numTranslated
        return "Total: "+ str(self.numTotal) + "  |  Fuzzy: " +  str(self.numFuzzy) + "  |  Translated: " +  str(self.numTranslated) + "  |  Untranslated: " + str(self.numUntranslated)
        
    def addNumFuzzy(self):
        self.numFuzzy += 1

    def subNumFuzzy(self):
        self.numFuzzy -= 1

    def addNumTranslated(self):
        self.numTranslated += 1

    def subNumTranslated(self):
        self.numTranslated -= 1

class emptyUnit:
    def __init__(self):
        self.source = ''
        self.target = ''
    
    def getnotes(self):
        return ''
    

class Operator(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._modified = False
        self._saveDone = False
        
        self._unitpointer = None
        self.unitPointerList = []
    
    def getUnits(self, fileName):
        self.store = factory.getobject(fileName)
        
        self.unitStatus = status(self.store.units)
        self.emitNewUnits()
        self._unitpointer = 0
        self.emitCurrentUnit()
        self.emitCurrentStatus()

    def emitCurrentUnit(self):
        if (self.unitPointerList == []):
            self.emptyUnit = emptyUnit()
            self.emit(QtCore.SIGNAL("noUnit"))
            return
        elif (self._unitpointer == 0):
            self.firstUnit()
        elif (self._unitpointer == len(self.unitPointerList) - 1):
            self.lastUnit()
        else:
            self.middleUnit()
        
        currentUnit = self.unitPointerList[self._unitpointer]
        if (currentUnit != len(self.store.units)):
            self.emit(QtCore.SIGNAL("currentUnit"), self.store.units[currentUnit])
            self.emit(QtCore.SIGNAL("currentPosition"), self._unitpointer)

    def emitNewUnits(self):
        self._unitpointer = 0
        self.unitPointerList = range(len(self.store.units))
        self.emit(QtCore.SIGNAL("newUnits"), self.store.units, self.unitPointerList)

    def emitFilteredUnits(self, filter):
        if (filter == 'fuzzy'):
            filter = 1
        elif (filter == 'translated'):
            filter = 2
        elif (filter == 'untranslated'):
            filter = 3
        else:
            filter = 0
        
        self._unitpointer = 0
        filteredUnits = []
        self.unitPointerList = []
        for i in range(len(self.store.units)):

            if (filter == 1):
                if (self.store.units[i].isfuzzy()):
                    filteredUnits.append(self.store.units[i])
                    self.unitPointerList.append(i)
            elif (filter == 2):
                if (self.store.units[i].istranslated()):
                    filteredUnits.append(self.store.units[i])
                    self.unitPointerList.append(i)
            elif (filter == 3):
                if (not self.store.units[i].istranslated()):
                    filteredUnits.append(self.store.units[i])
                    self.unitPointerList.append(i)

        self.emit(QtCore.SIGNAL("newUnits"), filteredUnits, self.unitPointerList)
        #self.emitCurrentUnit()

    def emitUpdateUnit(self):
        if (self._unitpointer != None):            
            self.emit(QtCore.SIGNAL("updateUnit"))    

    def takeoutUnit(self, value):
        self.unitPointerList.pop(value)
    
    def firstUnit(self):
        self.emit(QtCore.SIGNAL("firstUnit"))
    
    def lastUnit(self):
        self.emit(QtCore.SIGNAL("lastUnit"))
    
    def middleUnit(self):
        self.emit(QtCore.SIGNAL("middleUnit"))
        
    def previous(self):
        if self._unitpointer > 0:
            self.emitUpdateUnit()
            self._unitpointer -= 1
            self.emitCurrentUnit()
        
    def next(self):
        # move to next unit inside the list, not the whole store.units
        if self._unitpointer < len(self.unitPointerList):
            self.emitUpdateUnit()
            #if (self._unitpointer == len(self.unitPointerList) - 1):
            #    self._unitpointer -= 1
            self._unitpointer += 1
            self.emitCurrentUnit()
        
    def first(self):
        self.emitUpdateUnit()
        self._unitpointer = 0
        self.emitCurrentUnit()
        
    def last(self):
        self.emitUpdateUnit()
        self._unitpointer = len(self.unitPointerList) - 1
        self.emitCurrentUnit()

    def saveStoreToFile(self, fileName):
        self.emitUpdateUnit()
        self.store.savefile(fileName)
        self._saveDone = True

    def modified(self):
        self.emitUpdateUnit()
        if self._saveDone:
            self._modified = False
            self._saveDone = False
        return self._modified
    
    def setComment(self, comment):
        """set the comment which is QString type to the current unit."""
        currentUnit = self.unitPointerList[self._unitpointer]
##        self.store.units[currAentUnit].setnotes()
        self.store.units[currentUnit].addnote(unicode(comment))
        self._modified = True        
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit."""
        unit = self.unitPointerList[self._unitpointer]
        currentUnit = self.store.units[unit]
        before_isuntranslated = not currentUnit.istranslated()
        beforeIsFuzzy = currentUnit.isfuzzy()
        currentUnit.target = unicode(target)
        if (currentUnit.target != ''):
            currentUnit.marktranslated()
            if (beforeIsFuzzy):
                self.unitStatus.subNumFuzzy()
        after_istranslated = currentUnit.istranslated()
        if (before_isuntranslated and after_istranslated):
            self.unitStatus.addNumTranslated()
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)
        elif (not before_isuntranslated and not after_istranslated):
            self.unitStatus.subNumTranslated()
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)

        self.emitCurrentStatus()
        self._modified = True


    def setCurrentUnit(self, value):
        self.emitUpdateUnit()
        self._unitpointer = self.unitPointerList.index(value)
        self.emitCurrentUnit()

    def setCurrentPosition(self, value):
        self.emitUpdateUnit()
        self._unitpointer = value
        self.emitCurrentUnit()
    
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit"""
        unit = self.unitPointerList[self._unitpointer]
        currentUnit = self.store.units[unit]
        boolFuzzy = not currentUnit.isfuzzy()
        currentUnit.markfuzzy(boolFuzzy)
        self._modified = True
        if (boolFuzzy):
            self.unitStatus.addNumFuzzy()
        else:
            self.unitStatus.subNumFuzzy()
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)
        self.emitCurrentStatus()
    
    def emitCurrentStatus(self):    
        self.emit(QtCore.SIGNAL("currentStatus"), self.unitStatus.status())
    
    def cutEdit(self, object):        
        try:
            self.connect(object, QtCore.SIGNAL("copyAvailable(bool)"), QtCore.SLOT("setEnabled"))
            object.cut()
        except TypeError:
            pass
            
    def copyEdit(self, object):          
        try:
            self.connect(object, QtCore.SIGNAL("copyAvailable(bool)"), QtCore.SLOT("setEnabled"))
            object.copy()
        except TypeError:
            pass
        
        
    def undoEdit(self, object):
        object.document().undo()        
     
    def redoEdit(self, object):
        object.document().redo()

    
