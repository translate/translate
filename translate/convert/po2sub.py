#
# Copyright 2008-2009 Zuza Software Foundation
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

"""
Convert Gettext PO localization files to subtitle files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/sub2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po


class po2sub:
    def __init__(self, templatefile, inputstore, includefuzzy=False):
        from translate.storage import subtitles

        self.includefuzzy = includefuzzy
        self.templatefile = templatefile
        self.templatestore = subtitles.SubtitleFile(templatefile)
        self.inputstore = inputstore

    def convert_store(self):
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


def convertsub(
    inputfile, outputfile, templatefile, includefuzzy=False, outputthreshold=None
):
    if templatefile is None:
        raise ValueError("must have template file for subtitle files")

    inputstore = po.pofile(inputfile)
    if not convert.should_output_store(inputstore, outputthreshold):
        return 0

    convertor = po2sub(templatefile, inputstore, includefuzzy)
    outputstring = convertor.convert_store()
    outputfile.write(outputstring)
    return 1


formats = {
    ("po", "srt"): ("srt", convertsub),
    ("po", "sub"): ("sub", convertsub),
    ("po", "ssa"): ("ssa", convertsub),
    ("po", "ass"): ("ass", convertsub),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
