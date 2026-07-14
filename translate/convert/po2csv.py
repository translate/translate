#
# Copyright 2003-2006 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""
Convert Gettext PO localization files to Comma-Separated Value (.csv) files.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/csv2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import csvl10n, po


class po2csv:
    @staticmethod
    def convertcomments(inputunit):
        return " ".join(inputunit.getlocations())

    def convertunit(self, inputunit):
        if inputunit.isheader():
            return None
        if inputunit.isblank():
            return None
        csvunit = csvl10n.csvunit()
        csvunit.location = self.convertcomments(inputunit)
        csvunit.source = inputunit.source
        csvunit.target = inputunit.target
        csvunit.setcontext(inputunit.getcontext())
        return csvunit

    def convertplurals(self, inputunit):
        """
        Convert PO plural units.

        We only convert the first plural form.  So languages with multiple
        plurals are not handled.  For single plural languages we simply
        skip this plural extraction.
        """
        if len(inputunit.target.strings) == 1:  # No plural forms
            return None
        csvunit = csvl10n.csvunit()
        csvunit.location = self.convertcomments(inputunit)
        csvunit.source = inputunit.source.strings[1]
        csvunit.target = inputunit.target.strings[1]
        return csvunit

    def convertstore(self, inputstore, columnorder=None, escape_formulas=True):
        if columnorder is None:
            columnorder = ["location", "source", "target"]
        outputstore = csvl10n.csvfile(
            fieldnames=columnorder, escape_formulas=escape_formulas
        )
        for inputunit in inputstore.units:
            outputunit = self.convertunit(inputunit)
            if outputunit is not None:
                outputstore.addunit(outputunit)
            if inputunit.hasplural():
                outputunit = self.convertplurals(inputunit)
                if outputunit is not None:
                    outputstore.addunit(outputunit)
        return outputstore


def convertcsv(
    inputfile, outputfile, templatefile, columnorder=None, escape_formulas=True
) -> int:
    """Reads in inputfile using po, converts using po2csv, writes to outputfile."""
    # note that templatefile is not used, but it is required by the converter...
    inputstore = po.pofile(inputfile)
    if inputstore.isempty():
        return 0
    convertor = po2csv()
    outputstore = convertor.convertstore(inputstore, columnorder, escape_formulas)
    outputstore.serialize(outputfile)
    return 1


def columnorder_callback(option, opt, value, parser) -> None:
    setattr(parser.values, option.dest, value.split(","))


def main(argv=None) -> None:
    formats = {"po": ("csv", convertcsv)}
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.add_option(
        "",
        "--columnorder",
        dest="columnorder",
        action="callback",
        callback=columnorder_callback,
        type="str",
        default=None,
        help="specify the order and position of columns (location,source,target,context)",
    )
    parser.add_option(
        "",
        "--escape-formulas",
        dest="escape_formulas",
        action="store_true",
        default=True,
        help="escape spreadsheet formula-like values in CSV output (default)",
    )
    parser.add_option(
        "",
        "--no-escape-formulas",
        dest="escape_formulas",
        action="store_false",
        help="preserve spreadsheet formula-like values in CSV output",
    )
    parser.passthrough.append("columnorder")
    parser.passthrough.append("escape_formulas")
    parser.run(argv)


if __name__ == "__main__":
    main()
