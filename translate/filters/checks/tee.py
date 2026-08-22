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

"""A checker delegating to several other checkers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from translate.filters.checks.standard import StandardChecker

if TYPE_CHECKING:
    from collections.abc import Sequence

    from translate.filters.checks.checker import (
        CheckerErrorHandler,
        CheckFailureInfo,
        CheckFailures,
        UnitChecker,
    )
    from translate.filters.checks.config import CheckerConfig
    from translate.filters.decorators import CheckFunction
    from translate.storage.base import TranslationStore, TranslationUnit

logger = logging.getLogger(__name__)


class TeeChecker:
    """A Checker that controls multiple checkers."""

    #: Categories where each checking function falls into
    #: Function names are used as keys, categories are the values
    categories: dict[str, int] = {}

    def __init__(
        self,
        checkerconfig: CheckerConfig | None = None,
        excludefilters: dict[str, object] | None = None,
        limitfilters: list[str] | None = None,
        checkerclasses: Sequence[type[UnitChecker]] | None = None,
        errorhandler: CheckerErrorHandler | None = None,
        languagecode: str | None = None,
    ) -> None:
        """Construct a TeeChecker from the given checkers."""
        self.limitfilters = limitfilters

        if checkerclasses is None:
            checkerclasses = [StandardChecker]

        self.checkers = [
            checkerclass(
                checkerconfig=checkerconfig,
                excludefilters=excludefilters,
                limitfilters=limitfilters,
                errorhandler=errorhandler,
            )
            for checkerclass in checkerclasses
        ]

        if languagecode:
            for checker in self.checkers:
                checker.config.updatetargetlanguage(languagecode)

            # Let's hook up the language specific checker
            lang_checker = self.checkers[0].config.lang.checker

            if lang_checker:
                self.checkers.append(lang_checker)

        self.combinedfilters = self.getfilters(excludefilters, limitfilters)
        self.config = checkerconfig or self.checkers[0].config

    def getfilters(
        self,
        excludefilters: dict[str, object] | None = None,
        limitfilters: list[str] | None = None,
    ) -> dict[str, CheckFunction]:
        """
        Returns a dictionary of available filters, including/excluding
        those in the given lists.
        """
        if excludefilters is None:
            excludefilters = {}

        filterslist = [
            checker.getfilters(excludefilters, limitfilters)
            for checker in self.checkers
        ]
        self.combinedfilters = {}

        for filters in filterslist:
            self.combinedfilters.update(filters)

        # TODO: move this somewhere more sensible (a checkfilters method?)
        if limitfilters is not None:
            for filtername in limitfilters:
                if filtername not in self.combinedfilters:
                    logger.warning("could not find filter %s", filtername)

        return self.combinedfilters

    def run_filters(
        self, unit: TranslationUnit, categorised: bool = False
    ) -> CheckFailures:
        """Run all the tests in the checker's suites."""
        failures: dict[str, str | CheckFailureInfo] = {}

        for checker in self.checkers:
            failures.update(checker.run_filters(unit, categorised))

        return failures

    def setsuggestionstore(self, store: TranslationStore[TranslationUnit]) -> None:
        """
        Sets the filename that a checker should use for evaluating
        suggestions.
        """
        for checker in self.checkers:
            checker.setsuggestionstore(store)
