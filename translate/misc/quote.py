#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""String processing utilities for extracting strings with various kinds
of delimiters"""

import logging
import htmlentitydefs

from translate.misc.typecheck import accepts, returns


def find_all(searchin, substr):
    """Returns a list of locations where substr occurs in searchin
    locations are not allowed to overlap"""
    location = 0
    locations = []
    while location != -1:
        location = searchin.find(substr, location)
        if location != -1:
            locations.append(location)
            location += len(substr)
    return locations


def extract(source, startdelim, enddelim,
            escape=None, startinstring=False, allowreentry=True):
    """Extracts a doublequote-delimited string from a string, allowing for
    backslash-escaping returns tuple of (quoted string with quotes, still in
    string at end).
    """
    # Note that this returns the quote characters as well... even internally
    instring = startinstring
    enteredonce = False
    lenstart = len(startdelim)
    lenend = len(enddelim)
    startdelim_places = find_all(source, startdelim)
    if startdelim == enddelim:
        enddelim_places = startdelim_places[:]
    else:
        enddelim_places = find_all(source, enddelim)
    if escape is not None:
        lenescape = len(escape)
        escape_places = find_all(source, escape)
        # Filter escaped escapes
        true_escape = False
        true_escape_places = []
        for escape_pos in escape_places:
            if escape_pos - lenescape in escape_places:
                true_escape = not true_escape
            else:
                true_escape = True
            if true_escape:
                true_escape_places.append(escape_pos)
        startdelim_places = [pos for pos in startdelim_places if pos - lenescape not in true_escape_places]
        enddelim_places = [pos + lenend for pos in enddelim_places if pos - lenescape not in true_escape_places]
    else:
        enddelim_places = [pos + lenend for pos in enddelim_places]
    # Get a unique sorted list of the significant places in the string
    significant_places = [0] + startdelim_places + enddelim_places + [len(source)-1]
    significant_places.sort()
    extracted = ""
    lastpos = None
    for pos in significant_places:
        if instring and pos in enddelim_places:
            # Make sure that if startdelim == enddelim we don't get confused
            # and count the same string as start and end.
            if lastpos == pos - lenstart and lastpos in startdelim_places:
                continue
            extracted += source[lastpos:pos]
            instring = False
            lastpos = pos
        if (not instring) and pos in startdelim_places and not (enteredonce and not allowreentry):
            instring = True
            enteredonce = True
            lastpos = pos
    if instring:
        extracted += source[lastpos:]
    return (extracted, instring)


def extractwithoutquotes(source, startdelim, enddelim, escape=None,
                         startinstring=False, includeescapes=True,
                         allowreentry=True):
    """Extracts a doublequote-delimited string from a string, allowing for
    backslash-escaping includeescapes can also be a function that takes the
    whole escaped string and returns the replaced version.
    """
    instring = startinstring
    enteredonce = False
    lenstart = len(startdelim)
    lenend = len(enddelim)
    startdelim_places = find_all(source, startdelim)
    if startdelim == enddelim:
        enddelim_places = startdelim_places[:]
    else:
        enddelim_places = find_all(source, enddelim)
    #hell slow because it is called far too often
    if escape is not None:
        lenescape = len(escape)
        escape_places = find_all(source, escape)
        # filter escaped escapes
        true_escape = False
        true_escape_places = []
        for escape_pos in escape_places:
            if escape_pos - lenescape in escape_places:
                true_escape = not true_escape
            else:
                true_escape = True
            if true_escape:
                true_escape_places.append(escape_pos)
        startdelim_places = [pos for pos in startdelim_places if pos - lenescape not in true_escape_places]
        enddelim_places = [pos + lenend for pos in enddelim_places if pos - lenescape not in true_escape_places]
    else:
        enddelim_places = [pos + lenend for pos in enddelim_places]
    # get a unique sorted list of the significant places in the string
    significant_places = [0] + startdelim_places + enddelim_places + [len(source)-1]
    significant_places.sort()
    extracted = ""
    lastpos = 0
    callable_includeescapes = callable(includeescapes)
    checkescapes = callable_includeescapes or not includeescapes
    for pos in significant_places:
        if instring and pos in enddelim_places and lastpos != pos - lenstart:
            section_start, section_end = lastpos + len(startdelim), pos - len(enddelim)
            section = source[section_start:section_end]
            if escape is not None and checkescapes:
                escape_list = [epos - section_start for epos in true_escape_places if section_start <= epos <= section_end]
                new_section = ""
                last_epos = 0
                for epos in escape_list:
                    new_section += section[last_epos:epos]
                    if callable_includeescapes:
                        replace_escape = includeescapes(section[epos:epos + lenescape + 1])
                        # TODO: deprecate old method of returning boolean from
                        # includeescape, by removing this if block
                        if not isinstance(replace_escape, basestring):
                            if replace_escape:
                                replace_escape = section[epos:epos + lenescape + 1]
                            else:
                                replace_escape = section[epos + lenescape:epos + lenescape + 1]
                        new_section += replace_escape
                        last_epos = epos + lenescape + 1
                    else:
                        last_epos = epos + lenescape
                section = new_section + section[last_epos:]
            extracted += section
            instring = False
            lastpos = pos
        if (not instring) and pos in startdelim_places and not (enteredonce and not allowreentry):
            instring = True
            enteredonce = True
            lastpos = pos
    if instring:
        section_start = lastpos + len(startdelim)
        section = source[section_start:]
        if escape is not None and not includeescapes:
            escape_list = [epos - section_start for epos in true_escape_places if section_start <= epos]
            new_section = ""
            last_epos = 0
            for epos in escape_list:
                new_section += section[last_epos:epos]
                if callable_includeescapes and includeescapes(section[epos:epos + lenescape + 1]):
                    last_epos = epos
                else:
                    last_epos = epos + lenescape
            section = new_section + section[last_epos:]
        extracted += section
    return (extracted, instring)


def escapequotes(source, escapeescapes=0):
    "Returns the same string, with double quotes escaped with backslash"
    if escapeescapes:
        return source.replace('\\', '\\\\').replace('"', '\\"')
    else:
        return source.replace('"', '\\"')


def escapesinglequotes(source):
    "Returns the same string, with single quotes doubled"
    return source.replace("'", "''")


@accepts(unicode)
@returns(unicode)
def htmlentityencode(source):
    """encodes source using HTML entities e.g. © -> &copy;"""
    output = u""
    for char in source:
        charnum = ord(char)
        if charnum in htmlentitydefs.codepoint2name:
            output += u"&%s;" % htmlentitydefs.codepoint2name[charnum]
        else:
            output += str(char)
    return output


@accepts(unicode)
@returns(unicode)
def htmlentitydecode(source):
    """decodes source using HTML entities e.g. &copy; -> ©"""
    output = u""
    inentity = False
    for char in source:
        if char == "&":
            inentity = True
            possibleentity = ""
            continue
        if inentity:
            if char == ";":
                if len(possibleentity) > 0 and possibleentity in htmlentitydefs.name2codepoint:
                    output += unichr(htmlentitydefs.name2codepoint[possibleentity])
                    inentity = False
                else:
                    output += "&" + possibleentity + ";"
                    inentity = False
            elif char == " ":
                output += "&" + possibleentity + char
                inentity = False
            else:
                possibleentity += char
        else:
            output += char
    return output


@accepts(unicode)
@returns(unicode)
def javapropertiesencode(source):
    """Encodes source in the escaped-unicode encoding used by Java
    .properties files
    """
    output = u""
    if source and source[0] == u" ":
        output = u"\\"
    for char in source:
        charnum = ord(char)
        if char in controlchars:
            output += controlchars[char]
        elif 0 <= charnum < 128:
            output += str(char)
        else:
            output += u"\\u%04X" % charnum
    return output


@accepts(unicode)
@returns(unicode)
def mozillapropertiesencode(source):
    """Encodes source in the escaped-unicode encoding used by Mozilla
    .properties files.
    """
    output = u""
    for char in source:
        if char in controlchars:
            output += controlchars[char]
        else:
            output += char
    return output

propertyescapes = {
    # escapes that are self-escaping
    "\\": "\\", "'": "'", '"': '"',
    # control characters that we keep
    "f": "\f", "n": "\n", "r": "\r", "t": "\t",
    }

controlchars = {
    # the reverse of the above...
    "\\": "\\\\",
    "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t",
    }


def escapecontrols(source):
    """escape control characters in the given string"""
    for key, value in controlchars.iteritems():
        source = source.replace(key, value)
    return source


@accepts(unicode)
@returns(unicode)
def propertiesdecode(source):
    """Decodes source from the escaped-unicode encoding used by .properties
    files.

    Java uses Latin1 by default, and Mozilla uses UTF-8 by default.

    Since the .decode("unicode-escape") routine decodes everything, and we
    don't want to we reimplemented the algorithm from Python Objects/unicode.c
    in Python and modify it to retain escaped control characters.
    """
    output = u""
    s = 0

    def unichr2(i):
        """Returns a Unicode string of one character with ordinal 32 <= i,
        otherwise an escaped control character.
        """
        if 32 <= i:
            return unichr(i)
        elif unichr(i) in controlchars:
            # we just return the character, unescaped
            # if people want to escape them they can use escapecontrols
            return unichr(i)
        else:
            return "\\u%04x" % i

    while s < len(source):
        c = source[s]
        if c != '\\':
            output += c
            s += 1
            continue
        s += 1
        if s >= len(source):
            # this is an escape at the end of the line, which implies
            # a continuation..., return the escape to inform the parser
            output += c
            continue
        c = source[s]
        s += 1
        if c == '\n':
            pass
        # propertyescapes lookups
        elif c in propertyescapes:
            output += propertyescapes[c]
        # \uXXXX escapes
        # \UXXXX escapes
        elif c in "uU":
            digits = 4
            x = 0
            for digit in range(digits):
                x <<= 4
                if s + digit >= len(source):
                    digits = digit
                    break
                c = source[s + digit].lower()
                if c.isdigit():
                    x += ord(c) - ord('0')
                elif c in "abcdef":
                    x += ord(c) - ord('a') + 10
                else:
                    break
            s += digits
            output += unichr2(x)
        elif c == "N":
            if source[s] != "{":
                logging.warn("Invalid named unicode escape: no { after \\N")
                output += "\\" + c
                continue
            s += 1
            e = source.find("}", s)
            if e == -1:
                logging.warn("Invalid named unicode escape: no } after \\N{")
                output += "\\" + c
                continue
            import unicodedata
            name = source[s:e]
            output += unicodedata.lookup(name)
            s = e + 1
        else:
            output += c # Drop any \ that we don't specifically handle
    return output


def quotestr(source, escapeescapes=0):
    """Returns a doublequote-delimited quoted string, escaping double
    quotes with backslash.
    """
    if isinstance(source, list):
        firstline = True
        for line in source:
            if firstline:
                newsource = '"' + escapequotes(line, escapeescapes) + '"'
                firstline = False
            else:
                newsource = newsource + '\n' + \
                            '"' + escapequotes(line, escapeescapes) + '"'
        return newsource
    else:
        return '"' + escapequotes(source, escapeescapes) + '"'


def singlequotestr(source):
    """Returns a doublequote-delimited quoted string, escaping single quotes
    with themselves.
    """
    return "'" + escapesinglequotes(source) + "'"


def findend(string, substring):
    s = string.find(substring)
    if s != -1:
        s += len(substring)
    return s


def rstripeol(string):
    return string.rstrip("\r\n")


def stripcomment(comment, startstring="<!--", endstring="-->"):
    cstart = comment.find(startstring)
    if cstart == -1:
        cstart = 0
    else:
        cstart += len(startstring)
    cend = comment.find(endstring, cstart)
    return comment[cstart:cend].strip()


def unstripcomment(comment, startstring="<!-- ", endstring=" -->\n"):
    return startstring + comment.strip() + endstring
