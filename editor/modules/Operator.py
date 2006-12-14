#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
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
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#     
from PyQt4 import QtCore, QtGui
from translate.storage import factory
from translate.storage import po
##from translate.storage import poheader
from translate.storage import xliff
import modules.World as World
from modules.Status import Status

class Operator(QtCore.QObject):
    """
    Operates on the internal datastructure.
    The class loads and saves files and navigates in the data.
    Provides means for searching and filtering.
    
    @signal currentStatus(string): emitted with the new status message
    @signal newUnits(store.units): emitted with the new units
    @signal updateUnit(): emitted when the views should update the unit´s data
    @signal toggleFirstLastUnit(atFirst, atLast): emitted to allow dis/enable of actions
    @signal filteredList(list, filter): emitted when the filter was changed
    @signal savedAlready(False): emitted when a file was saved
    """
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._modified = False
        self._unitpointer = None
        
    def getUnits(self, fileName):
        """reading a file into the internal datastructure.
        @param fileName: the file to open"""
        self.fileName = fileName
        self.store = factory.getobject(fileName)
        self._modified = False

        # filter flags
        self.filter = World.filterAll
        
        # get status for units
        self.status = Status(self.store.units)
        self.emitStatus()

        self.emit(QtCore.SIGNAL("newUnits"), self.store.units)
        self.emitFiltered(self.filter)

    def emitStatus(self):
        self.emit(QtCore.SIGNAL("currentStatus"), self.status.statusString())        

    def emitCurrentUnit(self):
        """send currentUnit signal with currentUnit, currentIndex."""
        # TODO: Sending toggleFirstLastUnit only needed.
        atFirst = (self._unitpointer == 0)
        atLast = (self._unitpointer >= len(self.filteredList) - 1)
        self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), atFirst, atLast)
        self.searchPointer = self._unitpointer
        currentIndex = self._getCurrentIndex()
        if (currentIndex == -1):
            currentUnit = None
            currentIndex = None
        else:
            currentUnit = self.store.units[currentIndex]
        self.emit(QtCore.SIGNAL("currentUnit"), currentUnit, currentIndex)

    def _getCurrentIndex(self):
        """return current index of current unit."""
        try:
            return self.filteredList[self._unitpointer]
        except:
            # no current id found in list
            return -1

    def filterFuzzy(self, checked):
        """add/remove fuzzy to filter, and send filter signal.
        @param checked: True or False when Fuzzy checkbox is checked or unchecked.
        """
        if (checked):
            self.filter |= World.fuzzy
        else:
            self.filter &= ~World.fuzzy
        self.emitFiltered(self.filter)
        
    def filterTranslated(self, checked):
        """add/remove translated to filter, and send filter signal.
        @param checked: True or False when Translated checkbox is checked or unchecked."""
        if (checked):
            self.filter |= World.translated
        else:
            self.filter &= ~World.translated
        self.emitFiltered(self.filter)
        
    def filterUntranslated(self, checked):
        """add/remove untranslated to filter, and send filter signal.
        @param checked: True or False when Untranslated checkbox is checked or unchecked.
        """
        if (checked):
            self.filter |= World.untranslated
        else:
            self.filter &= ~World.untranslated
        self.emitFiltered(self.filter)

    def emitFiltered(self, filter):
        """send filtered list signal according to filter."""
        self.emitUpdateUnit()
        self.filteredList = []
        self.filter = filter
        if (self.store.units[0].isheader()):
            start = 1
        else:
            start = 0
        for i in range(start, len(self.store.units)):
            currentUnit = self.store.units[i]
            # add unit to filteredList if it is in the filter
            if (self.filter & currentUnit.x_editor_state):
                self.filteredList.append(i)
        self.emit(QtCore.SIGNAL("filteredList"), self.filteredList, filter)
        self._unitpointer = 0
        self.emitCurrentUnit()
    
    def emitUpdateUnit(self):
        """emit "updateUnit" signal."""
        currentIndex = self._getCurrentIndex()
        if (self._unitpointer == None) or (currentIndex > len(self.store.units)):
            return
        self.emit(QtCore.SIGNAL("updateUnit"))

    def headerData(self):
        """@return Header comment and Header dictonary"""
        if (not isinstance(self.store, poheader.poheader)):
            return (None, None)

        header = self.store.header() 
        if header:
            headerDic = self.store.parseheader()
            return (header.getnotes("translator"), headerDic)
        else:
            return ("", {})

    def makeNewHeader(self, headerDic):
          """receive headerDic as dictionary, and return header as string"""
          #TODO: move to world
          self.store.x_generator = World.settingOrg + ' ' + World.settingApp + ' ' + World.settingVer
          return self.store.makeheaderdict(**headerDic)
          
    def updateNewHeader(self, othercomments, headerDic):
        """will update header"""
        header = self.store.header()
        if (header):
            header.removenotes()
            header.addnote(str(othercomments))
            self.store.updateheader(add=True, **headerDic)

    def previous(self):
        """move to previous unit inside the filtered list."""
        if self._unitpointer > 0:
            self.emitUpdateUnit()
            self._unitpointer -= 1
            self.emitCurrentUnit()
        
    def next(self):
        """move to next unit inside the filtered list."""
        if self._unitpointer < len(self.filteredList):
            if (not self.emitUpdateUnit()):
                self._unitpointer += 1
            self.emitCurrentUnit()
        
    def first(self):
        """move to first unit of the filtered list."""
        self.emitUpdateUnit()
        self._unitpointer = 0
        self.emitCurrentUnit()
        
    def last(self):
        """move to last unit of the filtered list."""
        self.emitUpdateUnit()
        self._unitpointer = len(self.filteredList) - 1
        self.emitCurrentUnit()

    def saveStoreToFile(self, fileName):
        """
        save the temporary store into a file.
        @param fileName: String type
        """
        self.emitUpdateUnit()
        if (World.settings.value("headerAuto", QtCore.QVariant(True)).toBool()):
            self.emit(QtCore.SIGNAL("headerAuto"))
        self.store.savefile(fileName)
        self._modified = False
        self.emit(QtCore.SIGNAL("savedAlready"), False) 

    def modified(self):
        """
        @return bool: True or False if current unit is modified or not modified.
        """
        self.emitUpdateUnit()
        return self._modified
    
    def setComment(self, comment):
        """set the comment to the current unit.
        @param comment: QString type
        """
        currentIndex = self._getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        currentUnit.removenotes()
        currentUnit.addnote(unicode(comment))
        self._modified = True
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit.
        @param target: QString type"""
        currentIndex = self._getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        translatedState = currentUnit.istranslated()
        # update target for current unit
        currentUnit.target = unicode(target)
        if (currentUnit.target):
            self.status.markTranslated(currentUnit, True)
        else:
            self.status.markTranslated(currentUnit, False)
        self._modified = True
        self.emitStatus()

    def setCurrentUnit(self, currentIndex):
        """adjust the unitpointer with currentIndex, and send currentUnit signal.
        @param currentIndex: current unit's index inside the units."""
        self.emitUpdateUnit()
        try:
            self._unitpointer = self.filteredList.index(currentIndex)
        except ValueError:
            self._unitpointer = -1
        self.emitCurrentUnit()
   
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit."""
        self.emitUpdateUnit()
        currentIndex = self._getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        if (currentUnit.x_editor_state & World.fuzzy):
            self.status.markFuzzy(currentUnit, False)
        elif (currentUnit.x_editor_state & World.translated):
            self.status.markFuzzy(currentUnit, True)
        else:
            return
        self._modified = True
        self.emitCurrentUnit()
        self.emitStatus()
    
    def initSearch(self, searchString, searchableText, matchCase):
        """initilize the needed variables for searching.
        @param searchString: string to search for.
        @param searchableText: text fields to search through.
        @param matchCase: bool indicates case sensitive condition."""
        self.searchPointer = self._unitpointer
        self.currentTextField = 0
        self.foundPosition = -1
        self.searchString = str(searchString)
        self.searchableText = searchableText
        self.matchCase = matchCase
        if (not matchCase):
            self.searchString = self.searchString.lower()

    def searchNext(self):
        """search forward through the text fields."""
        while (self.searchPointer < len(self.filteredList)):
            unitString = self._getUnitString()
            self.foundPosition = unitString.find(self.searchString, self.foundPosition + 1)
            # found in current textField
            if (self.foundPosition >= 0):
                self._searchFound()
                return True
                #break
            else:
                # next textField
                if (self.currentTextField < len(self.searchableText) - 1):
                    self.currentTextField += 1
                    continue
                # next unit
                else:
                    self.currentTextField = 0
                    self.searchPointer += 1
        else:
            # exhausted
            self._searchNotFound()
            self.emit(QtCore.SIGNAL("generalInfo"), "Search has reached end of document")
            self.searchPointer = len(self.filteredList) - 1

    def searchPrevious(self):
        """search backward through the text fields."""
        while (self.searchPointer >= 0):
            unitString = self._getUnitString()
            self.foundPosition = unitString.rfind(self.searchString, 0, self.foundPosition)
            # found in current textField
            if (self.foundPosition >= 0):
                self._searchFound()
                break
            else:
                # previous textField
                if (self.currentTextField > 0):
                    self.currentTextField -= 1
                    unitString = self._getUnitString()
                    self.foundPosition = len(unitString)
                    continue
                # previous unit
                else:
                    self.currentTextField = len(self.searchableText) - 1
                    self.searchPointer -= 1
                unitString = self._getUnitString()
                self.foundPosition = len(unitString)
        else:
            # exhausted
            self._searchNotFound()
            self.emit(QtCore.SIGNAL("generalInfo"), "Search has reached start of document")
    
    def replace(self, replacedText):
        """replace the found text in the text fields.
        @param replacedText: text to replace."""
        self.foundPosition = -1
        if self.searchNext():
            textField = self.searchableText[self.currentTextField]
            self.emit(QtCore.SIGNAL("replaceText"), \
                textField, \
                self.foundPosition, \
                len(unicode(self.searchString)), \
                replacedText)

    def replaceAll(self, replacedText):
        """replace the found text in the text fields through out the units.
        @param replacedText: text to replace."""
        self.searchPointer = 0
        self.foundPosition = -1
        for i in self.filteredList:
            if self.searchNext():
                textField = self.searchableText[self.currentTextField]
                self.emit(QtCore.SIGNAL("replaceText"), \
                    textField, \
                    self.foundPosition, \
                    len(unicode(self.searchString)), \
                    replacedText)
        
    def _getUnitString(self):
        """@return: the string of current text field."""
        textField = self.searchableText[self.currentTextField]
        unitIndex = self.filteredList[self.searchPointer]
        if (textField == World.source):
            unitString = self.store.units[unitIndex].source
        elif (textField == World.target):
            unitString = self.store.units[unitIndex].target
        elif (textField == World.comment):
            unitString = self.store.units[unitIndex].getnotes()
        else:
            unitString = ""
        if (not self.matchCase):
            unitString = unitString.lower()
        return unitString

    def _searchFound(self):
        """emit searchResult signal with text field, position, and length."""
        self.emitUpdateUnit()
        self._unitpointer = self.searchPointer
        self.emitCurrentUnit()
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), textField, self.foundPosition, len(unicode(self.searchString)))
        self.emit(QtCore.SIGNAL("generalInfo"), "")

    def _searchNotFound(self):
        """emit searchResult signal with text field, position, and length."""
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), textField, None, None)
