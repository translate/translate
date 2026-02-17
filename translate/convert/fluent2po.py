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
Convert Fluent files to Gettext PO localization files.

Fluent is a monolingual localization format used by Mozilla Firefox, Anki,
and other projects.
"""

from translate.convert import convert
from translate.storage import fluent, po


class fluent2po:
    """Convert a Fluent file to a PO file."""

    def convert_store(self, input_store, duplicatestyle="msgctxt"):
        """Converts a single Fluent file to a PO file."""
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
        """Converts two Fluent files (template + translation) to a PO file."""
        output_store = po.pofile()
        output_header = output_store.header()
        output_header.addnote(
            f"extracted from {template_store.filename}, {input_store.filename}",
            "developer",
        )

        # Build an index by unit ID since FluentUnit doesn't use locations.
        input_index = {}
        for unit in input_store.units:
            uid = unit.getid()
            if uid is not None:
                input_index[uid] = unit

        for template_unit in template_store.units:
            origpo = self.convert_unit(template_unit, "developer")
            if origpo is None:
                continue
            # try and find a translation of the same name...
            template_unit_id = template_unit.getid()
            if template_unit_id in input_index:
                translatedfluent = input_index[template_unit_id]
                translatedpo = self.convert_unit(translatedfluent, "translator")
            else:
                translatedpo = None
            if translatedpo is not None and not blankmsgstr:
                origpo.target = translatedpo.source
            output_store.addunit(origpo)
        output_store.removeduplicates(duplicatestyle)
        return output_store

    @staticmethod
    def convert_unit(input_unit, commenttype):
        """
        Converts a Fluent unit to a PO unit.

        :return: None if the unit is a comment-only header (ResourceComment,
            GroupComment, DetachedComment), or is not translatable.
        """
        if (
            input_unit is None
            or input_unit.isheader()
            or not input_unit.istranslatable()
        ):
            return None
        output_unit = po.pounit(encoding="UTF-8")
        output_unit.addlocation(input_unit.getid())
        output_unit.addnote(input_unit.getnotes(), commenttype)
        output_unit.source = input_unit.source
        output_unit.target = ""
        return output_unit


def convertfluent(
    input_file,
    output_file,
    template_file,
    pot=False,
    duplicatestyle="msgctxt",
) -> int:
    """
    Reads in *input_file* using fluent.FluentFile, converts using
    :class:`fluent2po`, writes to *output_file*.
    """
    input_store = fluent.FluentFile(input_file)
    convertor = fluent2po()
    if template_file is None:
        output_store = convertor.convert_store(
            input_store, duplicatestyle=duplicatestyle
        )
    else:
        template_store = fluent.FluentFile(template_file)
        output_store = convertor.merge_store(
            template_store, input_store, blankmsgstr=pot, duplicatestyle=duplicatestyle
        )
    if output_store.isempty():
        return 0
    output_store.serialize(output_file)
    return 1


def main(argv=None) -> None:
    formats = {
        "ftl": ("po", convertfluent),
        ("ftl", "ftl"): ("po", convertfluent),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, usepots=True, description=__doc__
    )
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == "__main__":
    main()
