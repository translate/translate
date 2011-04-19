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


"""convert Gettext PO localization files to .ini files"""

from translate.storage import factory


class reini:

    def __init__(self, templatefile, inputstore, dialect="default"):
        from translate.storage import ini
        self.templatefile = templatefile
        self.templatestore = ini.inifile(templatefile, dialect=dialect)
        self.inputstore = inputstore

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            for location in unit.getlocations():
                if location in self.inputstore.locationindex:
                    inputunit = self.inputstore.locationindex[location]
                    if inputunit.isfuzzy() and not self.includefuzzy:
                        unit.target = unit.source
                    else:
                        unit.target = inputunit.target
                else:
                    unit.target = unit.source
        return unicode(self.templatestore)


def convertini(inputfile, outputfile, templatefile, includefuzzy=False, dialect="default"):
    inputstore = factory.getobject(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for ini files")
    else:
        convertor = reini(templatefile, inputstore, dialect)
    outputstring = convertor.convertstore(includefuzzy)
    outputfile.write(outputstring)
    return 1


def convertisl(inputfile, outputfile, templatefile, includefuzzy=False, dialect="inno"):
    convertini(inputfile, outputfile, templatefile, includefuzzy, dialect)


def main(argv=None):
    # handle command line options
    from translate.convert import convert
    formats = {
               ("po", "ini"): ("ini", convertini),
               ("po", "isl"): ("isl", convertisl),
              }
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
