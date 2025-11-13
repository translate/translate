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

"""
Builds a new translation file with the target of the input language as
source language.

.. note:: Ensure that the two po files correspond 100% to the same pot file before using
   this.

To translate Kurdish (ku) through French::

    poswap -i fr/ -t ku -o fr-ku

To convert the fr-ku files back to en-ku::

    poswap --reverse -i fr/ -t fr-ku -o en-ku

To translate Quechua (qu) through Spanish (es) using intermediate mode::

    poswap --intermediate -t en/ es/ es-qu/

Intermediate mode keeps the original source language (English) and adds the
intermediate language translation (Spanish) as a translator comment, making it
easier to translate through an intermediate language while keeping both
languages visible.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/poswap.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po


def swapdir(store):
    """Swap the source and target of each unit."""
    for unit in store.units:
        if unit.isheader():
            continue
        if not unit.target or unit.isfuzzy():
            unit.target = unit.source
        else:
            unit.source, unit.target = unit.target, unit.source


def add_missing_translation_note(unit, inputpo):
    """Add a note indicating no translation was found."""
    if inputpo.filename:
        unit.addnote(f"No translation found in {inputpo.filename}", origin="programmer")
    else:
        unit.addnote(
            "No translation found in the supplied source language",
            origin="programmer",
        )


def convertpo(inputpofile, outputpotfile, template, reverse=False, intermediate=False):
    """Reads in inputpofile, removes the header, writes to outputpotfile."""
    inputpo = po.pofile(inputpofile)
    templatepo = po.pofile(template)
    if reverse:
        swapdir(inputpo)
    templatepo.makeindex()
    header = inputpo.header()
    if header:
        inputpo.units = inputpo.units[1:]

    for i, unit in enumerate(inputpo.units):
        for location in unit.getlocations():
            templateunit = templatepo.locationindex.get(location)
            if templateunit and templateunit.source == unit.source:
                break
        else:
            templateunit = templatepo.findunit(unit.source)

        unit.othercomments = []
        if intermediate:
            # In intermediate mode, keep original source and add target as translator comment
            if unit.target and not unit.isfuzzy():
                unit.addnote(unit.target, origin="translator")
            elif not reverse:
                add_missing_translation_note(unit, inputpo)
        # Original behavior: swap target to source
        elif unit.target and not unit.isfuzzy():
            unit.source = unit.target
        elif not reverse:
            add_missing_translation_note(unit, inputpo)
        unit.target = ""
        unit.markfuzzy(False)
        if templateunit:
            unit.addnote(templateunit.getnotes(origin="translator"))
            unit.markfuzzy(templateunit.isfuzzy())
            unit.target = templateunit.target
        if unit.isobsolete():
            # TODO: should not modify loop variable
            del inputpo.units[i]  # noqa: B909
    inputpo.serialize(outputpotfile)
    return 1


def main(argv=None):
    formats = {
        ("po", "po"): ("po", convertpo),
        ("po", "pot"): ("po", convertpo),
        "po": ("po", convertpo),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_option(
        "",
        "--reverse",
        dest="reverse",
        default=False,
        action="store_true",
        help="reverse the process of intermediate language conversion",
    )
    parser.add_option(
        "",
        "--intermediate",
        dest="intermediate",
        default=False,
        action="store_true",
        help="use intermediate language mode: keep original source and add target as translator comment",
    )
    parser.passthrough.append("reverse")
    parser.passthrough.append("intermediate")
    parser.run(argv)


if __name__ == "__main__":
    main()
