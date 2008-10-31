#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2008 Zuza Software Foundation
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

"""classes that hold units of PHP localisation files L{phpunit} or entire files
   L{phpfile} these files are used in translating many PHP based applications.

   Only PHP files written with these conventtions are supported::
      $lang['item'] = "vale";  # Array of values
      $some_entity = "value";  # Named variables

   The parser does not support other array conventions such as::
      $lang = array(
         'item1' => 'value1',
         'item2' => 'value2',
      );

   The working of PHP strings and specifically the escaping conventions which
   differ between single quote (') and double quote (") characters are outlined
   in the PHP documentation for the U{String type<http://www.php.net/language.types.string>}
"""

from translate.storage import base
from translate.misc import quote
import re

def phpencode(text, quotechar="'"):
    """convert Python string to PHP escaping

    The encoding is implemented for 
    U{'single quote'<http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>}
    and U{"double quote"<http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>}
    syntax.

    heredoc and nowdoc are not implemented and it is not certain whether this would 
    ever be needed for PHP localisation needs.
    """
    if not text:
        return text
    return text.replace("%s" % quotechar, "\\%s" % quotechar).replace("\n", "\\n")

def phpdecode(text, quotechar="'"):
    """convert PHP escaped string to a Python string"""
    if not text:
        return text
    return text.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")

class phpunit(base.TranslationUnit):
    """a unit of a PHP file i.e. a name and value, and any comments
    associated"""
    def __init__(self, source=""):
        """construct a blank phpunit"""
        self.escape_type = None
        super(phpunit, self).__init__(source)
        self.name = ""
        self.value = ""
        self._comments = []
        self.source = source

    def setsource(self, source):
        """Sets the source AND the target to be equal"""
        self.value = phpencode(source, self.escape_type)

    def getsource(self):
        return phpdecode(self.value, self.escape_type)
    source = property(getsource, setsource)

    def settarget(self, target):
        """Note: this also sets the .source attribute!"""
        # TODO: shouldn't this just call the .source property? no quoting done here...
        self.source = target

    def gettarget(self):
        return self.source
    target = property(gettarget, settarget)

    def __str__(self):
        """convert to a string. double check that unicode is handled somehow here"""
        source = self.getoutput()
        if isinstance(source, unicode):
            return source.encode(getattr(self, "encoding", "UTF-8"))
        return source

    def getoutput(self):
        """convert the unit back into formatted lines for a php file"""
        return "".join(self._comments + ["%s='%s';\n" % (self.name, self.value)])

    def addlocation(self, location):
        self.name = location

    def getlocations(self):
        return [self.name]

    def addnote(self, note, origin=None):
        self._comments.append(note)

    def getnotes(self, origin=None):
        return '\n'.join(self._comments)

    def removenotes(self):
        self._comments = []

    def isblank(self):
        """returns whether this is a blank element, containing only comments..."""
        return not (self.name or self.value)

class phpfile(base.TranslationStore):
    """this class represents a php file, made up of phpunits"""
    UnitClass = phpunit
    def __init__(self, inputfile=None, encoding='utf-8'):
        """construct a phpfile, optionally reading in from inputfile"""
        super(phpfile, self).__init__(unitclass = self.UnitClass)
        self.filename = getattr(inputfile, 'name', '')
        self._encoding = encoding
        if inputfile is not None:
            phpsrc = inputfile.read()
            inputfile.close()
            self.parse(phpsrc)

    def parse(self, phpsrc):
        """read the source of a php file in and include them as units"""
        newunit = phpunit()
        lastvalue = ""
        value = ""
        comment = []
        invalue = False
        incomment = False
        valuequote = "" # either ' or "
        for line in phpsrc.decode(self._encoding).split("\n"):
            commentstartpos = line.find("/*")
            commentendpos = line.rfind("*/")            
            if commentstartpos != -1:
                incomment = True
                if commentendpos != -1:
                    newunit.addnote(line[commentstartpos:commentendpos].strip(), "developer")
                    incomment = False
                else:
                    newunit.addnote(line[commentstartpos:].strip(), "developer")
            if commentendpos != -1 and incomment:
                newunit.addnote(line[:commentendpos+2].strip(), "developer")
                incomment = False
            if incomment and commentstartpos == -1:
                newunit.addnote(line.strip(), "developer")
                continue
            equalpos = line.find("=")
            if equalpos != -1 and not invalue:
                newunit.addlocation(line[:equalpos].strip().replace(" ", ""))
                value = line[equalpos+1:].lstrip()[1:]
                valuequote = line[equalpos+1:].lstrip()[0]
                lastvalue = ""
                invalue = True
            else:
                if invalue:
                    value = line
            colonpos = value.rfind(";")
            while colonpos != -1:
                if value[colonpos-1] == valuequote:
                    newunit.value = lastvalue + value[:colonpos-1] 
                    newunit.escape_type = valuequote
                    lastvalue = ""
                    invalue = False
                if not invalue and colonpos != len(value)-1:
                    commentinlinepos = value.find("//", colonpos)
                    if commentinlinepos != -1:
                        newunit.addnote(value[commentinlinepos+2:].strip(), "developer") 
                if not invalue:
                    self.addunit(newunit)
                    value = ""
                    newunit = phpunit()
                colonpos = value.rfind(";", 0, colonpos)
            if invalue:
                lastvalue = lastvalue + value

    def __str__(self):
        """convert the units back to lines"""
        lines = []
        for unit in self.units:
            lines.append(str(unit))
        return "".join(lines)

if __name__ == '__main__':
    import sys
    pf = phpfile(sys.stdin)
    sys.stdout.write(str(pf))

