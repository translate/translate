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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""convert Gettext PO localization files to Java/Mozilla .properties files

see: http://translate.sourceforge.net/wiki/toolkit/po2prop for examples and 
usage instructions
"""

from translate.misc import quote
from translate.storage import po
from translate.storage.properties import find_delimiter

eol = "\n"

class reprop:
    def __init__(self, templatefile):
        self.templatefile = templatefile
        self.inputdict = {}

    def convertstore(self, inputstore, personality, includefuzzy=False):
        self.personality = personality
        self.inmultilinemsgid = False
        self.inecho = False
        self.makestoredict(inputstore, includefuzzy)
        outputlines = []
        for line in self.templatefile.readlines():
            outputstr = self.convertline(line)
            outputlines.append(outputstr)
        return outputlines

    def makestoredict(self, store, includefuzzy=False):
        # make a dictionary of the translations
        for unit in store.units:
            if includefuzzy or not unit.isfuzzy():
                # there may be more than one entity due to msguniq merge
                for entity in unit.getlocations():
                    propstring = unit.target
                    
                    # NOTE: triple-space as a string means leave it empty (special signal)
                    if len(propstring.strip()) == 0 and propstring != "   ":
                        propstring = unit.source
                    self.inputdict[entity] = propstring

    def convertline(self, line):
        returnline = ""
        # handle multiline msgid if we're in one
        if self.inmultilinemsgid:
            msgid = quote.rstripeol(line).strip()
            # see if there's more
            self.inmultilinemsgid = (msgid[-1:] == '\\')
            # if we're echoing...
            if self.inecho:
                returnline = line
        # otherwise, this could be a comment
        elif line.strip()[:1] == '#':
            returnline = quote.rstripeol(line)+eol
        else:
            line = quote.rstripeol(line)
            delimiter_char, delimiter_pos = find_delimiter(line)
            if quote.rstripeol(line)[-1:] == '\\':
                self.inmultilinemsgid = True
            if delimiter_pos == -1:
                key = line.strip()
                delimiter = " = "
            else:
                key = line[:delimiter_pos].strip()
                # Calculate space around the equal sign
                prespace = line.lstrip()[line.lstrip().find(' '):delimiter_pos]
                postspacestart = len(line[delimiter_pos+1:])
                postspaceend = len(line[delimiter_pos+1:].lstrip())
                postspace = line[delimiter_pos+1:delimiter_pos+(postspacestart-postspaceend)+1]
                delimiter = prespace + delimiter_char + postspace
            if self.inputdict.has_key(key):
                self.inecho = False
                value = self.inputdict[key]
                if isinstance(value, str):
                    value = value.decode('utf8')
                if self.personality == "mozilla" or self.personality == "skype":
                    returnline = key + delimiter + quote.mozillapropertiesencode(value)+eol
                else:
                    returnline = key + delimiter + quote.javapropertiesencode(value)+eol
            else:
                self.inecho = True
                returnline = line+eol
        if isinstance(returnline, unicode):
            returnline = returnline.encode('utf-8')
        return returnline

def convertmozillaprop(inputfile, outputfile, templatefile, includefuzzy=False):
    """Mozilla specific convertor function"""
    return convertprop(inputfile, outputfile, templatefile, personality="mozilla", includefuzzy=includefuzzy)

def convertprop(inputfile, outputfile, templatefile, personality="java", includefuzzy=False):
    inputstore = po.pofile(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for properties files")
        # convertor = po2prop()
    else:
        convertor = reprop(templatefile)
    outputproplines = convertor.convertstore(inputstore, personality, includefuzzy)
    outputfile.writelines(outputproplines)
    return 1

formats = {
    ("po", "properties"): ("properties", convertprop),
    ("po", "lang"):       ("lang",       convertprop),
}

def main(argv=None):
    # handle command line options
    from translate.convert import convert
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.add_option("", "--personality", dest="personality", default="java", type="choice",
            choices=["java", "mozilla", "skype"],
            help="set the output behaviour: java (default), mozilla, skype", metavar="TYPE")
    parser.add_fuzzy_option()
    parser.passthrough.append("personality")
    parser.run(argv)

if __name__ == '__main__':
    main()

