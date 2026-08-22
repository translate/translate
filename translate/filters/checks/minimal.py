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

"""Checkers running only a small selection of the standard checks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.standard import StandardChecker

if TYPE_CHECKING:
    from translate.filters.checks.checker import CheckerKwargs

minimalconfig = CheckerConfig()


class MinimalChecker(StandardChecker):
    def __init__(self, **kwargs: Unpack[CheckerKwargs]) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        limitfilters = kwargs.get("limitfilters")

        if limitfilters is None:
            limitfilters = ["untranslated", "unchanged", "blank"]
            kwargs["limitfilters"] = limitfilters

        checkerconfig.update(minimalconfig)
        super().__init__(**kwargs)


reducedconfig = CheckerConfig()


class ReducedChecker(StandardChecker):
    def __init__(self, **kwargs: Unpack[CheckerKwargs]) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        limitfilters = kwargs.get("limitfilters")

        if limitfilters is None:
            limitfilters = [
                "untranslated",
                "unchanged",
                "blank",
                "doublespacing",
                "doublewords",
                "spellcheck",
            ]
            kwargs["limitfilters"] = limitfilters

        checkerconfig.update(minimalconfig)
        super().__init__(**kwargs)
