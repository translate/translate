#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)
#

from PyQt4 import QtCore, QtGui
from translate.storage import factory
from translate.storage import xliff
from translate.tools import pocount

class Operator(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._modified = False
        self._saveDone = False
        self._unitpointer = None
        
        # filter flags
        self.FUZZY = 2
        self.TRANSLATED = 4
        self.UNTRANSLATED = 8
        self.filter = self.FUZZY + self.TRANSLATED + self.UNTRANSLATED

    def getUnits(self, fileName):
        self.store = factory.getobject(fileName)

        # get status for units       
        self.numFuzzy = len(pocount.fuzzymessages(self.store.units))
        self.numTranslated = len(pocount.translatedmessages(self.store.units))
        self.numUntranslated = len(pocount.untranslatedmessages(self.store.units))
        self.numTotal = self.numTranslated + self.numUntranslated
        self.emitCurrentStatus()

####        fileNode = self.store.getfilenode(fileName)
##        xliffHeader = self.store.getheadernode(fileNode)
##        header = self.store.header(xliffHeader)

        header = self.store.units[0].isheader()
##        self.filteredList = range(len(self.store.units))[header:]
##        self.emit(QtCore.SIGNAL("newUnits"), self.store.units, self.filteredList)
##        header = {"charset":"CHARSET", "encoding":"ENCODING", "project_id_version":None, "pot_creation_date":None, "po_revision_date":None, "last_translator":None, "language_team":None, "mime_version":None, "plural_forms":None, "report_msgid_bugs_to":None}
##        poHeader = self.store.makeheader(charset="CHARSET", encoding="ENCODING", project_id_version=None, pot_creation_date=None, po_revision_date=None, last_translator=None, language_team=None, mime_version=None, plural_forms=None, report_msgid_bugs_to=None)
        
        self.emit(QtCore.SIGNAL("newUnits"), self.store.units)
        self.filteredList = range(len(self.store.units))
        # hide first unit if it's header
        if (header):
            self.hideUnit(0)
        # set to first unit pointer
        self._unitpointer = 0
        self.emitCurrentUnit()
        # set color for fuzzy unit only
##        fuzzyUnits = pocount.fuzzymessages(self.store.units)
##        for i in fuzzyUnits:
##            id = self.store.units.index(i)
##            self.emit(QtCore.SIGNAL("setColor"), id, self.FUZZY)


    def updateNewHeader(self, header):
##        poHeader = self.store.makeheader(header)
        self.store.updateheader(header)
##        print self.store.header()
        
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
        
        currentId = self.getCurrentId()
        currentUnit = self.store.units[currentId]
        if (currentId == -1):
            self.emit(QtCore.SIGNAL("currentUnit"), None)
        else:
            self.emit(QtCore.SIGNAL("currentUnit"), currentUnit)
            self.emit(QtCore.SIGNAL("currentId"), currentId)

    def getCurrentId(self):
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
        if (checked) and (not self.filter & self.FUZZY):
            self.filter += self.FUZZY
        elif (not checked) and (self.filter & self.FUZZY):
            self.filter -= self.FUZZY
        self.emitFiltered(self.filter)
        
    def filterTranslated(self, checked):
        """add/remove translated to filter, and send filter signal."""
        if (checked) and (not self.filter & self.TRANSLATED):
            self.filter += self.TRANSLATED
        elif (not checked) and (self.filter & self.TRANSLATED):
            self.filter -= self.TRANSLATED
        self.emitFiltered(self.filter)
        
    def filterUntranslated(self, checked):
        """add/remove untranslated to filter, and send filter signal."""
        if (checked):
            self.filter = self.filter | self.UNTRANSLATED
        elif (self.filter & self.UNTRANSLATED):
            self.filter -= self.UNTRANSLATED
        self.emitFiltered(self.filter)

    def emitFiltered(self, filter):
        """send filtered list signal according to filter."""
        #pocount.fuzzymessages(self.store.units)
        self.emitUpdateUnit()
        self.filteredList = []
        self.filter = filter
        header = self.store.units[0].isheader()
        for i in range(header, len(self.store.units)):
            currentUnit = self.store.units[i]
            # get the unit state
            unitState = 0
            if currentUnit.isfuzzy():
                unitState += self.FUZZY
            if currentUnit.istranslated():
                unitState += self.TRANSLATED
            else:
                unitState += self.UNTRANSLATED
            # add unit to filteredList if it is in the filter
            if (self.filter & unitState):
                self.filteredList.append(i)
        self.emit(QtCore.SIGNAL("filteredList"), self.filteredList)
        self._unitpointer = 0
        self.emitCurrentUnit()
    
    def emitUpdateUnit(self):
        """send updateUnit, setColor, and hideUnit signal."""
        currentId = self.getCurrentId()
        if (self._unitpointer == None) or (currentId > len(self.store.units)):
            return
        self.emit(QtCore.SIGNAL("updateUnit"))
        currentUnit = self.store.units[currentId]
        # get the unit state
        unitState = 0
        if currentUnit.isfuzzy():
            unitState += self.FUZZY
        if currentUnit.istranslated():
            unitState += self.TRANSLATED
        else:
            unitState += self.UNTRANSLATED
        # set color for current unit
        self.emit(QtCore.SIGNAL("setColor"), currentId, unitState)        
        # hide unit if it is not in the filter
        if (self.filter) and not (self.filter & unitState):
            self.hideUnit(currentId)
            # tell next button not to advance another step
            return True

    def emitOtherComments(self):
        """sending comment of Header"""
        self.emit(QtCore.SIGNAL("otherComments"),self.store.units[0].othercomments)
        
    def emitHeader(self, fileName):
        """sending Header """        
        self.store = factory.getobject(fileName)
        self.emit(QtCore.SIGNAL("header"),self.store.units[0].target)
##        if (callable(getattr(self.store, "header", None))):
        
##            self.emit(QtCore.SIGNAL("header"),self.store.header())
      
##        except:
##            pass

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
        currentId = self.getCurrentId()
        currentUnit = self.store.units[currentId]
        currentUnit.removenotes()
        currentUnit.addnote(unicode(comment))
        self._modified = True
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit."""
        currentId = self.getCurrentId()
        currentUnit = self.store.units[currentId]
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
            self.numFuzzy -= 1
            currentUnit.markfuzzy(False)
        # calculate number of translated units
        if (translatedState != currentUnit.istranslated()):
            self.numTranslated += (1 - (int(translatedState)*2))
        self._modified = True
        self.emitCurrentStatus()

    def setCurrentUnit(self, currentId):
        """adjust the unitpointer with currentId, and send currentUnit signal."""
        self.emitUpdateUnit()
        try:
            self._unitpointer = self.filteredList.index(currentId)
        except ValueError:
            self._unitpointer = -1
        self.emitCurrentUnit()
   
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit."""
        self.emitUpdateUnit()
        currentId = self.getCurrentId()
        currentUnit = self.store.units[currentId]
        # skip if unit is not yet translated
        if (not currentUnit.istranslated()):
            return
        if (currentUnit.isfuzzy()):
            self.store.units[currentId].markfuzzy(False)
            self.numFuzzy -= 1
        else:
            self.store.units[currentId].markfuzzy(True)
            self.numFuzzy += 1
        self._modified = True
        self.emitUpdateUnit()
        self.emitCurrentStatus()
    
    def emitCurrentStatus(self):
        """send currentStatus signal."""
        self.numUntranslated = self.numTotal - self.numTranslated
        status = "Total: "+ str(self.numTotal) + "  |  Fuzzy: " +  str(self.numFuzzy) + "  |  Translated: " +  str(self.numTranslated) + "  |  Untranslated: " + str(self.numUntranslated)
        self.emit(QtCore.SIGNAL("currentStatus"), ' ' + status + ' ')
    
    def setSearchOptions(self, options):
        """set location to search, direction, matchcase, and searching text"""
        self._sourcesearch = options[0]
        self._targetsearch = options[1]
        self._commentsearch = options[2]
        self._matchcase = options[3]
        self._forward = options[4]
        self._text = options[5]

    def startSearch(self, options):
        """set options to start searching when input"""
        self._searchFound = False
        self._cycled = False        
        self._insource = True
        self._incomment = False
        self._intarget = False                
        self.setSearchOptions(options)
        if (self._forward):
            self._offset = -1
            self.searchNext(options)
        else:
            self._offset = 0
            self.searchPrevious(options)

    def searchNext(self, options): 
        self.setSearchOptions(options)
        unitpointer = self._unitpointer
        startingpoint = self._unitpointer
        while (unitpointer != None and (unitpointer < len(self.filteredList) and unitpointer > -1)):
            unitpointer = self.search(self._offset + 1, unitpointer)
            if ( unitpointer >  len(self.filteredList) - 1):
                unitpointer = 0
                self._cycled = True
            if (unitpointer == startingpoint and self._cycled and not self._searchFound):
                self.emitSearchNotFound()
                break
            
    def searchPrevious(self, options):        
        self.setSearchOptions(options)
        unitpointer = self._unitpointer
        startingpoint = self._unitpointer        
        if (self._offset == 0):
            if (self._unitpointer != 0):
                if (self._insource):
                    unitpointer = self._unitpointer - 1
                self.setFlagsPrevious()
            else:
                if (not self._insource):
                    self.setFlagsPrevious()
                else:
                    unitpointer = len(self.filteredList) - 1
        
        while (unitpointer != None and (unitpointer < len(self.filteredList) and unitpointer > -1)):            
            unitpointer = self.search(self._offset - 1, unitpointer)            
            if ( unitpointer < 0 and unitpointer != None):                
                unitpointer =   len(self.filteredList) - 1
                self._cycled = True
            if (unitpointer == startingpoint and self._cycled and not self._searchFound):
                self.emitSearchNotFound()
                break
            
    def search(self, offset, unitpointer):
        temp = None
        if (self.filteredList):
            searchString = ''
            if (self._sourcesearch and self._insource):
                searchString = self.store.units[self.filteredList[unitpointer]].source

            if (self._commentsearch and self._incomment):
                searchString = self.store.units[self.filteredList[unitpointer]].getnotes()

            if (self._targetsearch and self._intarget):                
                searchString = self.store.units[self.filteredList[unitpointer]].target

            temp = self.searchedIndex(offset, searchString)
        # when found in source, comment or target, it will emit signal
        # in order to go to highlight place and put highlight.
        if (temp != -1 and temp != None):
            self._searchFound = True
            self._offset = temp
            self._unitpointer = unitpointer
            if (self._insource):
                self.emitFoundInSource()
            if (self._incomment):
                self.emitFoundInComment()
            if (self._intarget):
                self.emitFoundInTarget()
            return None
        
        # when search not found, it will decrease/increase unit depending on search previous or next
        if (temp == -1 or temp == None):
            if (self._forward):                
                if (self._intarget):
                    unitpointer += 1                    
                self._offset = -1
                self.setFlagsNext()
            else:
                if (self._insource):
                    unitpointer -= 1                    
                self.setFlagsPrevious()
                self._offset = 0
            return unitpointer
            
    def setFlagsPrevious(self):        
        if (self._intarget):
            self._incomment = True
            self._intarget = False                  
            self._insource = False
        elif (self._incomment):                        
            self._insource = True
            self._incomment = False
            self._intarget = False
        else:     
            self._intarget = True
            self._incomment = False
            self._insource = False

    def setFlagsNext(self):
        if (self._insource):
            self._incomment = True
            self._insource = False
            self._intarget = False
        elif (self._incomment):          
            self._intarget = True
            self._insource = False
            self._incomment = False
        else:
            self._insource = True
            self._incomment = False
            self._intarget = False

    def searchedIndex(self, offset, stringofunit):
        """get string that it will be searched in, and position to search from"""
        if (self._matchcase):
            regexp = QtCore.QRegExp(self._text)
        else:
            regexp = QtCore.QRegExp(self._text, QtCore.Qt.CaseInsensitive)

        if (self._forward):
            temp = regexp.indexIn(stringofunit, offset)
        else:
            temp = regexp. lastIndexIn(stringofunit, offset)
        self._matchlength = regexp.matchedLength()
        return temp 
            
    def emitFoundInSource(self):
        """emit signal foundInSource with the a list of position the search found, and length in source"""
        self.emitCurrentUnit()
        self.emit(QtCore.SIGNAL("foundInSource"), [self._offset, self._matchlength])
    
    def emitFoundInComment(self):
        """emit signal foundInComment with the a list of position the search found, and length in comment"""
        self.emitCurrentUnit()
        self.emit(QtCore.SIGNAL("foundInComment"), [self._offset, self._matchlength])
    
    def emitFoundInTarget(self):
        """emit signal foundInTarget with the a list of position the search found, and length to highlight in target"""
        self.emitCurrentUnit()
        self.emit(QtCore.SIGNAL("foundInTarget"), [self._offset, self._matchlength])

    def emitSearchNotFound(self):
        """emit signal search not found in order to unhighlight"""
        self.emit(QtCore.SIGNAL("clearHighLight"))
        self.emit(QtCore.SIGNAL("searchNotFound"), "search not found")    
    
