#
# Copyright 2004-2011 Zuza Software Foundation
# 2013, 2016 F Wolff
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

"""Base classes that all the checkers are built on."""

from __future__ import annotations

from translate.filters import helpers, prefilters
from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.exceptions import FilterFailure
from translate.filters.checks.tags import tag_re
from translate.lang import data


def cache_results(f):
    def cached_f(self, param1):
        key = (f.__name__, param1)
        res_cache = self.results_cache

        if key in res_cache:
            return res_cache[key]
        value = f(self, param1)
        res_cache[key] = value
        return value

    return cached_f


class UnitChecker:
    """
    Parent Checker class which does the checking based on functions
    available in derived classes.
    """

    preconditions = {}

    def __init__(
        self,
        checkerconfig=None,
        excludefilters=None,
        limitfilters=None,
        errorhandler=None,
    ) -> None:
        self.errorhandler = errorhandler

        #: Categories where each checking function falls into
        #: Function names are used as keys, categories are the values
        self.categories = {}

        if checkerconfig is None:
            self.setconfig(CheckerConfig())
        else:
            self.setconfig(checkerconfig)

        # Exclude functions defined in UnitChecker from being treated as tests.
        self.helperfunctions = {}

        for functionname in dir(UnitChecker):
            function = getattr(self, functionname)

            if callable(function):
                self.helperfunctions[functionname] = function

        self.defaultfilters = self.getfilters(excludefilters, limitfilters)
        self.results_cache = {}

    def getfilters(self, excludefilters=None, limitfilters=None):
        """
        Returns dictionary of available filters, including/excluding those
        in the given lists.
        """
        filters = {}

        if limitfilters is None:
            # use everything available unless instructed
            limitfilters = dir(self)

        if excludefilters is None:
            excludefilters = {}

        for functionname in limitfilters:
            if functionname in excludefilters:
                continue

            if functionname in self.helperfunctions:
                continue

            if functionname == "errorhandler":
                continue

            filterfunction = getattr(self, functionname, None)
            if not callable(filterfunction):
                continue

            filters[functionname] = filterfunction

        return filters

    def setconfig(self, config) -> None:
        """Sets the accelerator list."""
        self.config = config
        self.accfilters = [
            prefilters.filteraccelerators(accelmarker)
            for accelmarker in self.config.accelmarkers
        ]
        self.varfilters = [
            prefilters.filtervariables(startmatch, endmatch, prefilters.varname)
            for startmatch, endmatch in self.config.varmatches
        ]
        self.removevarfilter = [
            prefilters.filtervariables(startmatch, endmatch, prefilters.varnone)
            for startmatch, endmatch in self.config.varmatches
        ]

    def setsuggestionstore(self, store) -> None:
        """
        Sets the filename that a checker should use for evaluating
        suggestions.
        """
        self.suggestion_store = store

        if self.suggestion_store:
            self.suggestion_store.require_index()

    @cache_results
    def filtervariables(self, str1):
        """Filter out variables from ``str1``."""
        return helpers.multifilter(str1, self.varfilters)

    @cache_results
    def removevariables(self, str1):
        """Remove variables from ``str1``."""
        return helpers.multifilter(str1, self.removevarfilter)

    @cache_results
    def filteraccelerators(self, str1):
        """Filter out accelerators from ``str1``."""
        return helpers.multifilter(str1, self.accfilters, None)

    def filteraccelerators_by_list(self, str1, acceptlist=None):
        """Filter out accelerators from ``str1``."""
        return helpers.multifilter(str1, self.accfilters, acceptlist)

    @cache_results
    def filterwordswithpunctuation(self, str1):
        """
        Replaces words with punctuation with their unpunctuated
        equivalents.
        """
        return prefilters.filterwordswithpunctuation(str1)

    @cache_results
    def filterxml(self, str1):
        """Filter out XML from the string so only text remains."""
        return tag_re.sub("", str1)

    @staticmethod
    def run_test(test, unit):
        """
        Runs the given test on the given unit.

        Note that this can raise a :exc:`FilterFailure` as part of normal operation.
        """
        return test(unit)

    @property
    def checker_name(self):
        """Extract checker name, for example 'mozilla' from MozillaChecker."""
        return str(self.__class__.__name__).lower()[: -len("checker")]

    def get_ignored_filters(self):
        """Return checker's additional filters for current language."""
        return list(
            set(
                self.config.lang.ignoretests.get(self.checker_name, [])
                + self.config.lang.ignoretests.get("all", [])
            )
        )

    def run_filters(self, unit, categorised: bool = False) -> dict[str, dict]:
        """
        Run all the tests in this suite.

        :return: Content of the dictionary is as follows::

           {'testname': { 'message': message_or_exception, 'category': failure_category } }
        """
        self.results_cache = {}
        failures = {}
        ignores = self.get_ignored_filters()
        functionnames = self.defaultfilters.keys()
        priorityfunctionnames = self.preconditions.keys()
        otherfunctionnames = filter(
            lambda functionname: functionname not in self.preconditions, functionnames
        )

        for functionname in list(priorityfunctionnames) + list(otherfunctionnames):
            if functionname in ignores:
                continue

            filterfunction = getattr(self, functionname, None)

            # This filterfunction may only be defined on another checker if
            # using TeeChecker
            if filterfunction is None:
                continue

            filtermessage = ""

            try:
                filterresult = self.run_test(filterfunction, unit)
            except FilterFailure as e:
                filterresult = False
                filtermessage = str(e)
            except Exception as e:
                if self.errorhandler is None:
                    raise ValueError(
                        f"error in filter {functionname}: {unit.source!r}, {unit.target!r}, {e}"
                    ) from e
                filterresult = self.errorhandler(
                    functionname, unit.source, unit.target, e
                )
            if not filterresult:
                if not filtermessage:
                    # Should be quite rare
                    # pylint: disable-next=import-outside-toplevel
                    import pydoc  # ruff:ignore[import-outside-top-level]

                    # Strip out unnecessary whitespace from docstring
                    filtermessage = pydoc.getdoc(filterfunction)
                # We test some preconditions that aren't actually a cause for
                # failure
                if functionname in self.defaultfilters:
                    failures[functionname] = {
                        "message": filtermessage,
                        "category": self.categories[functionname],
                    }

                if functionname in self.preconditions:
                    for ignoredfunctionname in self.preconditions[functionname]:
                        ignores.append(ignoredfunctionname)

        self.results_cache = {}

        if not categorised:
            for name, info in failures.items():
                failures[name] = info["message"]
        return failures


class TranslationChecker(UnitChecker):
    """
    A checker that passes source and target strings to the checks, not the
    whole unit.

    This provides some speedup and simplifies testing.
    """

    def __init__(
        self,
        checkerconfig=None,
        excludefilters=None,
        limitfilters=None,
        errorhandler=None,
    ) -> None:
        super().__init__(checkerconfig, excludefilters, limitfilters, errorhandler)

        self.locations = []

    def run_test(self, test, unit):
        """
        Runs the given test on the given unit.

        Note that this can raise a :exc:`FilterFailure` as part of normal
        operation.
        """
        if self.hasplural:
            filtermessages = []
            filterresult = True

            for pluralform in unit.target.strings:
                try:
                    if not test(self.str1, str(pluralform)):
                        filterresult = False
                except FilterFailure as e:
                    filterresult = False
                    filtermessages.extend(e.messages)

            if not filterresult and filtermessages:
                raise FilterFailure(filtermessages)
            return filterresult
        return test(self.str1, self.str2)

    def run_filters(self, unit, categorised=False):
        """
        Do some optimisation by caching some data of the unit for the
        benefit of :meth:`~TranslationChecker.run_test`.
        """
        self.str1 = data.normalize(unit.source) or ""
        self.str2 = data.normalize(unit.target) or ""
        self.hasplural = unit.hasplural()
        self.locations = unit.getlocations()

        return super().run_filters(unit, categorised)
