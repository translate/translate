# pyright: strictDictionaryInference=true
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

"""
Count strings and words for supported localization files.

These include: XLIFF, TMX, Gettex PO and MO, Qt .ts and .qm, Wordfast TM, etc

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pocount.html
for examples and usage instructions.
"""

from __future__ import annotations

import csv
import logging
import os
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from operator import itemgetter

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

# kdepluralre = re.compile(r"^_n: ") #Restore this if you really need support for old kdeplurals
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
numberre = re.compile(r"\D\.\D")


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
    """
    Counts the words in the unit's source and target, taking plurals into
    account. The target words are only counted if the unit is translated.
    """
    (sourcewords, targetwords) = (0, 0)
    source = unit.source
    if isinstance(source, multistring):
        sourcestrings = source.strings
    else:
        sourcestrings = [source or ""]

    for s in sourcestrings:
        sourcewords += wordcount(s)
    if not unit.istranslated():
        return sourcewords, targetwords
    target = unit.target
    if isinstance(target, multistring):
        targetstrings = target.strings
    else:
        targetstrings = [target or ""]

    for s in targetstrings:
        targetwords += wordcount(s)

    return sourcewords, targetwords


def calcstats(filename):
    # ignore totally blank or header units
    try:
        store = factory.getobject(filename)
    except ValueError as e:
        logger.warning("Error in %s: %s", filename, e)
        return {}

    # Initialize counters
    stats = {"filename": filename}
    stats["translated"] = 0
    stats["fuzzy"] = 0
    stats["untranslated"] = 0
    stats["review"] = 0
    stats["translatedsourcewords"] = 0
    stats["translatedtargetwords"] = 0
    stats["fuzzysourcewords"] = 0
    stats["untranslatedsourcewords"] = 0
    stats["reviewsourcewords"] = 0

    # Extended state tracking
    extended_stats = {}

    # Single pass through all units
    for unit in store.units:
        if not unit.istranslatable():
            continue

        # Count words once per unit
        sourcewords, targetwords = wordsinunit(unit)

        # Categorize unit and accumulate counts
        # Note: A unit cannot be both translated and fuzzy, as istranslated()
        # returns False when isfuzzy() is True
        is_translated = unit.istranslated()
        is_fuzzy = unit.isfuzzy()

        if is_translated:
            stats["translated"] += 1
            stats["translatedsourcewords"] += sourcewords
            stats["translatedtargetwords"] += targetwords
        elif is_fuzzy and unit.target:
            stats["fuzzy"] += 1
            stats["fuzzysourcewords"] += sourcewords
        elif unit.source:
            # Remaining units with source are untranslated
            stats["untranslated"] += 1
            stats["untranslatedsourcewords"] += sourcewords

        if unit.isreview():
            stats["review"] += 1
            stats["reviewsourcewords"] += sourcewords

        # Handle extended states
        state = unit.get_state_n()
        if state not in extended_state_strings:
            for k in unit.STATE:
                val = unit.STATE[k]
                if val[0] <= int(str(state)) <= val[1]:
                    state = k

        extended_state = extended_state_strings[state]
        if extended_state not in extended_stats:
            extended_stats[extended_state] = defaultdict(int)

        extended_stats[extended_state]["units"] += 1
        extended_stats[extended_state]["sourcewords"] += sourcewords
        extended_stats[extended_state]["targetwords"] += targetwords

    stats["total"] = stats["translated"] + stats["fuzzy"] + stats["untranslated"]
    stats["totalsourcewords"] = (
        stats["translatedsourcewords"]
        + stats["fuzzysourcewords"]
        + stats["untranslatedsourcewords"]
    )
    stats["extended"] = extended_stats

    return stats


@dataclass
class Renderer:
    stats: StatCollector

    def header(self) -> None:
        pass

    def entry(self, title: str, stats: dict) -> None:
        pass

    def footer(self) -> None:
        pass


@dataclass
class CsvRenderer(Renderer):
    def __post_init__(self):
        self._fields = {
            "title": "Filename",
            "translated": "Translated Messages",
            "translatedsourcewords": "Translated Source Words",
            "translatedtargetwords": "Translated Target Words",
            "fuzzy": "Fuzzy Messages",
            "fuzzysourcewords": "Fuzzy Source Words",
            "untranslated": "Untranslated Messages",
            "untranslatedsourcewords": "Untranslated Source Words",
            "total": "Total Message",
            "totalsourcewords": "Total Source Words",
            "review": "Review Messages",
            "reviewsourcewords": "Review Source Words",
        }
        self._writer = csv.DictWriter(
            sys.stdout, self._fields.values(), lineterminator="\n"
        )

    def header(self) -> None:
        self._writer.writeheader()

    def entry(self, title, stats) -> None:
        data = stats.copy()
        data.update(title=title)
        row = {v: data[k] for k, v in self._fields.items()}
        self._writer.writerow(row)


class FullRenderer(Renderer):
    def entry(self, title, stats) -> None:
        print(f"Processing file : {ConsoleColor.HEADER()}{title}{ConsoleColor.ENDC()}")
        print("Type               Strings      Words (source)    Words (translation)")
        print(
            f"{ConsoleColor.OKGREEN()}Translated:   %5d (%3d%%) %10d (%3d%%) %15d"
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
            f"{ConsoleColor.WARNING()}Fuzzy:        %5d (%3d%%) %10d (%3d%%)             n/a"
            % (
                stats["fuzzy"],
                percent(stats["fuzzy"], stats["total"]),
                stats["fuzzysourcewords"],
                percent(stats["fuzzysourcewords"], stats["totalsourcewords"]),
            )
            + ConsoleColor.ENDC()
        )
        print(
            f"{ConsoleColor.FAIL()}Untranslated: %5d (%3d%%) %10d (%3d%%)             n/a"
            % (
                stats["untranslated"],
                percent(stats["untranslated"], stats["total"]),
                stats["untranslatedsourcewords"],
                percent(stats["untranslatedsourcewords"], stats["totalsourcewords"]),
            )
            + ConsoleColor.ENDC()
        )
        print(
            "Total:        {:5d} {:17d} {:22d}".format(
                stats["total"],
                stats["totalsourcewords"],
                stats["translatedtargetwords"],
            )
        )
        if "extended" in stats:
            print()
            for state, e_stats in stats["extended"].items():
                print(
                    "{:<11s}   {:5d} ({:3d}%) {:10d} ({:3d}%) {:15d}".format(
                        f"{state.title()}:",
                        e_stats["units"],
                        percent(e_stats["units"], stats["total"]),
                        e_stats["sourcewords"],
                        percent(e_stats["sourcewords"], stats["totalsourcewords"]),
                        e_stats["targetwords"],
                    )
                )

        if stats["review"] > 0:
            print(
                "review:          {:5d} {:17d}                    n/a".format(
                    stats["review"], stats["reviewsourcewords"]
                )
            )
        print()

    def footer(self) -> None:
        stats = self.stats
        if stats.file_count > 1:
            if stats.incomplete_only:
                self.entry("TOTAL (incomplete only):", stats.totals)
                print(f"File count (incomplete):   {len(stats.results):5d}")
            else:
                self.entry("TOTAL:", stats.totals)
            print(f"File count:   {stats.file_count:5d}")
            print()


@dataclass
class ShortStringsRenderer(Renderer):
    """:param indent: indentation of the 2nd column (length of longest filename)"""

    indent: int = 8

    def entry(self, title, stats) -> None:
        spaces = " " * (self.indent - len(title))
        print(
            "{}{} strings: total: {}\t| {}t\t{}f\t{}u\t| {}t\t{}f\t{}u".format(
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


@dataclass
class ShortWordsRenderer(Renderer):
    """:param indent: indentation of the 2nd column (length of longest filename)"""

    indent: int = 8

    def entry(self, title, stats) -> None:
        spaces = " " * (self.indent - len(title))
        print(
            "{}{} source words: total: {}\t| {}t\t{}f\t{}u\t| {}t\t{}f\t{}u".format(
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


def percent(denominator: int, devisor: int) -> int:
    if devisor == 0:
        return 0
    return denominator * 100 // devisor


class StatCollector:
    def __init__(self, items: list[str], incomplete_only=False) -> None:
        self.incomplete_only = incomplete_only
        self._results: list[dict] = []
        self._handle_items(items)

    def render(self, renderer_class: type[Renderer]) -> None:
        if renderer_class in {ShortWordsRenderer, ShortStringsRenderer}:
            renderer = renderer_class(self, indent=self.longest_filename)  # ty:ignore[unknown-argument]
        else:
            renderer = renderer_class(self)

        renderer.header()
        for entry in self.results:
            renderer.entry(entry["filename"], entry)
        renderer.footer()

    @cached_property
    def results(self):
        if self.incomplete_only:
            return [s for s in self._results if s["total"] != s["translated"]]
        return self._results

    def _handle_items(self, items: list[str]) -> None:
        for item in items:
            if not os.path.exists(item):
                logger.error("cannot process %s: does not exist", item)
                continue
            if os.path.isdir(item):
                self._handle_dir(item)
            else:
                self._handle_single_file(item)

    def _handle_dir(self, dirname) -> None:
        _, name = os.path.split(dirname)
        if name in {"CVS", ".svn", "_darcs", ".git", ".hg", ".bzr"}:
            return
        entries = os.listdir(dirname)
        self._handle_multiple_files(dirname, entries)

    def _handle_multiple_files(self, dirname, filenames) -> None:
        for filename in filenames:
            pathname = os.path.join(dirname, filename)
            if os.path.isdir(pathname):
                self._handle_dir(pathname)
            else:
                self._handle_single_file(pathname)

    def _handle_single_file(self, filename) -> None:
        try:
            stats = calcstats(filename)
            self._results.append(stats)
        except Exception:  # This happens if we have a broken file.
            logger.exception("Broken file")

    @property
    def longest_filename(self):
        filenames = list(map(itemgetter("filename"), self.results)) or [""]
        return max(len(f) for f in filenames)

    @property
    def file_count(self):
        return len(self._results)

    @cached_property
    def totals(self) -> dict:
        """Total stats."""
        totals = defaultdict(int)
        for stats in self._results:
            for key, value in stats.items():
                if key in {"extended", "filename"}:
                    # FIXME: calculate extended totals
                    continue
                totals[key] += value
        return totals


def main(arguments=None) -> None:
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
        const=FullRenderer,
        dest="style",
        default=FullRenderer,
        help="(default) statistics in full, verbose format",
    )
    megroup.add_argument(
        "--csv",
        action="store_const",
        const=CsvRenderer,
        dest="style",
        help="statistics in CSV format",
    )
    megroup.add_argument(
        "--short",
        action="store_const",
        const=ShortStringsRenderer,
        dest="style",
        help="same as --short-strings",
    )
    megroup.add_argument(
        "--short-strings",
        action="store_const",
        const=ShortStringsRenderer,
        dest="style",
        help="statistics of strings in short format - one line per file",
    )
    megroup.add_argument(
        "--short-words",
        action="store_const",
        const=ShortWordsRenderer,
        dest="style",
        help="statistics of words in short format - one line per file",
    )
    output_group.add_argument(
        "--no-color", action="store_true", help="show output without color"
    )

    parser.add_argument("files", nargs="+")

    args = parser.parse_args(arguments)

    logging.basicConfig(format="%(name)s: %(levelname)s: %(message)s")
    ConsoleColor.color_mode = not args.no_color

    StatCollector(args.files, args.incomplete_only).render(args.style)


if __name__ == "__main__":
    main()
