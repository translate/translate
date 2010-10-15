#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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

"""Classes that hold units of .properties, and similar, files that are used in
   translating Java, Mozilla, MacOS and other software.

   The L{propfile} class is a monolingual class with L{propunit} providing unit
   level access.

   The .properties store has become a general key value pair class with
   L{Dialect} providing the ability to change the behaviour of the parsing
   and handling of the various dialects.

   Currently we support::
     * Java .properties
     * Mozilla .properties
     * Adobe Flex files
     * MacOS X .strings files
     * Skype .lang files


   Dialects
   ========
   The following provides references and descriptions of the various dialects supported::

   Java
   ----
   Java .properties are supported completely except for the ability to drop
   pairs that are not translated.

   The following U{.properties file
   description<http://java.sun.com/j2se/1.4.2/docs/api/java/util/Properties.html#load(java.io.InputStream)>}
   and U{example <http://www.exampledepot.com/egs/java.util/Props.html>} give
   some good references to the .properties specification.

   Properties file may also hold Java
   U{MessageFormat<http://java.sun.com/j2se/1.4.2/docs/api/java/text/MessageFormat.html>}
   messages.  No special handling is provided in this storage class for
   MessageFormat, but this may be implemented in future.

   All delimiter types, comments, line continuations and spaces handling in
   delimeters are supported.

   Mozilla
   -------
   Mozilla files use '=' as a delimiter, are UTF-8 encoded and thus don't need \\u
   escaping.  Any \\U values will be converted to correct Unicode characters.
`
   Strings
   -------
   Mac OS X strings files are implemented using
   U{these<http://developer.apple.com/mac/library/documentation/MacOSX/Conceptual/BPInternational/Articles/StringsFiles.html>}
   U{two<http://developer.apple.com/mac/library/documentation/Cocoa/Conceptual/LoadingResources/Strings/Strings.html>}
   articles as references.

   Flex
   ----
   Adobe Flex files seem to be normal .properties files but in UTF-8 just like
   Mozilla files. This
   U{page<http://livedocs.adobe.com/flex/3/html/help.html?content=l10n_3.html>}
   provides the information used to implement the dialect.

   Skype
   -----
   Skype .lang files seem to be UTF-16 encoded .properties files.

   Implementation
   ==============

   A simple summary of what is permissible follows.

   Comments supported::
     # a comment
     ! a comment
     // a comment (only at the beginning of a line)
     /* a comment (not across multiple lines) */

   Name and Value pairs::
     # Delimiters
     key = value
     key : value
     key value

     # Space in key and around value
     \ key\ = \ value

     # Note that the b and c are escaped for epydoc rendering
     b = a string with escape sequences \\t \\n \\r \\\\ \\" \\' \\ (space) \u0123
     c = a string with a continuation line \\
         continuation line

     # Special cases
     # key with no value
     key
     # value no key (extractable in prop2po but not mergeable in po2prop)
     =value

     # .strings specific
     "key" = "value";
"""

import re
import warnings

from translate.lang import data
from translate.misc import quote
from translate.misc.typecheck import accepts, returns, IsOneOf
from translate.storage import base

# the rstripeols convert dos <-> unix nicely as well
# output will be appropriate for the platform

eol = "\n"


@accepts(unicode, [unicode])
@returns(IsOneOf(type(None), unicode), int)
def _find_delimiter(line, delimiters):
    """Find the type and position of the delimiter in a property line.

    Property files can be delimeted by "=", ":" or whitespace (space for now).
    We find the position of each delimiter, then find the one that appears
    first.

    @param line: A properties line
    @type line: str
    @param delimiters: valid delimiters
    @type delimiters: list
    @return: delimiter character and offset within L{line}
    @rtype: Tuple (delimiter char, Offset Integer)
    """
    delimiter_dict = {}
    for delimiter in delimiters:
        delimiter_dict[delimiter] = -1
    delimiters = delimiter_dict
    # Find the position of each delimiter type
    for delimiter, pos in delimiters.iteritems():
        prewhitespace = len(line) - len(line.lstrip())
        pos = line.find(delimiter, prewhitespace)
        while pos != -1:
            if delimiters[delimiter] == -1 and line[pos-1] != u"\\":
                delimiters[delimiter] = pos
                break
            pos = line.find(delimiter, pos + 1)
    # Find the first delimiter
    mindelimiter = None
    minpos = -1
    for delimiter, pos in delimiters.iteritems():
        if pos == -1 or delimiter == u" ":
            continue
        if minpos == -1 or pos < minpos:
            minpos = pos
            mindelimiter = delimiter
    if mindelimiter is None and delimiters.get(u" ", -1) != -1:
        # Use space delimiter if we found nothing else
        return (u" ", delimiters[" "])
    if mindelimiter is not None and u" " in delimiters and delimiters[u" "] < delimiters[mindelimiter]:
        # If space delimiter occurs earlier than ":" or "=" then it is the
        # delimiter only if there are non-whitespace characters between it and
        # the other detected delimiter.
        if len(line[delimiters[u" "]:delimiters[mindelimiter]].strip()) > 0:
            return (u" ", delimiters[u" "])
    return (mindelimiter, minpos)


def find_delimeter(line):
    """Spelling error that is kept around for in case someone relies on it.

    Deprecated."""
    warnings.warn("deprecated use Dialect.find_delimiter instead", DeprecationWarning)
    return _find_delimiter(line, DialectJava.delimiters)


@accepts(unicode)
@returns(bool)
def is_line_continuation(line):
    """Determine whether L{line} has a line continuation marker.

    .properties files can be terminated with a backslash (\\) indicating
    that the 'value' continues on the next line.  Continuation is only
    valid if there are an odd number of backslashses (an even number
    would result in a set of N/2 slashes not an escape)

    @param line: A properties line
    @type line: str
    @return: Does L{line} end with a line continuation
    @rtype: Boolean
    """
    pos = -1
    count = 0
    if len(line) == 0:
        return False
    # Count the slashes from the end of the line. Ensure we don't
    # go into infinite loop.
    while len(line) >= -pos and line[pos:][0] == "\\":
        pos -= 1
        count += 1
    return (count % 2) == 1  # Odd is a line continuation, even is not


@accepts(unicode)
@returns(unicode)
def _key_strip(key):
    """Cleanup whitespace found around a key

    @param key: A properties key
    @type key: str
    @return: Key without any uneeded whitespace
    @rtype: str
    """
    newkey = key.rstrip()
    # If line now end in \ we put back the whitespace that was escaped
    if newkey[-1:] == "\\":
        newkey += key[len(newkey):len(newkey)+1]
    return newkey.lstrip()

dialects = {}
default_dialect = "java"


def register_dialect(dialect):
    dialects[dialect.name] = dialect


def get_dialect(dialect=default_dialect):
    return dialects.get(dialect)


class Dialect(object):
    """Settings for the various behaviours in key=value files."""
    name = None
    default_encoding = 'iso-8859-1'
    delimiters = None
    pair_terminator = u""
    key_wrap_char = u""
    value_wrap_char = u""
    drop_comments = []

    def encode(cls, string):
        """Encode the string"""
        return quote.javapropertiesencode(string or u"")
    encode = classmethod(encode)

    def find_delimiter(cls, line):
        """Find the delimeter"""
        return _find_delimiter(line, cls.delimiters)
    find_delimiter = classmethod(find_delimiter)

    def key_strip(cls, key):
        """Strip uneeded characters from the key"""
        return _key_strip(key)
    key_strip = classmethod(key_strip)

    def value_strip(cls, value):
        """Strip uneeded characters from the value"""
        return value.lstrip()
    value_strip = classmethod(value_strip)


class DialectJava(Dialect):
    name = "java"
    default_encoding = "iso-8859-1"
    delimiters = [u"=", u":", u" "]
register_dialect(DialectJava)


class DialectFlex(DialectJava):
    name = "flex"
    default_encoding = "utf-8"
register_dialect(DialectFlex)


class DialectMozilla(Dialect):
    name = "mozilla"
    default_encoding = "utf-8"
    delimiters = [u"="]

    def encode(cls, string):
        return quote.mozillapropertiesencode(string or u"")
    encode = classmethod(encode)
register_dialect(DialectMozilla)


class DialectSkype(Dialect):
    name = "skype"
    default_encoding = "utf-16"
    delimiters = [u"="]

    def encode(cls, string):
        return quote.mozillapropertiesencode(string or u"")
    encode = classmethod(encode)
register_dialect(DialectSkype)


class DialectStrings(Dialect):
    name = "strings"
    default_encoding = "utf-16"
    delimiters = [u"="]
    pair_terminator = u";"
    key_wrap_char = u'"'
    value_wrap_char = u'"'
    drop_comments = ["/* No comment provided by engineer. */"]

    def key_strip(cls, key):
        """Strip uneeded characters from the key"""
        newkey = key.rstrip().rstrip('"')
        # If line now end in \ we put back the char that was escaped
        if newkey[-1:] == "\\":
            newkey += key[len(newkey):len(newkey)+1]
        return newkey.lstrip().lstrip('"')
    key_strip = classmethod(key_strip)

    def value_strip(cls, value):
        """Strip uneeded characters from the value"""
        newvalue = value.rstrip().rstrip(';').rstrip('"')
        # If line now end in \ we put back the char that was escaped
        if newvalue[-1:] == "\\":
            newvalue += value[len(newvalue):len(newvalue)+1]
        return newvalue.lstrip().lstrip('"')
    value_strip = classmethod(value_strip)

    def encode(cls, string):
        return string.replace('"', '\\"').replace("\n", r"\n").replace("\t", r"\t")
    encode = classmethod(encode)
register_dialect(DialectStrings)


class propunit(base.TranslationUnit):
    """an element of a properties file i.e. a name and value, and any comments
    associated"""

    def __init__(self, source="", personality="java"):
        """construct a blank propunit"""
        self.personality = get_dialect(personality)
        super(propunit, self).__init__(source)
        self.name = u""
        self.value = u""
        self.translation = u""
        self.delimiter = u"="
        self.comments = []
        self.source = source

    def setsource(self, source):
        self._rich_source = None
        source = data.forceunicode(source)
        self.value = self.personality.encode(source or u"")

    def getsource(self):
        value = quote.propertiesdecode(self.value)
        return value

    source = property(getsource, setsource)

    def settarget(self, target):
        self._rich_target = None
        target = data.forceunicode(target)
        self.translation = self.personality.encode(target or u"")

    def gettarget(self):
        translation = quote.propertiesdecode(self.translation)
        translation = re.sub(u"\\\\ ", u" ", translation)
        return translation

    target = property(gettarget, settarget)

    def _get_encoding(self):
        if self._store:
            return self._store.encoding
        else:
            return self.personality.default_encoding
    encoding = property(_get_encoding)

    def __str__(self):
        """convert to a string. double check that unicode is handled somehow
        here"""
        source = self.getoutput()
        assert isinstance(source, unicode)
        return source.encode(self.encoding)

    def getoutput(self):
        """convert the element back into formatted lines for a .properties
        file"""
        notes = self.getnotes()
        if notes:
            notes += u"\n"
        if self.isblank():
            return notes + u"\n"
        else:
            self.value = self.personality.encode(self.source)
            self.translation = self.personality.encode(self.target)
            value = self.translation or self.value
            return u"%(notes)s%(key)s%(del)s%(value)s\n" % {"notes": notes,
                                                            "key": self.name,
                                                            "del": self.delimiter,
                                                            "value": value}

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append"):
        if origin in ['programmer', 'developer', 'source code', None]:
            text = data.forceunicode(text)
            self.comments.append(text)
        else:
            return super(propunit, self).addnote(text, origin=origin,
                                                 position=position)

    def getnotes(self, origin=None):
        if origin in ['programmer', 'developer', 'source code', None]:
            return u'\n'.join(self.comments)
        else:
            return super(propunit, self).getnotes(origin)

    def removenotes(self):
        self.comments = []

    def isblank(self):
        """returns whether this is a blank element, containing only
        comments."""
        return not (self.name or self.value)

    def istranslatable(self):
        return bool(self.name)

    def getid(self):
        return self.name

    def setid(self, value):
        self.name = value


class propfile(base.TranslationStore):
    """this class represents a .properties file, made up of propunits"""
    UnitClass = propunit

    def __init__(self, inputfile=None, personality="java", encoding=None):
        """construct a propfile, optionally reading in from inputfile"""
        super(propfile, self).__init__(unitclass=self.UnitClass)
        self.personality = get_dialect(personality)
        self.encoding = encoding or self.personality.default_encoding
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            propsrc = inputfile.read()
            inputfile.close()
            self.parse(propsrc)

    def parse(self, propsrc):
        """read the source of a properties file in and include them as units"""
        if self.encoding == "auto":
            import chardet
            detected = chardet.detect(propsrc)
            if detected['confidence'] > 0.48:
                self.encoding = detected['encoding']
            else:
                self.encoding = self.personality.default_encoding

        newunit = propunit("", self.personality.name)
        inmultilinevalue = False
        propsrc = unicode(propsrc, self.encoding)
        for line in propsrc.split(u"\n"):
            # handle multiline value if we're in one
            line = quote.rstripeol(line)
            if inmultilinevalue:
                newunit.value += line.lstrip()
                # see if there's more
                inmultilinevalue = is_line_continuation(newunit.value)
                # if we're still waiting for more...
                if inmultilinevalue:
                    # strip the backslash
                    newunit.value = newunit.value[:-1]
                if not inmultilinevalue:
                    # we're finished, add it to the list...
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
            # otherwise, this could be a comment
            # FIXME handle /* */ in a more reliable way
            # FIXME handle // inline comments
            elif line.strip()[:1] in (u'#', u'!') or line.strip()[:2] in (u"/*", u"//") or line.strip()[:-2] == "*/":
                # add a comment
                if line not in self.personality.drop_comments:
                    newunit.comments.append(line)
            elif not line.strip():
                # this is a blank line...
                if str(newunit).strip():
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
            else:
                newunit.delimiter, delimiter_pos = self.personality.find_delimiter(line)
                if delimiter_pos == -1:
                    newunit.name = self.personality.key_strip(line)
                    newunit.value = u""
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
                else:
                    newunit.name = self.personality.key_strip(line[:delimiter_pos])
                    if is_line_continuation(line[delimiter_pos+1:].lstrip()):
                        inmultilinevalue = True
                        newunit.value = line[delimiter_pos+1:].lstrip()[:-1]
                    else:
                        newunit.value = self.personality.value_strip(line[delimiter_pos+1:])
                        self.addunit(newunit)
                        newunit = propunit("", self.personality.name)
        # see if there is a leftover one...
        if inmultilinevalue or len(newunit.comments) > 0:
            self.addunit(newunit)

    def __str__(self):
        """convert the units back to lines"""
        lines = []
        for unit in self.units:
            lines.append(str(unit))
        return "".join(lines)


class stringsfile(propfile):
    Name = _("OS X Strings")
    Extensions = ['strings']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "strings"
        super(stringsfile, self).__init__(*args, **kwargs)
