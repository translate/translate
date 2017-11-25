# -*- coding: utf-8 -*-
#
# Copyright 2008 Mozilla Corporation, Zuza Software Foundation
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

"""Convert TikiWiki's language.php files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tiki2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, tiki


class tiki2po(object):
    """Convert one or two TikiWiki's language.php files to a single PO file."""

    def __init__(self, include_unused=False):
        """Initialize the converter."""
        self.include_unused = include_unused

    def convert_store(self, thetikifile):
        """Convert a single source format file to a target format file."""
        thetargetfile = po.pofile()

        for unit in thetikifile.units:
            if not self.include_unused and "unused" in unit.getlocations():
                continue
            newunit = po.pounit()
            newunit.source = unit.source
            newunit.target = unit.target
            locations = unit.getlocations()
            if locations:
                newunit.addlocations(locations)
            thetargetfile.addunit(newunit)
        return thetargetfile


def run_converter(inputfile, outputfile, template=None, includeunused=False):
    """Wrapper around converter."""
    convertor = tiki2po(includeunused)
    inputstore = tiki.TikiStore(inputfile)
    outputstore = convertor.convert_store(inputstore)
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


formats = {
    "php": ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.add_option("", "--include-unused", dest="includeunused",
                      action="store_true", default=False,
                      help="Include strings in the unused section")
    parser.passthrough.append("includeunused")
    parser.run(argv)


if __name__ == '__main__':
    main()
