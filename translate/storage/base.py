#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2006 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""base classes for storage interfaces"""

import pickle
from exceptions import NotImplementedError

def force_override(method, baseclass):
    """forces derived classes to override method"""
    if type(method.im_self) == type(baseclass):
        # then this is a classmethod and im_self is the actual class
        actualclass = method.im_self
    else:
        actualclass = method.im_class
    if actualclass != baseclass:
        raise NotImplementedError("%s does not reimplement %s as required by %s" % (actualclass.__name__, method.__name__, baseclass.__name__))

class TranslationUnit(object):
    def __init__(self, source):
        """Constructs a TranslationUnit containing the given source string"""
        self.source = source
        self.target = None
        self.notes = ""

    def __eq__(self, other):
        """Compares two TranslationUnits"""
        return self.source == other.source and self.target == other.target

    def settarget(self, target):
        """Sets the target string to the given value"""
        self.target = target
    
    def gettargetlen(self):
        """returns the length of the translation string, possible combining 
        plural forms"""
        length = len(self.target)
        strings = getattr(self.target, "strings", [])
        if strings:
            length += sum([len(pluralform) for pluralform in strings[1:]])
        return length

    def getlocations(self):
        """A list of source code locations. Shouldn't be implemented if the
        format doesn't support it."""
        return []
    
    def addlocation(self, location):
        """Add one location to the list of locations. Shouldn't be implemented
        if the format doesn't support it."""
        pass

    def addlocations(self, location):
        """Add a location or a list of locations. Most classes shouldn't need
        to implement this, but should rather implement addlocation()."""
        if isinstance(location, list):
            for item in location:
                self.addlocation(item)
        else:
            self.addlocation(location)

    def getnotes(self, origin=None):
        """Returns all notes about this unit. It will probably be freeform text
        or something reasonable that can be synthesised by the format. It should
        not include location comments (see getlocations)"""
        return getattr(self, "notes", "")

    def addnote(self, text, origin=None):
        """Adds a note (comment). 
        Origin specifies who/where the comment comes from.
        Origin can be one of the following text strings:
            - 'translator'
            - 'developer', 'programmer' or 'source code' (synonyms),
            - """
        if self.notes:
            self.notes += '\n'+text
        else:
            self.notes = text

    def removenotes(self):
        """Remove all the translator's notes."""
        self.notes = u''

    def markreviewneeded(self, needsreview=True, explanation=None):
        """Marks the unit to indicate whether it needs review. Adds an optional explanation as a note."""
        raise NotImplementedError

    def istranslated(self):
        """Indicates whether this unit is translated. This should be used 
        rather than deducing it from .target, to ensure that other classes can
        implement more functionality (as XLIFF does)."""
        return bool(self.target) and not self.isfuzzy()

    def isfuzzy(self):
        """Indicates whether this unit is fuzzy"""
        return False

    def isheader(self):
        return False

    def isreview(self):
        """Indicates whether this unit needs review."""
        raise NotImplementedError

    def isblank(self):
        """Used to see if this unit has no source or target string. This is 
        probably used more to find translatable units, and we might want to 
        move in that direction rather and get rid of this."""
        return not (self.source and self.target)

    def hasplural(self):
        """Tells whether or not this specific unit has plural strings."""
        #TODO: Reconsider
        return False

    def merge(self, otherunit, overwrite=False, comments=True):
        """do basic format agnostic merging"""
        if self.target == "" or overwrite:
            self.target = otherunit.target

    def buildfromunit(cls, unit):
        """build a native unit from a foreign unit, preserving as much as 
        possible information"""
        if type(unit) == cls and hasattr(unit, "copy") and iscallable(unit.copy):
            return unit.copy()
        newunit = cls(unit.source)
        newunit.target = unit.target
        newunit.markfuzzy(unit.isfuzzy())
        locations = unit.getlocations()
        if locations: newunit.addlocations(locations)
        notes = unit.getnotes()
        if notes: newunit.addnote(notes)
        return newunit
    buildfromunit = classmethod(buildfromunit)

class TranslationStore(object):
    """Base class for stores for multiple translation units of type UnitClass"""
    UnitClass = TranslationUnit

    def __init__(self, unitclass=None):
        """Constructs a blank TranslationStore"""
        self.units = []
        if unitclass:
            self.UnitClass = unitclass

    def addunit(self, unit):
        """Appends the given unit to the object's list of units."""
        self.units.append(unit)

    def addsourceunit(self, source):
        """Adds and returns a new unit with the given source string"""
        unit = self.UnitClass(source)
        self.addunit(unit)
        return unit

    def findunit(self, source):
        """Finds the unit with the given source string"""
        if len(getattr(self, "sourceindex", [])):
            if source in self.sourceindex:
                return self.sourceindex[source]
        else:
            for unit in self.units:
                if unit.source == source:
                    return unit
        return None

    def translate(self, source):
        unit = self.findunit(source)
        if unit and unit.target:
            return unit.target
        else:
            return None

    def makeindex(self):
        """Indexes the items in this store. At least .sourceindex should be usefull."""
        self.locationindex = {}
        self.sourceindex = {}
        for unit in self.units:
            self.sourceindex[unit.source] = unit
            if unit.hasplural():
                plural_source = unit.source.strings[1]
                self.sourceindex[plural_source] = unit
            for location in unit.getlocations():
                if location in self.locationindex:
                    # if sources aren't unique, don't use them
                    self.locationindex[location] = None
                else:
                    self.locationindex[location] = unit

    def __str__(self):
        """Converts to a string representation that can be parsed back using parse"""
        force_override(self.__str__, TranslationStore)
        return pickle.dumps(self)

    def isempty(self):
      """returns True if the object doesn't contain any translation units."""
      if len(self.units) == 0:
        return True
      # Skip the first unit if it is a header.
      if self.units[0].isheader():
        units = self.units[1:]
      else:
        units = self.units

      for unit in units:
        if not unit.isblank():
          return False
      return True

    def parsestring(cls, storestring):
        """Converts the string representation back to an object"""
        force_override(cls.parsestring, TranslationStore)
        return pickle.loads(storestring)
    parsestring = classmethod(parsestring)

    def savefile(self, storefile):
        """Writes the string representation to the given file (or filename)"""
        storestring = str(self)
        if isinstance(storefile, basestring):
            storefile = open(storefile, "w")
        storefile.write(storestring)
        storefile.close()

    def parsefile(cls, storefile):
        """Reads the given file (or opens the given filename) and parses back to an object"""
        if isinstance(storefile, basestring):
            storefile = open(storefile, "r")
        if "r" in getattr(storefile, "mode", "r"):
          storestring = storefile.read()
        else:
          storestring = ""
        return cls.parsestring(storestring)
    parsefile = classmethod(parsefile)

