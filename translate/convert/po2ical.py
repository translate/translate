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

"""Convert Gettext PO localization files to iCalendar files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ical2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ical, po


class po2ical(object):
    """Convert a PO file and a template iCalendar file to a iCalendar file."""

    TargetStoreClass = ical.icalfile

    def __init__(self, templatefile, inputstore, include_fuzzy=False):
        """Initialize the converter."""
        self.include_fuzzy = include_fuzzy
        self.templatefile = templatefile
        self.templatestore = self.TargetStoreClass(templatefile)
        self.inputstore = inputstore

    def convertstore(self):
        """Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            for location in unit.getlocations():
                if location in self.inputstore.locationindex:
                    inputunit = self.inputstore.locationindex[location]
                    if inputunit.isfuzzy() and not self.include_fuzzy:
                        unit.target = unit.source
                    else:
                        unit.target = inputunit.target
                else:
                    unit.target = unit.source
        return bytes(self.templatestore)


def convertical(inputfile, outputfile, templatefile, includefuzzy=False,
                outputthreshold=None):
    """Wrapper around converter."""
    inputstore = po.pofile(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    if templatefile is None:
        raise ValueError("must have template file for iCal files")
    else:
        convertor = po2ical(templatefile, inputstore, includefuzzy)
    outputstring = convertor.convertstore()
    outputfile.write(outputstring)
    return 1


formats = {
    ("po", "ics"): ("ics", convertical)
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
