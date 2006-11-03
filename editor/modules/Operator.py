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
from translate.storage import xliff
from modules.World import World
from modules.Status import Status

class Operator(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._modified = False
        self._saveDone = False
        self._unitpointer = None
        # global variables
        self.world = World()
        # filter flags
        self.filter = self.world.fuzzy + self.world.translated + self.world.untranslated
        # search function's variables
        self.searchReached = False
        self.foundPosition = -1
        self.lastI = 0

    def getUnits(self, fileName):
        self.fileName = fileName
        self.store = factory.getobject(fileName)
        # get status for units
        self.status = Status(self.store.units)
        self.emitStatus()

####        fileNode = self.store.getfilenode(fileName)
##        xliffHeader = self.store.getheadernode(fileNode)
##        header = self.store.header(xliffHeader)
 
        header = self.store.units[0].isheader()
##        self.filteredList = range(len(self.store.units))[header:]
##        self.emit(QtCore.SIGNAL("newUnits"), self.store.units, self.filteredList)
        
        unitsState = []
        for unit in self.store.units:
            currentState = self.status.getStatus(unit)
            unitsState.append(currentState)
        
        self.emit(QtCore.SIGNAL("newUnits"), self.store.units, unitsState)
        self.filteredList = range(len(self.store.units))
        # hide first unit if it's header
        if (header):
            self.hideUnit(0)
        # set to first unit pointer
        self._unitpointer = 0
        self.emitCurrentUnit()
##        # set color for fuzzy unit only
##        fuzzyUnits = pocount.fuzzymessages(self.store.units)
##        for i in fuzzyUnits:
##            id = self.store.units.index(i)
##            self.emit(QtCore.SIGNAL("setColor"), id, self.world.fuzzy)


    def updateNewHeader(self, othercomments, headerDic):
          """will update header when ok button in Header Editor is clicked or auto Header is on and save is triggered"""
##          headerDic= po.poheader.parse(header)
          print type(headerDic), headerDic
          self.store.updateheader(self.store.units[0].target, True, headerDic)
##        print poHeader


    def emitStatus(self):
        self.emit(QtCore.SIGNAL("currentStatus"), self.status.statusString())
        

    def emitCurrentUnit(self):
        if (len(self.filteredList) <= 1):
            # less than one unit, disable all 4 navigation buttons
            self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), False, False)
        elif (self._unitpointer == 0):
            # first unit
            # toggleUnitButtons: enable first/prev, next/last
            self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), False, True)
            self.middleUnit = False
        elif (self._unitpointer == len(self.filteredList) - 1):
            # last unit
            self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), True, False)
            self.middleUnit = False
        elif (not self.middleUnit):
            # middle unit
            self.emit(QtCore.SIGNAL("toggleFirstLastUnit"), True, True)
            self.middleUnit = True
        
        # tell search it is not reached end or start of file.
        self.searchReached = False
        currentIndex = self.getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        currentState = self.status.getStatus(currentUnit)
        if (currentIndex == -1):
            self.emit(QtCore.SIGNAL("currentUnit"), None, None, None)
        else:
            self.emit(QtCore.SIGNAL("currentUnit"), currentUnit, currentIndex, currentState)

    def getCurrentIndex(self):
        try:
            return self.filteredList[self._unitpointer]
        except:
            # no current id found in list
            return -1

    def hideUnit(self, value):
        """remove unit inside filtered list, and send hideUnit signal."""
        try:
            self.filteredList.remove(value)
        except ValueError:
            pass
        self.emit(QtCore.SIGNAL("hideUnit"), value)
        
    def filterFuzzy(self, checked):
        """add/remove fuzzy to filter, and send filter signal."""
        if (checked) and (not self.filter & self.world.fuzzy):
            self.filter += self.world.fuzzy
        elif (not checked) and (self.filter & self.world.fuzzy):
            self.filter -= self.world.fuzzy
        print self.filter
        self.emitFiltered(self.filter)
        
    def filterTranslated(self, checked):
        """add/remove translated to filter, and send filter signal."""
        if (checked) and (not self.filter & self.world.translated):
            self.filter += self.world.translated
        elif (not checked) and (self.filter & self.world.translated):
            self.filter -= self.world.translated
        print self.filter
        self.emitFiltered(self.filter)
        
    def filterUntranslated(self, checked):
        """add/remove untranslated to filter, and send filter signal."""
        if (checked):
            self.filter = self.filter | self.world.untranslated
        elif (self.filter & self.world.untranslated):
            self.filter -= self.world.untranslated
        print self.filter
        self.emitFiltered(self.filter)

    def emitFiltered(self, filter):
        """send filtered list signal according to filter."""
        self.emitUpdateUnit()
        self.filteredList = []
        self.filter = filter
        header = self.store.units[0].isheader()
        for i in range(header, len(self.store.units)):
            currentUnit = self.store.units[i]
            # get the unit state
            unitState = 0
            if currentUnit.isfuzzy():
                unitState += self.world.fuzzy
            if currentUnit.istranslated():
                unitState += self.world.translated
            else:
                unitState += self.world.untranslated
            # add unit to filteredList if it is in the filter
            if (self.filter & unitState):
                self.filteredList.append(i)
        self.emit(QtCore.SIGNAL("filteredList"), self.filteredList)
        self._unitpointer = 0
        self.emitCurrentUnit()
    
    def emitUpdateUnit(self):
        """send updateUnit, setColor, and hideUnit signal."""
        currentIndex = self.getCurrentIndex()
        if (self._unitpointer == None) or (currentIndex > len(self.store.units)):
            return
        self.emit(QtCore.SIGNAL("updateUnit"))

##        currentUnit = self.store.units[currentIndex]
##        # get the unit state
##        unitState = 0
##        if currentUnit.isfuzzy():
##            unitState += self.world.fuzzy
##        if currentUnit.istranslated():
##            unitState += self.world.translated
##        else:
##            unitState += self.world.untranslated
##        # set color for current unit
##        self.emit(QtCore.SIGNAL("setColor"), currentIndex, unitState)
##        # hide unit if it is not in the filter
##        if (self.filter) and not (self.filter & unitState):
##            self.hideUnit(currentIndex)
##            # tell next button not to advance another step
##            return True

    def emitHeaderInfo(self):
        """sending Header and comment of Header"""
        headerDic= po.poheader.parse(self.store.units[0].target)
        self.emit(QtCore.SIGNAL("headerInfo"),self.store.units[0].othercomments,headerDic)
        
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
        self.emitUpdateUnit()
        self.store.savefile(fileName)
        self._saveDone = True
        self.emit(QtCore.SIGNAL("savedAlready"), False) 

    def modified(self):
        self.emitUpdateUnit()
        if self._saveDone:
            self._modified = False
            self._saveDone = False
        return self._modified
    
    def setComment(self, comment):
        """set the comment which is QString type to the current unit."""
        currentIndex = self.getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        currentUnit.removenotes()
        currentUnit.addnote(unicode(comment))
        self._modified = True
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit."""
        currentIndex = self.getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        translatedState = currentUnit.istranslated()
        # update target for current unit
        currentUnit.target = unicode(target)
        # marktranslated for xliff file
        if (currentUnit.target):
            try:
                currentUnit.marktranslated()
            except AttributeError:
                pass
        # unmark fuzzy is unit if it's previously fuzzy
        if (currentUnit.isfuzzy()):
            self.status.addNumFuzzy(-1)
            currentUnit.markfuzzy(False)
        # calculate number of translated units
        if (translatedState != currentUnit.istranslated()):
            self.status.addNumTranslated(1 - (int(translatedState)*2))
        self._modified = True
        self.emitStatus()

    def setCurrentUnit(self, currentIndex):
        """adjust the unitpointer with currentIndex, and send currentUnit signal."""
        self.emitUpdateUnit()
        try:
            self._unitpointer = self.filteredList.index(currentIndex)
        except ValueError:
            self._unitpointer = -1
        self.emitCurrentUnit()
   
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit."""
        self.emitUpdateUnit()
        currentIndex= self.getCurrentIndex()
        currentUnit = self.store.units[currentIndex]
        # skip if unit is not yet translated
        if (not currentUnit.istranslated()):
            return
        if (currentUnit.isfuzzy()):
            self.store.units[currentIndex].markfuzzy(False)
            self.status.addNumFuzzy(-1)
        else:
            self.store.units[currentIndex].markfuzzy(True)
            self.status.addNumFuzzy(1)
        self._modified = True
        self.emitUpdateUnit()
        self.emitStatus()
    
    def searchString(self, searchText, matchCase, searchDirection, container):
        """Search the whole units for searchText, when found emit searchResult signal."""
        # TODO: search in all fields, now work only in source
        # skip if no text to search for
        if (not searchText):
            return
        if (searchDirection == self.world.searchForward):
            direction = 1
        elif (searchDirection == self.world.searchBackward):
            direction = -1
        if (matchCase):
            regexp = QtCore.QRegExp(searchText)
        else:
            regexp = QtCore.QRegExp(searchText, QtCore.Qt.CaseInsensitive)
        startPoint = self._unitpointer
        if (self.searchReached):
            if (searchDirection == self.world.searchForward):
                startPoint = 0
            else:
                startPoint = len(self.filteredList) - 1
            self.searchReached = False
        while (startPoint >= 0) and (startPoint < len(self.filteredList)):
            unitIndex = self.filteredList[startPoint]
            # construct list of mainString
            mainStringList = []
            receiverList = []
            if (container & self.world.source):
                mainStringList.append(QtCore.QString(self.store.units[unitIndex].source))
                receiverList.append(self.world.source)
            if (container & self.world.target):
                mainStringList.append(QtCore.QString(self.store.units[unitIndex].target))
                receiverList.append(self.world.target)
            if (container & self.world.comment):
                mainStringList.append(QtCore.QString(self.store.units[unitIndex].getnotes()))
                receiverList.append(self.world.comment)
            
            for i in range(self.lastI, len(mainStringList)):
                mainString = mainStringList[i]            
                # get the index of string where searchText is found.
                if (searchDirection == self.world.searchForward):
                    self.foundPosition = regexp.indexIn(mainString, self.foundPosition + 1)
                elif (searchDirection == self.world.searchBackward):
                    firstFound = self.foundPosition
                    self.foundPosition = regexp.lastIndexIn(mainString, self.foundPosition - 1)
                    secondFound = self.foundPosition
                    # fix bug that it would go up one unit before, when search string found at pos 0
                    # if still find the same thing, assume it does not find.
                    if (firstFound == secondFound):
                        self.foundPosition = -1
                else:
                    self.foundPosition = regexp.lastIndexIn(mainString)
                # break "for" when found
                if (self.foundPosition >= 0):
                    self.lastI = i
                    foundLength = len(searchText)
                    # send current unit signal when found
                    self._unitpointer = startPoint
                    self.emitCurrentUnit()
                    self.emit(QtCore.SIGNAL("searchResult"), receiverList[i], self.foundPosition, foundLength)
                    self.emit(QtCore.SIGNAL("generalInfo"), "")
                    break
                else:
                    # search in new mainString starts with -1
                    self.foundPosition = -1
            else:
                # have searched in all containers
                self.lastI = 0
            # break "while" when found
            if (self.foundPosition >= 0):
                break
            # go to next/previous unit
            startPoint += direction
        else:
            if (searchDirection == self.world.searchBackward):
                message = self.tr("Search has reached the start of document.")
                self.searchReached = True
            else:
                message = self.tr("Search has reached the end of document.")
                self.searchReached = True
            self.emit(QtCore.SIGNAL("generalInfo"), message)
            
##            if (searchDirection == self.world.searchForward):
##                resumeRange = range(self.lastI, len(mainStringList))
##            else:
##                resumeRange = range(len(mainStringList) - 1, self.lastI - 1, -1)
##            # resume search from "lastI" and "self.foundPosition"
