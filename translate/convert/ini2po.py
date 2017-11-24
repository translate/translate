# -*- coding: utf-8 -*-
#
# Copyright 2007 Zuza Software Foundation
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

"""Convert .ini files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ini2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ini, po


class ini2po(object):
    """Convert one or two INI files to a single PO file."""

    def __init__(self, duplicate_style="msgctxt"):
        """Initialize the converter."""
        self.duplicate_style = duplicate_style

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = po.pounit(encoding="UTF-8")
        target_unit.addlocation("".join(unit.getlocations()))
        target_unit.source = unit.source
        target_unit.target = ""
        return target_unit

    def convert_store(self, input_store):
        """Convert a single source format file to a target format file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote("extracted from %s" % input_store.filename,
                              "developer")

        for input_unit in input_store.units:
            output_unit = self.convert_unit(input_unit)
            if output_unit is not None:
                output_store.addunit(output_unit)
        output_store.removeduplicates(self.duplicate_style)
        return output_store

    def merge_stores(self, template_store, input_store, blankmsgstr=False):
        """Convert two source format files to a target format file."""
        output_store = po.pofile()
        output_header = output_store.header()
        note = "extracted from %s, %s" % (template_store.filename,
                                          input_store.filename)
        output_header.addnote(note, "developer")

        input_store.makeindex()
        for template_unit in template_store.units:
            origpo = self.convert_unit(template_unit)
            # Try and find a translation of the same name...
            template_unit_name = "".join(template_unit.getlocations())
            add_translation = (
                not blankmsgstr and
                template_unit_name in input_store.locationindex)
            if add_translation:
                translatedini = input_store.locationindex[template_unit_name]
                origpo.target = translatedini.source
            output_store.addunit(origpo)
        output_store.removeduplicates(self.duplicate_style)
        return output_store


def run_converter(input_file, output_file, template_file=None, pot=False,
                  duplicatestyle="msgctxt", dialect="default"):
    """Wrapper around converter."""
    input_store = ini.inifile(input_file, dialect=dialect)
    convertor = ini2po(duplicate_style=duplicatestyle)
    if template_file is None:
        output_store = convertor.convert_store(input_store)
    else:
        template_store = ini.inifile(template_file, dialect=dialect)
        output_store = convertor.merge_stores(template_store, input_store,
                                              blankmsgstr=pot)
    if output_store.isempty():
        return 0
    output_store.serialize(output_file)
    return 1


def convertisl(input_file, output_file, template_file=None, pot=False,
               duplicatestyle="msgctxt", dialect="inno"):
    return run_converter(input_file, output_file, template_file, pot,
                         duplicatestyle, dialect)


formats = {
    "ini": ("po", run_converter),
    ("ini", "ini"): ("po", run_converter),
    "isl": ("po", convertisl),
    ("isl", "isl"): ("po", convertisl),
    "iss": ("po", convertisl),
    ("iss", "iss"): ("po", convertisl),
}


def main(argv=None):
    import sys
    if sys.version_info[0] == 3:
        print("Translate Toolkit doesn't yet support converting from INI in "
              "Python 3.")
        sys.exit()

    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
