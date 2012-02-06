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


"""Convert Gettext PO localization files to JSON files"""

from translate.storage import factory


class rejson:

    def __init__(self, templatefile, inputstore):
        from translate.storage import jsonl10n
        self.templatefile = templatefile
        self.templatestore = jsonl10n.JsonFile(templatefile)
        self.inputstore = inputstore

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            inputunit = self.inputstore.locationindex.get(unit.getid())
            if inputunit is not None:
                if inputunit.isfuzzy() and not self.includefuzzy:
                    unit.target = unit.source
                else:
                    unit.target = inputunit.target
            else:
                unit.target = unit.source
        return str(self.templatestore)


def convertjson(inputfile, outputfile, templatefile, includefuzzy=False):
    inputstore = factory.getobject(inputfile)
    if templatefile is None:
        raise ValueError("Must have template file for JSON files")
    else:
        convertor = rejson(templatefile, inputstore)
    outputstring = convertor.convertstore(includefuzzy)
    outputfile.write(outputstring)
    return 1


def main(argv=None):
    # handle command line options
    from translate.convert import convert
    formats = {
               ("po", "json"): ("json", convertjson),
              }
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
