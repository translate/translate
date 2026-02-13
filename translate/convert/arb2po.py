#
# Copyright 2026 Pere Orga <pere@orga.cat>
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
Convert ARB files to Gettext PO localization files.

ARB (Application Resource Bundle) is a JSON-based format used by Flutter
for app localization.
"""

import logging

from translate.convert import convert
from translate.storage import jsonl10n, po

logger = logging.getLogger(__name__)


class arb2po:
    """Convert an ARB file to a PO file."""

    def convert_store(self, input_store, duplicatestyle="msgctxt"):
        """Converts an ARB file to a PO file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote(f"extracted from {input_store.filename}", "developer")
        for input_unit in input_store.units:
            output_unit = self.convert_unit(input_unit, "developer")
            if output_unit is not None:
                output_store.addunit(output_unit)
        output_store.removeduplicates(duplicatestyle)
        return output_store

    def merge_store(
        self, template_store, input_store, blankmsgstr=False, duplicatestyle="msgctxt"
    ):
        """Converts two ARB files to a PO file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote(
            f"extracted from {template_store.filename}, {input_store.filename}",
            "developer",
        )

        input_store.makeindex()
        for template_unit in template_store.units:
            origpo = self.convert_unit(template_unit, "developer")
            # try and find a translation of the same name...
            template_unit_name = "".join(template_unit.getlocations())
            if template_unit_name in input_store.locationindex:
                translatedarb = input_store.locationindex[template_unit_name]
                translatedpo = self.convert_unit(translatedarb, "translator")
            else:
                translatedpo = None
            # if we have a valid po unit, get the translation and add it...
            if origpo is not None:
                if translatedpo is not None and not blankmsgstr:
                    origpo.target = translatedpo.source
                output_store.addunit(origpo)
            elif translatedpo is not None:
                logger.error("error converting original ARB definition %s", origpo.name)
        output_store.removeduplicates(duplicatestyle)
        return output_store

    @staticmethod
    def convert_unit(input_unit, commenttype):
        """
        Converts an ARB unit to a PO unit.

        :return: None if empty or header unit (@@locale etc.)
        """
        if input_unit is None or input_unit.isheader():
            return None
        output_unit = po.pounit(encoding="UTF-8")
        output_unit.addlocation(input_unit.getid())
        output_unit.addnote(input_unit.getnotes(), commenttype)
        output_unit.source = input_unit.source
        output_unit.target = ""
        return output_unit


def convertarb(
    input_file,
    output_file,
    template_file,
    pot=False,
    duplicatestyle="msgctxt",
) -> int:
    """
    Reads in *input_file* using jsonl10n.ARBJsonFile, converts using
    :class:`arb2po`, writes to *output_file*.
    """
    input_store = jsonl10n.ARBJsonFile(input_file)
    convertor = arb2po()
    if template_file is None:
        output_store = convertor.convert_store(
            input_store, duplicatestyle=duplicatestyle
        )
    else:
        template_store = jsonl10n.ARBJsonFile(template_file)
        output_store = convertor.merge_store(
            template_store, input_store, blankmsgstr=pot, duplicatestyle=duplicatestyle
        )
    if output_store.isempty():
        return 0
    output_store.serialize(output_file)
    return 1


def main(argv=None) -> None:
    formats = {
        "arb": ("po", convertarb),
        ("arb", "arb"): ("po", convertarb),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, usepots=True, description=__doc__
    )
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == "__main__":
    main()
