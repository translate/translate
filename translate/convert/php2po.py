# -*- coding: utf-8 -*-
#
# Copyright 2002-2013 Zuza Software Foundation
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

"""Convert PHP localization files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/php2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import php, po


class php2po(object):
    """Convert one or two PHP files to a single PO file."""

    TargetUnitClass = po.pounit

    def __init__(self, blank_msgstr=False, duplicate_style="msgctxt"):
        """Initialize the converter."""
        self.blank_msgstr = blank_msgstr
        self.duplicate_style = duplicate_style

    def convert_unit(self, unit, origin):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass(encoding="UTF-8")
        target_unit.addnote(unit.getnotes(origin), origin)
        target_unit.addlocation("".join(unit.getlocations()))
        target_unit.source = unit.source
        target_unit.target = ""
        return target_unit

    def convertstore(self, inputstore):
        """Convert a single source format file to a target format file."""
        outputstore = po.pofile()
        outputheader = outputstore.header()
        outputheader.addnote("extracted from %s" % inputstore.filename,
                             "developer")

        for inputunit in inputstore.units:
            outputunit = self.convert_unit(inputunit, "developer")
            if outputunit is not None:
                outputstore.addunit(outputunit)
        outputstore.removeduplicates(self.duplicate_style)
        return outputstore

    def mergestore(self, templatestore, inputstore):
        """Convert two source format files to a target format file."""
        outputstore = po.pofile()
        outputheader = outputstore.header()
        outputheader.addnote("extracted from %s, %s" % (templatestore.filename,
                                                        inputstore.filename),
                             "developer")

        inputstore.makeindex()
        # Loop through the original file, looking at units one by one.
        for templateunit in templatestore.units:
            outputunit = self.convert_unit(templateunit, "developer")
            # Try and find a translation of the same name.
            use_translation = (not self.blank_msgstr and
                               templateunit.name in inputstore.locationindex)
            if use_translation:
                translatedinputunit = inputstore.locationindex[templateunit.name]
                outputunit.target = translatedinputunit.source
            outputstore.addunit(outputunit)
        outputstore.removeduplicates(self.duplicate_style)
        return outputstore


def convertphp(inputfile, outputfile, templatefile, pot=False,
               duplicatestyle="msgctxt"):
    """Wrapper around converter."""
    inputstore = php.phpfile(inputfile)
    convertor = php2po(blank_msgstr=pot, duplicate_style=duplicatestyle)
    if templatefile is None:
        outputstore = convertor.convertstore(inputstore)
    else:
        templatestore = php.phpfile(templatefile)
        outputstore = convertor.mergestore(templatestore, inputstore)
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


formats = {
    "php": ("po", convertphp),
    ("php", "php"): ("po", convertphp),
    "html": ("po", convertphp),
    ("html", "html"): ("po", convertphp),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
