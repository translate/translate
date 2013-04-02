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

"""Convert Gettext PO localization files to Java/Mozilla .properties files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/prop2po.html
for examples and usage instructions.
"""

from translate.misc import quote
from translate.storage import po
from translate.storage import properties

eol = u"\n"


class reprop:

    def __init__(self, templatefile, inputstore, personality, encoding=None,
                 remove_untranslated=False):
        self.templatefile = templatefile
        self.inputstore = inputstore
        self.personality = properties.get_dialect(personality)
        self.encoding = encoding
        if self.encoding is None:
            self.encoding = self.personality.default_encoding
        self.remove_untranslated = remove_untranslated

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inmultilinemsgid = False
        self.inecho = False
        self.inputstore.makeindex()
        if self.personality.name == "gaia":
            self._explode_gaia_plurals()
        outputlines = []
        # Readlines doesn't work for UTF-16, we read() and splitlines(keepends) instead
        content = self.templatefile.read().decode(self.encoding)
        for line in content.splitlines(True):
            outputstr = self.convertline(line)
            outputlines.append(outputstr)
        return u"".join(outputlines).encode(self.encoding)

    def _explode_gaia_plurals(self):
        """Explode the gaia plurals."""
        from translate.lang import data
        for unit in self.inputstore.units:
            if not unit.hasplural():
                continue
            if unit.isfuzzy() and not self.includefuzzy or not unit.istranslated():
                continue

            names = data.cldr_plural_categories
            location = unit.getlocations()[0]
            for category, text in zip(names, unit.target.strings):
                # TODO: for now we assume all forms are present. We need to
                # fill in the rest after mapping things to the proper CLDR names.
                if category == 'zero':
                    # [zero] cases are translated as separate units
                    continue
                new_unit = self.inputstore.addsourceunit(u"fish") # not used
                new_location = '%s[%s]' % (location, category)
                new_unit.addlocation(new_location)
                new_unit.target = text
                self.inputstore.locationindex[new_location] = new_unit

            # We don't want the plural marker to be translated:
            del self.inputstore.locationindex[location]

    def convertline(self, line):
        returnline = u""
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
            returnline = quote.rstripeol(line) + eol
        else:
            line = quote.rstripeol(line)
            delimiter_char, delimiter_pos = self.personality.find_delimiter(line)
            if quote.rstripeol(line)[-1:] == '\\':
                self.inmultilinemsgid = True
            if delimiter_pos == -1:
                key = self.personality.key_strip(line)
                delimiter = " %s " % self.personality.delimiters[0]
            else:
                key = self.personality.key_strip(line[:delimiter_pos])
                # Calculate space around the equal sign
                prespace = line[line.find(' ', len(key)):delimiter_pos]
                postspacestart = len(line[delimiter_pos+1:])
                postspaceend = len(line[delimiter_pos+1:].lstrip())
                postspace = line[delimiter_pos+1:delimiter_pos+(postspacestart-postspaceend)+1]
                delimiter = prespace + delimiter_char + postspace
            if key in self.inputstore.locationindex:
                unit = self.inputstore.locationindex[key]
                if self.remove_untranslated and (unit.source == unit.target or
                                                 unit.isfuzzy() or
                                                 len(unit.target) == 0):
                    returnline = u""
                else:
                    if unit.isfuzzy() and not self.includefuzzy or len(unit.target) == 0:
                        value = unit.source
                    else:
                        value = unit.target
                    self.inecho = False
                    assert isinstance(value, unicode)
                    returnline = "%(key)s%(del)s%(value)s%(term)s%(eol)s" % \
                         {"key": "%s%s%s" % (self.personality.key_wrap_char,
                                             key,
                                             self.personality.key_wrap_char),
                          "del": delimiter,
                          "value": "%s%s%s" % (self.personality.value_wrap_char,
                                               self.personality.encode(value),
                                               self.personality.value_wrap_char),
                          "term": self.personality.pair_terminator,
                          "eol": eol,
                         }
            else:
                self.inecho = True
                returnline = line + eol
        assert isinstance(returnline, unicode)
        return returnline


def convertstrings(inputfile, outputfile, templatefile, personality="strings",
                   includefuzzy=False, encoding=None,
                   remove_untranslated=False):
    """.strings specific convertor function"""
    return convertprop(inputfile, outputfile, templatefile,
                       personality="strings", includefuzzy=includefuzzy,
                       encoding=encoding,
                       remove_untranslated=remove_untranslated)


def convertmozillaprop(inputfile, outputfile, templatefile,
                       includefuzzy=False, remove_untranslated=False):
    """Mozilla specific convertor function"""
    return convertprop(inputfile, outputfile, templatefile,
                       personality="mozilla", includefuzzy=includefuzzy,
                       remove_untranslated=remove_untranslated)


def convertprop(inputfile, outputfile, templatefile, personality="java",
                includefuzzy=False, encoding=None, remove_untranslated=False):
    inputstore = po.pofile(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for properties files")
        # convertor = po2prop()
    else:
        convertor = reprop(templatefile, inputstore, personality, encoding,
                           remove_untranslated)
    outputprop = convertor.convertstore(includefuzzy)
    outputfile.write(outputprop)
    return 1

formats = {
    ("po", "properties"): ("properties", convertprop),
    ("po", "lang"): ("lang", convertprop),
    ("po", "strings"): ("strings", convertstrings),
}


def main(argv=None):
    # handle command line options
    from translate.convert import convert
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_option("", "--personality", dest="personality",
            default=properties.default_dialect, type="choice",
            choices=properties.dialects.keys(),
            help="override the input file format: %s (for .properties files, default: %s)" %
                 (", ".join(properties.dialects.iterkeys()),
                  properties.default_dialect),
            metavar="TYPE")
    parser.add_option("", "--encoding", dest="encoding", default=None,
            help="override the encoding set by the personality",
            metavar="ENCODING")
    parser.add_option("", "--removeuntranslated", dest="remove_untranslated",
            default=False, action="store_true",
            help="remove key value from output if it is untranslated")
    parser.add_fuzzy_option()
    parser.passthrough.append("personality")
    parser.passthrough.append("encoding")
    parser.passthrough.append("remove_untranslated")
    parser.run(argv)

if __name__ == '__main__':
    main()
