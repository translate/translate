#
# Copyright 2003-2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Count strings and words for supported localization files.

These include: XLIFF, TMX, Gettex PO and MO, Qt .ts and .qm, Wordfast TM, etc

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pocount.html
for examples and usage instructions.
"""

import logging
import os
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict

from translate.lang.common import Common
from translate.misc.multistring import multistring
from translate.storage import factory
from translate.storage.workflow import StateEnum


extended_state_strings = {
    StateEnum.EMPTY: "empty",
    StateEnum.NEEDS_WORK: "needs-work",
    StateEnum.REJECTED: "rejected",
    StateEnum.NEEDS_REVIEW: "needs-review",
    StateEnum.UNREVIEWED: "unreviewed",
    StateEnum.FINAL: "final",
}

UNTRANSLATED = StateEnum.EMPTY
FUZZY = StateEnum.NEEDS_WORK
TRANSLATED = StateEnum.UNREVIEWED

state_strings = {
    UNTRANSLATED: "untranslated",
    FUZZY: "fuzzy",
    TRANSLATED: "translated",
}

logger = logging.getLogger(__name__)

# define style constants
style_full, style_csv, style_short_strings, style_short_words = range(4)

# default output style
default_style = style_full

# kdepluralre = re.compile("^_n: ") #Restore this if you really need support for old kdeplurals
brtagre = re.compile(r"<br\s*?/?>")
# xmltagre is a direct copy of the from placeables/general.py
xmltagre = re.compile(
    r"""
        <                         # start of opening tag
        ([\w.:]+)                 # tag name, possibly namespaced
        (\s([\w.:]+=              # space and attribute name followed by =
            ((".*?")|('.*?'))     # attribute value, single or double quoted
        )?)*/?>                   # end of opening tag, possibly self closing
        |</([\w.]+)>              # or a closing tag
        """,
    re.VERBOSE,
)
numberre = re.compile("\\D\\.\\D")


class ConsoleColor:
    """Class to implement color mode."""

    # print using color? Default to true
    color_mode = True
    COLOR_PURPLE = "\033[95m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RED = "\033[91m"
    COLOR_DEFAULT = "\033[0m"

    @classmethod
    def HEADER(cls):
        return cls.COLOR_PURPLE if ConsoleColor.color_mode else ""

    @classmethod
    def OKGREEN(cls):
        return cls.COLOR_GREEN if ConsoleColor.color_mode else ""

    @classmethod
    def WARNING(cls):
        return cls.COLOR_YELLOW if ConsoleColor.color_mode else ""

    @classmethod
    def FAIL(cls):
        return cls.COLOR_RED if ConsoleColor.color_mode else ""

    @classmethod
    def ENDC(cls):
        return cls.COLOR_DEFAULT if ConsoleColor.color_mode else ""


def wordcount(string):
    # TODO: po class should understand KDE style plurals ##
    # string = kdepluralre.sub("", string) #Restore this if you really need support for old kdeplurals
    string = brtagre.sub("\n", string)
    string = xmltagre.sub("", string)
    string = numberre.sub(" ", string)
    # TODO: This should still use the correct language to count in the target
    # language
    return len(Common.words(string))


def wordsinunit(unit):
    """Counts the words in the unit's source and target, taking plurals into
    account. The target words are only counted if the unit is translated.
    """
    (sourcewords, targetwords) = (0, 0)
    if isinstance(unit.source, multistring):
        sourcestrings = unit.source.strings
    else:
        sourcestrings = [unit.source or ""]
    for s in sourcestrings:
        sourcewords += wordcount(s)
    if not unit.istranslated():
        return sourcewords, targetwords
    if isinstance(unit.target, multistring):
        targetstrings = unit.target.strings
    else:
        targetstrings = [unit.target or ""]
    for s in targetstrings:
        targetwords += wordcount(s)
    return sourcewords, targetwords


def calcstats(filename):
    """This is the previous implementation of calcstats() and is left for
    comparison and debuging purposes.
    """
    # ignore totally blank or header units
    try:
        store = factory.getobject(filename)
    except ValueError as e:
        logger.warning(e)
        return {}

    units = [unit for unit in store.units if unit.istranslatable()]
    translated = translatedmessages(units)
    fuzzy = fuzzymessages(units)
    review = [unit for unit in units if unit.isreview()]
    untranslated = untranslatedmessages(units)
    wordcounts = {id(unit): wordsinunit(unit) for unit in units}
    sourcewords = lambda elementlist: sum(
        wordcounts[id(unit)][0] for unit in elementlist
    )
    targetwords = lambda elementlist: sum(
        wordcounts[id(unit)][1] for unit in elementlist
    )
    stats = {}

    # units
    stats["translated"] = len(translated)
    stats["fuzzy"] = len(fuzzy)
    stats["untranslated"] = len(untranslated)
    stats["review"] = len(review)
    stats["total"] = stats["translated"] + stats["fuzzy"] + stats["untranslated"]

    # words
    stats["translatedsourcewords"] = sourcewords(translated)
    stats["translatedtargetwords"] = targetwords(translated)
    stats["fuzzysourcewords"] = sourcewords(fuzzy)
    stats["untranslatedsourcewords"] = sourcewords(untranslated)
    stats["reviewsourcewords"] = sourcewords(review)
    stats["totalsourcewords"] = (
        stats["translatedsourcewords"]
        + stats["fuzzysourcewords"]
        + stats["untranslatedsourcewords"]
    )

    stats["extended"] = file_extended_totals(units, wordcounts)

    return stats


def file_extended_totals(units, wordcounts):
    """
    Provide extended statuses (used by XLIFF)
    """

    stats = {}

    for unit in units:
        state = unit.get_state_n()

        # if state is not standard (xliff)
        # search for the default one to use
        # each unit defines its own states
        if state not in extended_state_strings:
            for k in unit.STATE.keys():
                val = unit.STATE[k]
                if val[0] <= int(state.__str__()) <= val[1]:
                    state = k

        extended_state = extended_state_strings[state]

        state_stats = stats.get(extended_state, defaultdict(int))
        state_stats["units"] += 1
        state_stats["sourcewords"] += wordcounts[id(unit)][0]
        state_stats["targetwords"] += wordcounts[id(unit)][1]

        stats[extended_state] = state_stats

    return stats


def summarize(title, stats, style=style_full, indent=8, incomplete_only=False):
    """Print summary for a .po file in specified format.

    :param title: name of .po file
    :param stats: array with translation statistics for the file specified
    :param indent: indentation of the 2nd column (length of longest filename)
    :param incomplete_only: omit fully translated files
    :type incomplete_only: Boolean
    :rtype: Boolean
    :return: 1 if counting incomplete files (incomplete_only=True) and the
             file is completely translated, 0 otherwise
    """

    def percent(denominator, devisor):
        if devisor == 0:
            return 0
        else:
            return denominator * 100 / devisor

    if incomplete_only and (stats["total"] == stats["translated"]):
        return 1

    if style == style_csv:
        print("%s, " % title, end=" ")
        print(
            "%d, %d, %d,"
            % (
                stats["translated"],
                stats["translatedsourcewords"],
                stats["translatedtargetwords"],
            ),
            end=" ",
        )
        print("%d, %d," % (stats["fuzzy"], stats["fuzzysourcewords"]), end=" ")
        print(
            "%d, %d," % (stats["untranslated"], stats["untranslatedsourcewords"]),
            end=" ",
        )
        print("%d, %d" % (stats["total"], stats["totalsourcewords"]), end=" ")
        if stats["review"] > 0:
            print(", %d, %d" % (stats["review"], stats["reviewsourdcewords"]), end=" ")
        print()
    elif style == style_short_strings:
        spaces = " " * (indent - len(title))
        print(
            "%s%s strings: total: %d\t| %st\t%sf\t%su\t| %st\t%sf\t%su"
            % (
                ConsoleColor.HEADER() + title + ConsoleColor.ENDC(),
                spaces,
                stats["total"],
                ConsoleColor.OKGREEN() + str(stats["translated"]) + ConsoleColor.ENDC(),
                ConsoleColor.WARNING() + str(stats["fuzzy"]) + ConsoleColor.ENDC(),
                ConsoleColor.FAIL() + str(stats["untranslated"]) + ConsoleColor.ENDC(),
                ConsoleColor.OKGREEN()
                + str(percent(stats["translated"], stats["total"]))
                + "%"
                + ConsoleColor.ENDC(),
                ConsoleColor.WARNING()
                + str(percent(stats["fuzzy"], stats["total"]))
                + "%"
                + ConsoleColor.ENDC(),
                ConsoleColor.FAIL()
                + str(percent(stats["untranslated"], stats["total"]))
                + "%"
                + ConsoleColor.ENDC(),
            )
        )
    elif style == style_short_words:
        spaces = " " * (indent - len(title))
        print(
            "%s%s source words: total: %d\t| %st\t%sf\t%su\t| %st\t%sf\t%su"
            % (
                ConsoleColor.HEADER() + title + ConsoleColor.ENDC(),
                spaces,
                stats["totalsourcewords"],
                ConsoleColor.OKGREEN()
                + str(stats["translatedsourcewords"])
                + ConsoleColor.ENDC(),
                ConsoleColor.WARNING()
                + str(stats["fuzzysourcewords"])
                + ConsoleColor.ENDC(),
                ConsoleColor.FAIL()
                + str(stats["untranslatedsourcewords"])
                + ConsoleColor.ENDC(),
                ConsoleColor.OKGREEN()
                + str(
                    percent(stats["translatedsourcewords"], stats["totalsourcewords"])
                )
                + "%"
                + ConsoleColor.ENDC(),
                ConsoleColor.WARNING()
                + str(percent(stats["fuzzysourcewords"], stats["totalsourcewords"]))
                + "%"
                + ConsoleColor.ENDC(),
                ConsoleColor.FAIL()
                + str(
                    percent(stats["untranslatedsourcewords"], stats["totalsourcewords"])
                )
                + "%"
                + ConsoleColor.ENDC(),
            )
        )
    else:  # style == style_full
        print(
            "Processing file : " + ConsoleColor.HEADER() + title + ConsoleColor.ENDC()
        )
        print("Type               Strings      Words (source)    Words (translation)")
        print(
            ConsoleColor.OKGREEN()
            + "Translated:   %5d (%3d%%) %10d (%3d%%) %15d"
            % (
                stats["translated"],
                percent(stats["translated"], stats["total"]),
                stats["translatedsourcewords"],
                percent(stats["translatedsourcewords"], stats["totalsourcewords"]),
                stats["translatedtargetwords"],
            )
            + ConsoleColor.ENDC()
        )
        print(
            ConsoleColor.WARNING()
            + "Fuzzy:        %5d (%3d%%) %10d (%3d%%)             n/a"
            % (
                stats["fuzzy"],
                percent(stats["fuzzy"], stats["total"]),
                stats["fuzzysourcewords"],
                percent(stats["fuzzysourcewords"], stats["totalsourcewords"]),
            )
            + ConsoleColor.ENDC()
        )
        print(
            ConsoleColor.FAIL()
            + "Untranslated: %5d (%3d%%) %10d (%3d%%)             n/a"
            % (
                stats["untranslated"],
                percent(stats["untranslated"], stats["total"]),
                stats["untranslatedsourcewords"],
                percent(stats["untranslatedsourcewords"], stats["totalsourcewords"]),
            )
            + ConsoleColor.ENDC()
        )
        print(
            "Total:        %5d %17d %22d"
            % (
                stats["total"],
                stats["totalsourcewords"],
                stats["translatedtargetwords"],
            )
        )
        if "extended" in stats:
            print("")
            for state, e_stats in stats["extended"].items():
                print(
                    "%-11s   %5d (%3d%%) %10d (%3d%%) %15d"
                    % (
                        state.title() + ":",
                        e_stats["units"],
                        percent(e_stats["units"], stats["total"]),
                        e_stats["sourcewords"],
                        percent(e_stats["sourcewords"], stats["totalsourcewords"]),
                        e_stats["targetwords"],
                    )
                )

        if stats["review"] > 0:
            print(
                "review:          %5d %17d                    n/a"
                % (stats["review"], stats["reviewsourcewords"])
            )
        print()
    return 0


def fuzzymessages(units):
    return [unit for unit in units if unit.isfuzzy() and unit.target]


def translatedmessages(units):
    return [unit for unit in units if unit.istranslated()]


def untranslatedmessages(units):
    return [
        unit
        for unit in units
        if not (unit.istranslated() or unit.isfuzzy()) and unit.source
    ]


class summarizer:
    def __init__(self, filenames, style=default_style, incomplete_only=False):
        self.totals = {}
        self.filecount = 0
        self.longestfilename = 0
        self.style = style
        self.incomplete_only = incomplete_only
        self.complete_count = 0

        if self.style == style_csv:
            print(
                """Filename, Translated Messages, Translated Source Words, \
Translated Target Words, Fuzzy Messages, Fuzzy Source Words, Untranslated Messages, \
Untranslated Source Words, Total Message, Total Source Words, \
Review Messages, Review Source Words"""
            )
        if self.style in (style_short_strings, style_short_words):
            for filename in filenames:  # find longest filename
                if len(filename) > self.longestfilename:
                    self.longestfilename = len(filename)
        for filename in filenames:
            if not os.path.exists(filename):
                logger.error("cannot process %s: does not exist", filename)
                continue
            elif os.path.isdir(filename):
                self.handledir(filename)
            else:
                self.handlefile(filename)
        if self.filecount > 1 and (self.style == style_full):
            if self.incomplete_only:
                summarize("TOTAL (incomplete only):", self.totals, incomplete_only=True)
                print(
                    "File count (incomplete):   %5d"
                    % (self.filecount - self.complete_count)
                )
            else:
                summarize("TOTAL:", self.totals, incomplete_only=False)
            print("File count:   %5d" % (self.filecount))
            print()

    def updatetotals(self, stats):
        """Update self.totals with the statistics in stats."""
        for key in stats.keys():
            if key == "extended":
                # FIXME: calculate extended totals
                continue
            if key not in self.totals:
                self.totals[key] = 0
            self.totals[key] += stats[key]

    def handlefile(self, filename):
        try:
            stats = calcstats(filename)
            self.updatetotals(stats)
            self.complete_count += summarize(
                filename, stats, self.style, self.longestfilename, self.incomplete_only
            )
            self.filecount += 1
        except Exception:  # This happens if we have a broken file.
            logger.error(sys.exc_info()[1])

    def handlefiles(self, dirname, filenames):
        for filename in filenames:
            pathname = os.path.join(dirname, filename)
            if os.path.isdir(pathname):
                self.handledir(pathname)
            else:
                self.handlefile(pathname)

    def handledir(self, dirname):
        path, name = os.path.split(dirname)
        if name in ["CVS", ".svn", "_darcs", ".git", ".hg", ".bzr"]:
            return
        entries = os.listdir(dirname)
        self.handlefiles(dirname, entries)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--incomplete",
        action="store_true",
        default=False,
        dest="incomplete_only",
        help="skip 100%% translated files.",
    )
    output_group = parser.add_argument_group("Output format")
    megroup = output_group.add_mutually_exclusive_group()
    megroup.add_argument(
        "--full",
        action="store_const",
        const=style_full,
        dest="style",
        default=style_full,
        help="(default) statistics in full, verbose format",
    )
    megroup.add_argument(
        "--csv",
        action="store_const",
        const=style_csv,
        dest="style",
        help="statistics in CSV format",
    )
    megroup.add_argument(
        "--short",
        action="store_const",
        const=style_short_strings,
        dest="style",
        help="same as --short-strings",
    )
    megroup.add_argument(
        "--short-strings",
        action="store_const",
        const=style_short_strings,
        dest="style",
        help="statistics of strings in short format - one line per file",
    )
    megroup.add_argument(
        "--short-words",
        action="store_const",
        const=style_short_words,
        dest="style",
        help="statistics of words in short format - one line per file",
    )
    output_group.add_argument(
        "--no-color", action="store_true", help="show output without color"
    )

    parser.add_argument("files", nargs="+")

    args = parser.parse_args()

    logging.basicConfig(format="%(name)s: %(levelname)s: %(message)s")
    ConsoleColor.color_mode = not args.no_color

    summarizer(args.files, args.style, args.incomplete_only)


if __name__ == "__main__":
    main()
