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

"""Convert Gettext PO localization files to .ini files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ini2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ini, po


class po2ini(object):
    """Convert a PO file and a template INI file to a INI file."""

    def __init__(self, templatefile, inputstore, dialect="default"):
        """Initialize the converter."""
        self.templatestore = ini.inifile(templatefile, dialect=dialect)
        self.inputstore = inputstore

    def merge_stores(self, includefuzzy=False):
        """Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
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
        return bytes(self.templatestore)


def run_converter(inputfile, outputfile, templatefile, includefuzzy=False,
                  dialect="default", outputthreshold=None):
    """Wrapper around converter."""
    if templatefile is None:
        raise ValueError("must have template file for ini files")

    inputstore = po.pofile(inputfile)
    if not convert.should_output_store(inputstore, outputthreshold):
        return 0

    convertor = po2ini(templatefile, inputstore, dialect)
    outputstring = convertor.merge_stores(includefuzzy)
    outputfile.write(outputstring)
    return 1


def convertisl(inputfile, outputfile, templatefile, includefuzzy=False,
               dialect="inno", outputthreshold=None):
    run_converter(inputfile, outputfile, templatefile, includefuzzy, dialect,
                  outputthreshold)


formats = {
    ("po", "ini"): ("ini", run_converter),
    ("po", "isl"): ("isl", convertisl),
}


def main(argv=None):
    import sys
    if sys.version_info[0] == 3:
        print("Translate Toolkit doesn't yet support converting to INI in "
              "Python 3.")
        sys.exit()

    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
