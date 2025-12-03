#
# Copyright 2004-2006 Zuza Software Foundation
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
Convert Gettext PO localization files to Qt Linguist (.ts) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ts2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.misc.multistring import multistring
from translate.storage import po, ts2


class po2ts:
    @staticmethod
    def _merge_plural_forms(singular, plural):
        """
        Merge singular and plural forms into (s) notation for TS format.

        For example: "item" and "items" becomes "item(s)"
                     "day ago" and "days ago" becomes "day(s) ago"
        Returns the merged form if possible, otherwise returns the plural form.

        Note: This is necessary because the Qt Linguist TS format does not support
        separate singular and plural source forms like Gettext PO does. As a result,
        we merge the forms into a single string using (s) notation where possible.
        """
        if not singular or not plural:
            return plural or singular

        # Try to find where they differ
        min_len = min(len(singular), len(plural))

        # Find the first difference
        first_diff = min_len
        for i in range(min_len):
            if singular[i] != plural[i]:
                first_diff = i
                break

        # If they're identical up to the end of the shorter string
        if first_diff == min_len:
            # Check if plural is just singular + 's'
            if len(plural) == len(singular) + 1 and plural == singular + "s":
                return f"{singular}(s)"
            # Check if plural is just singular + 'es'
            if len(plural) == len(singular) + 2 and plural == singular + "es":
                return f"{singular}(es)"
        # They differ somewhere in the middle
        # Check if the difference is just an 's' insertion
        # e.g., "day ago" vs "days ago"
        elif (
            len(plural) == len(singular) + 1
            and singular[:first_diff] == plural[:first_diff]
            and plural[first_diff] == "s"
            and singular[first_diff:] == plural[first_diff + 1 :]
        ):
            return f"{plural[:first_diff]}(s){plural[first_diff + 1 :]}"

        # If we can't merge intelligently, return the plural form
        return plural

    @staticmethod
    def convertstore(inputstore, outputfile, templatefile=None, context=None):
        """Converts a .po file to .ts format (using a template .ts file if given)."""
        tsfile = ts2.tsfile() if templatefile is None else ts2.tsfile(templatefile)
        for inputunit in inputstore.units:
            if inputunit.isheader() or inputunit.isblank():
                continue
            source = inputunit.source
            # For plural forms, merge singular and plural into (s) notation
            if inputunit.hasplural() and isinstance(source, multistring):
                if len(source.strings) > 1:
                    singular = source.strings[0]
                    plural = source.strings[1]
                    source = po2ts._merge_plural_forms(singular, plural)
                elif len(source.strings) == 1:
                    source = source.strings[0]
                # If strings is empty, source remains as multistring (will be handled by tsunit)
            translation = inputunit.target
            comment = inputunit.getnotes("translator")
            for sourcelocation in inputunit.getlocations():
                if context is None:
                    if "#" in sourcelocation:
                        contextname = sourcelocation[: sourcelocation.find("#")]
                    else:
                        contextname = sourcelocation
                else:
                    contextname = context
                tsunit = ts2.tsunit(source)
                tsunit.target = translation
                if not inputunit.istranslated():
                    tsunit.markfuzzy()
                elif inputunit.getnotes("developer") == "(obsolete)":
                    tsunit.set_state_n(tsunit.S_OBSOLETE)
                tsfile.addunit(tsunit, True, contextname, comment, True)
        tsfile.serialize(outputfile)


def convertpo(inputfile, outputfile, templatefile, context):
    """Reads in stdin using fromfileclass, converts using convertorclass, writes to stdout."""
    inputstore = po.pofile(inputfile)
    if inputstore.isempty():
        return 0
    convertor = po2ts()
    convertor.convertstore(inputstore, outputfile, templatefile, context)
    return 1


def main(argv=None):
    formats = {"po": ("ts", convertpo), ("po", "ts"): ("ts", convertpo)}
    parser = convert.ConvertOptionParser(
        formats, usepots=False, usetemplates=True, description=__doc__
    )
    parser.add_option(
        "-c",
        "--context",
        dest="context",
        default=None,
        help="use supplied context instead of the one in the .po file comment",
    )
    parser.passthrough.append("context")
    parser.run(argv)


if __name__ == "__main__":
    main()
