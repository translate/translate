 #!/usr/bin/python
# -*- coding: utf8 -*-
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
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
# This module is working on Operator.

from PyQt4 import QtCore, QtGui
from translate.storage import factory
from translate.storage import po
from translate.misc import quote
from translate.storage import poheader
from translate.storage import xliff
import pootling.modules.World as World
from pootling.modules.Status import Status
from pootling.modules.pickleTM import pickleTM
import os, sys
import __version__


class Operator(QtCore.QObject):
    """
    Operates on the internal datastructure.
    The class loads and saves files and navigates in the data.
    Provides means for searching and filtering.
    
    @signal currentStatus(string): emitted with the new status message
    @signal newUnits(store.units): emitted with the new units
    @signal currentUnit(unit): emitted with the current unit
    @signal updateUnit(): emitted when the views should update the unitÂ´s data
    @signal toggleFirstLastUnit(atFirst, atLast): emitted to allow dis/enable of actions
    @signal filterChanged(filter, lenFilter): emitted when the filter was changed
    @signal readyForSave(False): emitted when a file was saved
    """
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self.currentUnitIndex = 0
        self.filteredList = []
        self.filter = None
        TMpreference = World.settings.value("TMpreference").toInt()[0]
        self.setTMLookupStatus(TMpreference)
        GlossaryPreference = World.settings.value("GlossaryPreference").toInt()[0]
        self.setTermLookupStatus(GlossaryPreference)
        self.isCpResult = False

    def getUnits(self, fileName):
        """reading a file into the internal datastructure.
        @param fileName: the file to open, either a string or a file object"""
        if (not os.path.exists(fileName)):
            QtGui.QMessageBox.critical(None, 'Error', fileName  + '\n' + 'The file doesn\'t exist.')
            return
        try:
            store = factory.getobject(fileName)
        except Exception, e:
            QtGui.QMessageBox.critical(None, 'Error', 'Error while trying to read file ' + fileName  + '\n' + str(e))
            return
        self.setNewStore(store)
        self.emit(QtCore.SIGNAL("fileIsOK"), fileName)
      
    def setNewStore(self, store):
        """ setup the oparator with a new storage
        @param store: the new storage class"""
        self.store = store
        # filter flags
        self.filter = World.filterAll
        # get status for units
        self.status = Status(self.store)
        self.emitStatus()

        self.filteredList = []
        self.currentUnitIndex = 0
        i = 0
        for unit in self.store.units:
            unit.x_editor_state = self.status.getStatus(unit)
            if (self.filter & unit.x_editor_state):
                unit.x_editor_filterIndex = len(self.filteredList)
                self.filteredList.append(unit)
            i += 1
        self.emitNewUnits()
        self.setUnitFromPosition(0)
        self.setModified(False)

    def emitNewUnits(self):
        self.emit(QtCore.SIGNAL("newUnits"), self.filteredList)
        
    def emitStatus(self):
        '''show total of messages in a file, fuzzy, translated messages and untranslate  messages which are not fuzzy.
        
        '''
        self.emit(QtCore.SIGNAL("currentStatus"), self.status.statusString())
    
    def emitUnit(self, unit):
        """send "currentUnit" signal with unit.
        @param unit: class unit."""
        if (hasattr(unit, "x_editor_filterIndex")):
            self.currentUnitIndex = unit.x_editor_filterIndex
            self.searchPointer = unit.x_editor_filterIndex
        self.emit(QtCore.SIGNAL("currentUnit"), unit)
    
    def getCurrentUnit(self):
        """return the current unit"""
        return self.filteredList[self.currentUnitIndex]
    
    def filterFuzzy(self, checked):
        """add/remove fuzzy to filter, and send filter signal.
        @param checked: True or False when Fuzzy checkbox is checked or unchecked.
        """
        filter = self.filter
        if (checked):
            filter |= World.fuzzy
        elif (filter):
            filter &= ~World.fuzzy
        self.emitFiltered(filter)
    
    def filterTranslated(self, checked):
        """add/remove translated to filter, and send filter signal.
        @param checked: True or False when Translated checkbox is checked or unchecked."""
        filter = self.filter
        if (checked):
            filter |= World.translated
        elif (filter):
            filter &= ~World.translated
        self.emitFiltered(filter)
    
    def filterUntranslated(self, checked):
        """add/remove untranslated to filter, and send filter signal.
        @param checked: True or False when Untranslated checkbox is checked or unchecked.
        """
        filter = self.filter
        if (checked):
            filter |= World.untranslated
        elif (filter):
            filter &= ~World.untranslated
        self.emitFiltered(filter)
    
    def emitFiltered(self, filter):
        """send filtered list signal according to filter."""
        if (len(self.filteredList) > 0):
            unitBeforeFiltered = self.filteredList[self.currentUnitIndex]
        else:
            unitBeforeFiltered = None
        
        if (filter != self.filter):
            # build a new filteredList when only filter has changed.
            self.filter = filter
            self.filteredList = []
            for unit in self.store.units:
                if (self.filter & unit.x_editor_state):
                    unit.x_editor_filterIndex = len(self.filteredList)
                    self.filteredList.append(unit)
        self.emit(QtCore.SIGNAL("filterChanged"), filter, len(self.filteredList))
        if (unitBeforeFiltered) and (unitBeforeFiltered in self.filteredList):
            unit = unitBeforeFiltered
        elif (len(self.filteredList) > 0):
            unit = self.filteredList[0]
        else:
            unit = None
        self.emitUnit(unit)

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
          """Create a header with the information from headerDic.
          
          @param headerDic: a dictionary of arguments that are neccessary to form a header
          @return: a dictionary with the header items"""

          if (hasattr(self.store, "x_generator")):
            self.store.x_generator = World.settingApp + ' ' + __version__.ver
          if isinstance(self.store, poheader.poheader):
              self.store.updateheader(add=True, **headerDic)
              self.setModified(True)
              return self.store.makeheaderdict(**headerDic)
          else: return {}
          
    def updateNewHeader(self, othercomments, headerDic):
        """Will update the existing header.
        
        @param othercomments: The comment of header file
        @param headerDic: A header dictionary that have information about header
        """
        #TODO: need to make it work with xliff file
        if (not isinstance(self.store, poheader.poheader)):
            return {}
        
        header = self.store.header()
        if (header):
            header.removenotes()
            header.addnote(str(othercomments))
            #TODO this code is also in the library po.py, so we should combine it.
            header.msgid = ['""']
            headeritems = self.store.makeheaderdict(**headerDic)
            header.msgstr = ['""']
            for (key, value) in headeritems.items():
                header.msgstr.append(quote.quotestr("%s: %s\\n" % (key, value)))
        self.setModified(True)

    def saveStoreToFile(self, fileName):
        """
        save the temporary store into a file.
        @param fileName: String type
        """
        if (World.settings.value("headerAuto", QtCore.QVariant(True)).toBool()):
            self.emit(QtCore.SIGNAL("headerAuto"))
        
        try:
            if (fileName):
                self.store.savefile(fileName)
            else:
                self.store.save()
            self.setModified(False)
        except Exception, e:
            QtGui.QMessageBox.critical(None, 
                                    'Error', 
                                    'Error while trying to write file ' 
                                    + fileName  + 
                                    '\n' + str(e))
    
    def setComment(self, comment):
        """set the comment to the current unit, and emit current unit.
        @param comment: QString type"""
        if (self.currentUnitIndex < 0 or not self.filteredList):
            return
        unit = self.getCurrentUnit()
        unit.removenotes()
        unit.addnote(unicode(comment),'translator')
        self.emitUnit(unit)
        self.setModified(True)
    
    def setTarget(self, target):
        """set the target to the current unit, and emit current unit.
        @param target: Unicode sting type for single unit and list type for plural unit."""
        # if there is no translation unit in the view.
        if (self.currentUnitIndex < 0 or not self.filteredList):
            return
        unit = self.getCurrentUnit()
        # update target for current unit
        unit.settarget(target)
        #FIXME: this mark works single not plural unit.
        self.status.markTranslated(unit, (unit.target and True or False))
        self.emitUnit(unit)
        self.emitStatus()
        self.setModified(True)
    
    def setUnitFromPosition(self, position):
        """build a unit from position and call emitUnit.
        @param position: position inside the filtered list."""
        if (position < len(self.filteredList) and position >= 0):
            unit = self.filteredList[position]
            self.emitUnit(unit)
    
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit."""
        if (self.currentUnitIndex < 0):
            return
        unit = self.getCurrentUnit()
        if (unit.x_editor_state & World.fuzzy):
            self.status.markFuzzy(unit, False)
        elif (unit.x_editor_state & World.translated):
            self.status.markFuzzy(unit, True)
        else:
            return
        self.emitUnit(unit)
        self.emitStatus()
        self.setModified(True)
    
    def initSearch(self, searchString, searchableText, matchCase):
        """initilize the needed variables for searching.
        @param searchString: string to search for.
        @param searchableText: text fields to search through.
        @param matchCase: bool indicates case sensitive condition."""
        self.currentTextField = 0
        self.foundPosition = -1
        self.searchString = unicode(searchString)
        self.searchableText = searchableText
        self.matchCase = matchCase
        if (not matchCase):
            self.searchString = self.searchString.lower()

    def searchNext(self):
        """search forward through the text fields."""
        if (not hasattr(self, "searchPointer")):
            return
        oldSearchPointer = self.searchPointer
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
            self.searchPointer = oldSearchPointer

    def searchPrevious(self):
        """search backward through the text fields."""
        if (not hasattr(self, "searchPointer")):
            return
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
        self.foundPosition = -1
        while self.searchNext():
            textField = self.searchableText[self.currentTextField]
            self.emit(QtCore.SIGNAL("replaceText"), \
                textField, \
                self.foundPosition, \
                len(unicode(self.searchString)), \
                replacedText)
        
    def _getUnitString(self):
        """@return: the string of current text field."""
        if (self.searchPointer >= len(self.filteredList) or self.searchPointer < 0):
            return ""
        textField = self.searchableText[self.currentTextField]
        if (textField == World.source):
            unitString = self.filteredList[self.searchPointer].source
        elif (textField == World.target):
            unitString = self.filteredList[self.searchPointer].target
        elif (textField == World.comment):
            unitString = self.filteredList[self.searchPointer].getnotes()
        else:
            unitString = ""
        if (not self.matchCase):
            unitString = unitString.lower()
        return unitString

    def _searchFound(self):
        """emit searchResult signal with text field, position, and length."""
        self.setUnitFromPosition(self.searchPointer)
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), textField, self.foundPosition, len(unicode(self.searchString)))
        self.emit(QtCore.SIGNAL("generalInfo"), "")

    def _searchNotFound(self):
        """emit searchResult signal with text field, position, and length."""
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), textField, None, None)

    def setAfterfileClosed(self):
        self.store = None
        self.status = None
        self.filter = None
        self.filteredList = []
        self.emitNewUnits()
    
    def autoTranslate(self):
        '''
        get TM path and start lookup
        '''
        if (not self.filteredList):
            return
        self.lookupProcess(self.filteredList)
        
    def setMatcher(self, list):
        '''set matcher to new matcher'''
        if (list[0] == "TM"):
            self.matcher = list[1]
        else:
            self.termmatcher = list[1]
        
    def lookupProcess(self, units):
        '''process lookup translation from translation memory
        
        @param units: a unit or list of units
        '''
        
        # get matcher from when startup
        if (not hasattr(self, "matcher")):
            confFile = World.settings.fileName()
            self.pickleTM = pickleTM(str(confFile), "TM")
            self.matcher = self.pickleTM.getMatcher()
        
        if (not self.matcher):
            self.emit(QtCore.SIGNAL("noTM"), "Problem with translation memory, Build or Rebuild TM")
            return
        
        #for lookup a unit
        if (not isinstance(units, list)):
            if (units.isfuzzy() and self.ignoreFuzzyStatus):   # if ignore fuzzy strings is checked, ad units is fuzzy do nothing.
                return
            candidates = self.matcher.matches(units.source)
            return candidates
            
       #for autoTranslate all units
        for unit in units:
            if (unit.istranslated() or not unit.source or (unit.isfuzzy() and self.ignoreFuzzyStatus)):   # if ignore fuzzy strings is checked, ad units is fuzzy do nothing.
                continue
            candidates = self.matcher.matches(unit.source)
            # no condidates continue searching in next TM
            if (not candidates):
                continue
            self.setModified(True)
            # get the best candidates for targets in overview
            unit.settarget(candidates[0].target)
            #in XLiff, it is possible to have alternatives translation
            # TODO: add source original language and target language attribute
            if (isinstance(self.store, xliff.xlifffile)):
                for i in range(1, len(candidates)):
                    unit.addalttrans(candidates[i].target)
            self.status.markTranslated(unit, True)
            self.status.markFuzzy(unit, True)
        self.emitNewUnits()
        self.emitStatus()
        return
        
    def isCopyResult(self, bool):
        """Slot to recieve isCopyResult signal."""
        self.isCpResult = bool
        
    def lookupUnit(self):
        if (not self.filteredList):
            return
        if (self.isCpResult):
            self.isCpResult = False
            return
        unit = self.filteredList[self.currentUnitIndex]
        candidates = self.lookupProcess(unit)
        self.emit(QtCore.SIGNAL("candidates"), candidates)
    
    def setTMLookupStatus(self, TMprefrence):
        self.lookupUnitStatus = (TMprefrence & 1 and True or False)
        self.ignoreFuzzyStatus =  (TMprefrence & 2 and True or False)
        self.addtranslation =  (TMprefrence & 4 and True or False)
    
    def setTermLookupStatus(self, GlossaryPreference):
        self.AutoIdentTerm = (GlossaryPreference & 1 and True or False)
        self.ChangeTerm =  (GlossaryPreference & 2 and True or False)
        self.DetectTerm =  (GlossaryPreference & 8 and True or False)
        self.AddNewTerm =  (GlossaryPreference & 16 and True or False)
        self.SuggestTranslation =  (GlossaryPreference & 32 and True or False)
    
    def setModified(self, bool):
        self.modified = bool
        self.emit(QtCore.SIGNAL("readyForSave"), self.modified) 

    def getModified(self):
        return (hasattr(self, "modified") and self.modified or None)
    
    def lookupTerm(self):
        if (not self.filteredList):
            return
        
        # get glossary matcher from disk when startup
        if (not hasattr(self, "termmatcher")):
            confFile = World.settings.fileName()
            self.pickleterm = pickleTM(str(confFile), "Glossary")
            self.termmatcher = self.pickleterm.getMatcher()
        
        if (not self.termmatcher):
            self.emit(QtCore.SIGNAL("noTM"), "Problem with glossary, Build or Rebuild glossary")
            return
        unit = self.filteredList[self.currentUnitIndex]
        #TODO: split text by space
        words = unit.source.split(" ")
        for word in words:
            candidates = self.termmatcher.matches(word)
            foundPosition = unit.source.lower().find(candidates[0].source, 0)
            if (foundPosition):
                self.emit(QtCore.SIGNAL("glossaryResult"), foundPosition, len(unicode(candidates[0].source)))
    
    def lookupTranslation(self):
        '''lookup text translation or text terminologies in glossary.
        
        '''
        if (self.lookupUnitStatus):
            self.lookupUnit()
        if (self.AutoIdentTerm):
            self.lookupTerm()
