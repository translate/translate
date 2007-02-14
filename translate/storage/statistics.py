#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007 Zuza Software Foundation
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

"""Module to provide statistics and related functionality.

@organization: Zuza Software Foundation
@copyright: 2007 Zuza Software Foundation
@license: U{GPL <http://www.fsf.org/licensing/licenses/gpl.html>}
"""

from translate import lang
from translate.lang import factory

class Statistics(object):
    """Manages statistics for storage objects."""

    def __init__(self):
        self.sourcelanguage = 'en'
        self.targetlanguage = 'en'
        self.language = lang.factory.getlanguage(self.sourcelanguage)
        self.stats = {}

    def fuzzy_units(self):
        count = 0
        for unit in self.getunits():
            if unit.isfuzzy():
                count += 1
        return count

    def translated_units(self):
        """Return a list of translated units."""

        translated = []
        units = self.getunits()
        for unit in units:
            if unit.istranslated():
                translated.append(unit)
        return translated

    def translated_unitcount(self):
        """Returns the number of translated units."""

        translated_unitcount = len(self.translated_units())
        return translated_unitcount

    def untranslated_units(self):
        """Return a list of untranslated units."""

        untranslated = []
        units = self.getunits()
        for unit in units:
            if not unit.istranslated():
                untranslated.append(unit)
        return untranslated

    def untranslated_unitcount(self):
        """Returns the number of untranslated units."""

        return len(self.untranslated_units())

    def getunits(self):
        """Returns a list of all units in this object."""
        return []

    def get_source_text(self, units):
        """Joins the unit source strings in a single string of text."""
        source_text = ""
        for unit in units:
            source_text += unit.source + "\n"
            plurals = getattr(unit.source, "strings")
            if plurals:
                source_text += "\n".join(plurals[1:])
        return source_text

    def wordcount(self, text):
        """Returns the number of words in the given text."""
        return len(self.language.words(text))

    def source_wordcount(self):
        """Returns the number of words in the source text."""
        source_text = self.get_source_text(self.getunits())
        return self.wordcount(source_text)

    def translated_wordcount(self):
        """Returns the number of translated words in this object."""

        text = self.get_source_text(self.translated_units())
        return self.wordcount(text)

    def untranslated_wordcount(self):
        """Returns the number of untranslated words in this object."""

        text = self.get_source_text(self.untranslated_units())
        return self.wordcount(text)
