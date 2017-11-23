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

"""Convert iCalendar files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ical2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ical, po


class ical2po(object):
    """Convert one or two iCalendar files to a single PO file."""

    def convert_store(self, input_store, duplicatestyle="msgctxt"):
        """Convert a single source format file to a target format file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote("extracted from %s" % input_store.filename, "developer")
        for input_unit in input_store.units:
            output_store.addunit(self.convert_unit(input_unit))
        output_store.removeduplicates(duplicatestyle)
        return output_store

    def merge_stores(self, template_store, input_store, blankmsgstr=False,
                     duplicatestyle="msgctxt"):
        """Convert two source format files to a target format file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote("extracted from %s, %s" % (template_store.filename, input_store.filename), "developer")

        input_store.makeindex()
        for template_unit in template_store.units:
            origpo = self.convert_unit(template_unit)
            # try and find a translation of the same name...
            template_unit_name = "".join(template_unit.getlocations())
            add_translation = (not blankmsgstr and
                               template_unit_name in input_store.locationindex)
            if add_translation:
                translatedini = input_store.locationindex[template_unit_name]
                origpo.target = translatedini.source
            output_store.addunit(origpo)
        output_store.removeduplicates(duplicatestyle)
        return output_store

    def convert_unit(self, input_unit):
        """Convert a source format unit to a target format unit."""
        output_unit = po.pounit(encoding="UTF-8")
        output_unit.addlocation("".join(input_unit.getlocations()))
        output_unit.addnote(input_unit.getnotes("developer"), "developer")
        output_unit.source = input_unit.source
        output_unit.target = ""
        return output_unit


def convertical(input_file, output_file, template_file, pot=False, duplicatestyle="msgctxt"):
    """Wrapper around converter."""
    input_store = ical.icalfile(input_file)
    convertor = ical2po()
    if template_file is None:
        output_store = convertor.convert_store(input_store, duplicatestyle=duplicatestyle)
    else:
        template_store = ical.icalfile(template_file)
        output_store = convertor.merge_stores(template_store, input_store,
                                              blankmsgstr=pot,
                                              duplicatestyle=duplicatestyle)
    if output_store.isempty():
        return 0
    output_store.serialize(output_file)
    return 1


def main(argv=None):
    formats = {"ics": ("po", convertical), ("ics", "ics"): ("po", convertical)}
    parser = convert.ConvertOptionParser(formats, usetemplates=True, usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
