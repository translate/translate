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

"""Convert Gettext PO localization files to JSON files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/json2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import factory, jsonl10n


class rejson:

    def __init__(self, templatefile, inputstore):
        self.templatefile = templatefile
        self.templatestore = jsonl10n.JsonFile(templatefile)
        self.inputstore = inputstore

    def convertstore(self, includefuzzy=False, remove_untranslated=False):
        self.includefuzzy = includefuzzy
        self.remove_untranslated = remove_untranslated
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            inputunit = self.inputstore.locationindex.get(unit.getid())
            if inputunit is not None:
                if inputunit.isfuzzy() and not self.includefuzzy:
                    if self.remove_untranslated:
                        unit.target = u""
                    else:
                        unit.target = unit.source
                else:
                    unit.target = inputunit.target
            else:
                unit.target = unit.source
        return str(self.templatestore)


def convertjson(inputfile, outputfile, templatefile, includefuzzy=False,
                outputthreshold=None, remove_untranslated=False):
    inputstore = factory.getobject(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    if templatefile is None:
        raise ValueError("Must have template file for JSON files")

    convertor = rejson(templatefile, inputstore)
    outputstring = convertor.convertstore(includefuzzy, remove_untranslated)
    outputfile.write(outputstring)
    return True


def main(argv=None):
    # handle command line options
    formats = {
        ("po", "json"): ("json", convertjson),
    }
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.add_remove_translated_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
