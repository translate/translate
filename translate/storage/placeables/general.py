#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Contains general placeable implementations. That is placeables that does not
fit into any other sub-category.
"""

import re

__all__ = ['AltAttrPlaceable', 'XMLEntityPlaceable', 'XMLTagPlaceable', 'parsers']

from translate.storage.placeables.base import StringElem


class AltAttrPlaceable(StringElem):
    """Placeable for the "alt=..." attributes inside XML tags."""

    @classmethod
    def parse(cls, pstr):
        """Creates an C{AltAttrPlaceable} from C{pstr} if it starts with
            C{alt="}, up to the next occurance of C{"}.

            @returns: A new C{AltAttrPlaceable} if C{pstr} starts with a valid
                occurance of an alt attribute. C{None} otherwise.
            @see: StringElem.parse"""
        if pstr.startswith('alt="') and pstr.find('"', 5) > 0:
            return cls([pstr[:pstr.find('"', 5)+1]])
        return None


class XMLEntityPlaceable(StringElem):
    """Placeable handling XML entities (C{&xxxxx;}-style entities)."""

    iseditable = False

    @classmethod
    def parse(cls, pstr):
        """Creates a new C{XMLEntityPlaceable} from the sub-string at the
            beginning of C{pstr} that starts with C{&} up to the first C{;}.

            @see: StringElem.parse"""
        match = re.search('^&\S+;', pstr)
        if match:
            return cls([pstr[:match.end()+1]])
        return None


# Not there yet...
#class TerminologyPlaceable(StringElem):
#    @classmethod
#    def parse(cls, pstr):
#        for word in self.terminology:
#            if pstr.startswith(word):
#                placeable = cls([pstr[:len(word)]])
#                placeable.translate = lambda: self.terminology[word]
#                return placeable


class XMLTagPlaceable(StringElem):
    """Placeable handling XML tags."""

    iseditable = False

    @classmethod
    def parse(cls, pstr):
        """@see: StringElem.parse"""
        if pstr.startswith('<') and pstr.find('>') > 0:
            bracket_count = 0
            for i in range(len(pstr)):
                if pstr[i] == '>':
                    i += 1
                    bracket_count -= 1
                elif pstr[i] == '<':
                    bracket_count += 1
                if bracket_count == 0:
                    break
            if i <= len(pstr):
                return cls([pstr[:i]])
            return None

parsers = [AltAttrPlaceable.parse, XMLEntityPlaceable.parse, XMLTagPlaceable.parse]
