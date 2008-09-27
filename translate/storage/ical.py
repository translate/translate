#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007-2008 Zuza Software Foundation
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

"""Class that manages iCalender files for translation


"""
from translate.storage import base
from StringIO import StringIO
import re
import vobject


class icalunit(base.TranslationUnit):
    """An ical entry that is translatable"""
    def __init__(self, source=None, encoding="UTF-8"):
        self.location = ""
        if source:
            self.source = source
        super(icalunit, self).__init__(source)

    def addlocation(self, location):
        self.location = location

    def getlocations(self):
        return [self.location]

class icalfile(base.TranslationStore):
    """An ical file"""
    UnitClass = icalunit
    def __init__(self, inputfile=None, unitclass=icalunit):
        """construct an ical file, optionally reading in from inputfile."""
        self.UnitClass = unitclass
        base.TranslationStore.__init__(self, unitclass=unitclass)
        self.units = []
        self.filename = ''
        self._icalfile = None
        if inputfile is not None:
            self.parse(inputfile)

    def __str__(self):
        _outicalfile = self._icalfile
        for unit in self.units:
            for location in unit.getlocations():
                match = re.match('\\[(?P<uid>.+)\\](?P<property>.+)', location)
                for component in self._icalfile.components():
                    if component.name != "VEVENT":
                        continue
                    if component.uid.value != match.groupdict()['uid']:
                        continue
                    for property in component.getChildren():
                        if property.name == match.groupdict()['property']:
                            property.value = unit.target
                            
        if _outicalfile:
            return str(_outicalfile.serialize())
        else:
            return ""

    def parse(self, input):
        """parse the given file or file source string"""
        if hasattr(input, 'name'):
            self.filename = input.name
        elif not getattr(self, 'filename', ''):
            self.filename = ''
        if hasattr(input, "read"):
            inisrc = input.read()
            input.close()
            input = inisrc
        if isinstance(input, str):
            input = StringIO(input)
            self._icalfile = vobject.readComponents(input).next()
        else:
            self._icalfile = vobject.readComponents(open(input)).next()
        for component in self._icalfile.components():
            if component.name == "VEVENT":
                for property in component.getChildren():
                    if property.name in ('SUMMARY', 'DESCRIPTION', 'COMMENT', 'LOCATION'):
                        newunit = self.addsourceunit(property.value)
                        newunit.addnote("Start date: %s" % component.dtstart.value)
                        newunit.addlocation("[%s]%s" % (component.uid.value, property.name))
