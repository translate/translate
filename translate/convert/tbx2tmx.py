#
# Copyright 2005, 2006 Zuza Software Foundation
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
Convert TBX glossaries to a TMX (Translation Memory eXchange) file.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tbx2tmx.html
for examples and usage instructions.
"""

from translate.convert.po2tmx import TmxOptionParser, tmxmultifile
from translate.storage import tbx


class tbx2tmx:
    def convertfiles(
        self, inputfile, tmxfile, sourcelanguage="en", targetlanguage=None
    ) -> None:
        """Add all selected-language term pairs to a shared TMX store."""
        inputstore = tbx.tbxfile(
            inputfile, sourcelanguage=sourcelanguage, targetlanguage=targetlanguage
        )
        tmxfile.setsourcelanguage(sourcelanguage)
        tmxfile.addheader()
        for unit in inputstore.units:
            if unit.isfuzzy():
                continue
            for source in unit.get_source_terms():
                if not source.text or source.deprecated:
                    continue
                for target in unit.get_target_terms():
                    if not target.text or target.deprecated:
                        continue
                    notes = dict.fromkeys(
                        note.text for note in source.notes + target.notes if note.text
                    )
                    tmxfile.addtranslation(
                        source.text,
                        sourcelanguage,
                        target.text,
                        targetlanguage,
                        "\n".join(notes),
                    )


def converttbx(
    inputfile, outputfile, templatefile, sourcelanguage="en", targetlanguage=None
) -> int:
    """Read TBX and add its translations to the output archive."""
    tbx2tmx().convertfiles(
        inputfile, outputfile.tmxfile, sourcelanguage, targetlanguage
    )
    return 1


def main(argv=None) -> None:
    formats = {"tbx": ("tmx", converttbx)}
    archiveformats = {(None, "output"): tmxmultifile}
    parser = TmxOptionParser(
        formats,
        usepots=False,
        usetemplates=False,
        description=__doc__,
        archiveformats=archiveformats,
    )
    parser.add_option(
        "-l",
        "--language",
        dest="targetlanguage",
        default=None,
        help="set target language code (e.g. af-ZA) [required]",
        metavar="LANG",
    )
    parser.add_option(
        "",
        "--source-language",
        dest="sourcelanguage",
        default="en",
        help="set source language code (default: en)",
        metavar="LANG",
    )
    parser.passthrough.extend(["sourcelanguage", "targetlanguage"])
    parser.run(argv)


if __name__ == "__main__":
    main()
