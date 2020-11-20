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

"""Convert subtitle files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/sub2po.html
for examples and usage instructions.
"""

import logging

from translate.storage import po


logger = logging.getLogger(__name__)


def convert_store(input_store, duplicatestyle="msgctxt"):
    """converts a subtitle file to a .po file..."""
    output_store = po.pofile()
    output_header = output_store.header()
    output_header.addnote("extracted from %s" % input_store.filename, "developer")

    for input_unit in input_store.units:
        output_unit = convert_unit(input_unit, "developer")
        if output_unit is not None:
            output_store.addunit(output_unit)
    output_store.removeduplicates(duplicatestyle)
    return output_store


def merge_store(
    template_store, input_store, blankmsgstr=False, duplicatestyle="msgctxt"
):
    """converts two subtitle files to a .po file..."""
    output_store = po.pofile()
    output_header = output_store.header()
    output_header.addnote(
        f"extracted from {template_store.filename}, {input_store.filename}",
        "developer",
    )

    input_store.makeindex()
    for template_unit in template_store.units:
        origpo = convert_unit(template_unit, "developer")
        # try and find a translation of the same name...
        template_unit_name = "".join(template_unit.getlocations())
        if template_unit_name in input_store.locationindex:
            translatedini = input_store.locationindex[template_unit_name]
            translatedpo = convert_unit(translatedini, "translator")
        else:
            translatedpo = None
        # if we have a valid po unit, get the translation and add it...
        if origpo is not None:
            if translatedpo is not None and not blankmsgstr:
                origpo.target = translatedpo.source
            output_store.addunit(origpo)
        elif translatedpo is not None:
            logger.error(
                "error converting original subtitle definition %s", origpo.name
            )
    output_store.removeduplicates(duplicatestyle)
    return output_store


def convert_unit(input_unit, commenttype):
    """Converts a subtitle unit to a .po unit. Returns None if empty or not for
    translation.
    """
    if input_unit is None:
        return None
    # escape unicode
    output_unit = po.pounit(encoding="UTF-8")
    output_unit.addlocation("".join(input_unit.getlocations()))
    output_unit.addnote(input_unit.getnotes("developer"), "developer")
    output_unit.source = input_unit.source
    output_unit.target = ""
    return output_unit


def convertsub(
    input_file, output_file, template_file=None, pot=False, duplicatestyle="msgctxt"
):
    """Reads in *input_file* using translate.subtitles, converts using
    :class:`sub2po`, writes to *output_file*.
    """
    from translate.storage import subtitles

    input_store = subtitles.SubtitleFile(input_file)
    if template_file is None:
        output_store = convert_store(input_store, duplicatestyle=duplicatestyle)
    else:
        template_store = subtitles.SubtitleFile(template_file)
        output_store = merge_store(
            template_store, input_store, blankmsgstr=pot, duplicatestyle=duplicatestyle
        )
    if output_store.isempty():
        return 0
    output_store.serialize(output_file)
    return 1


def main(argv=None):
    from translate.convert import convert

    formats = {
        "srt": ("po", convertsub),
        ("srt", "srt"): ("po", convertsub),
        "sub": ("po", convertsub),
        ("sub", "sub"): ("po", convertsub),
        "ssa": ("po", convertsub),
        ("ssa", "ssa"): ("po", convertsub),
        "ass": ("po", convertsub),
        ("ass", "ass"): ("po", convertsub),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, usepots=True, description=__doc__
    )
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == "__main__":
    main()
