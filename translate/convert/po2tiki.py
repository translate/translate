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

"""Convert Gettext PO files to TikiWiki's language.php files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tiki2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, tiki


class po2tiki(object):
    """Convert a PO file and a template TikiWiki file to a TikiWiki file."""

    def convert_store(self, thepofile):
        """Convert a single source format file to a target format file."""
        thetargetfile = tiki.TikiStore()
        for unit in thepofile.units:
            if not (unit.isblank() or unit.isheader()):
                newunit = tiki.TikiUnit(unit.source)
                newunit.target = unit.target
                locations = unit.getlocations()
                if locations:
                    newunit.addlocations(locations)
                # If a word is "untranslated" but the target isn't empty and
                # isn't the same as the source it's been translated and we
                # switch it. This is an assumption but should remain true as
                # long as these scripts are used.
                change_location = (
                    newunit.getlocations() == ["untranslated"] and
                    unit.source != unit.target and
                    unit.target != "")
                if change_location:
                    newunit.location = []
                    newunit.addlocation("translated")

                thetargetfile.addunit(newunit)
        return thetargetfile


def run_converter(inputfile, outputfile, template=None):
    """Wrapper around converter."""
    inputstore = po.pofile(inputfile)
    if inputstore.isempty():
        return 0
    convertor = po2tiki()
    outputstore = convertor.convert_store(inputstore)
    outputstore.serialize(outputfile)
    return 1


formats = {
    "po": ("tiki", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == '__main__':
    main()
