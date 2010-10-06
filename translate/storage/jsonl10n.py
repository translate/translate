#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007,2009,2010 Zuza Software Foundation
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

"""Class that manages JSON data files for translation

JSON is an acronym for JavaScript Object Notation, it is an open standard
designed for human-readable data interchange.

JSON basic types
================
  - Number (integer or real)
  - String (double-quoted Unicode with backslash escaping)
  - Boolean (true or false)
  - Array (an ordered sequence of values, comma-separated and enclosed
    in square brackets)
  - Object (a collection of key:value pairs, comma-separated and
    enclosed in curly braces)
  - null

Example
=======

  {
       "firstName": "John",
       "lastName": "Smith",
       "age": 25,
       "address": {
           "streetAddress": "21 2nd Street",
           "city": "New York",
           "state": "NY",
           "postalCode": "10021"
       },
       "phoneNumber": [
           {
             "type": "home",
             "number": "212 555-1234"
           },
           {
             "type": "fax",
             "number": "646 555-4567"
           }
       ]
   }


TODO
====
  - Handle \u and other escapes in Unicode
  - Manage data type storage and conversion. True -> "True" -> True
  - Sort the extracted data to the order of the JSON file

"""

import re
from StringIO import StringIO
try:
    import json as json #available since Python 2.6
except ImportError:
    import simplejson as json #API compatible with the json module

from translate.storage import base


class JsonUnit(base.TranslationUnit):
    """A JSON entry"""

    def __init__(self, source=None, encoding="UTF-8"):
        self.location = ""
        if source:
            self.source = source
        super(JsonUnit, self).__init__(source)

    def addlocation(self, location):
        self.location = location

    def getlocations(self):
        return [self.location]


class JsonFile(base.TranslationStore):
    """A JSON file"""
    UnitClass = JsonUnit

    def __init__(self, inputfile=None, unitclass=UnitClass, filter=None):
        """construct a JSON file, optionally reading in from inputfile."""
        base.TranslationStore.__init__(self, unitclass=unitclass)
        self._filter = filter
        self.filename = ''
        self._file = None
        if inputfile is not None:
            self.parse(inputfile)

    def __str__(self):
        return json.dumps(self._file, sort_keys=True, indent=4)

    def _extract_translatables(self, data, stop=None, prev="", last=None):
        """Recursive function to extract items from the data files

        data is the current branch
        stop is a list of leaves to extract or None to extract everything
        prev is the heirchy of the tree at this iteration
        last is the last node
        """
        usable = {}
        if isinstance(data, dict):
            for k, v in data.iteritems():
                if (stop is None or k in stop) and (isinstance(v, str) or isinstance(v, unicode)):
                        usable["%s.%s" % (prev, k)] = v
                else:
                    usable.update(self._extract_translatables(v, stop, "%s.%s" % (prev, k), k))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if (stop is None or last in stop) and (isinstance(item, str) or isinstance(item, unicode)):
                        usable["%s[%s]" % (prev, i)] = item
                else:
                    usable.update(self._extract_translatables(item, stop, "%s[%s]" % (prev, i), item))
        elif isinstance(data, str) or isinstance(data, unicode):
            if (stop is None or last in stop):
                usable[prev] = data
        elif isinstance(data, bool):
            if (stop is None or last in stop):
                usable[prev] = str(data)
        else:
            raise ValueError("We don't handle these values:\n"
                             "Type: %s\n"
                             "Data: %s\n"
                             "Previous: %s" % (type(data), data, prev))
        return usable

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
        try:
            self._file = json.load(input)
        except ValueError, e:
            raise base.ParseError(e.message)

        for k, v in self._extract_translatables(self._file, stop=self._filter).iteritems():
            unit = self.addsourceunit(v)
            unit.addlocation(k)
