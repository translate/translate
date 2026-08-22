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

"""Checks that inspect a whole translation unit rather than its strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from translate.filters.checks.checker import UnitChecker
from translate.filters.decorators import critical, extraction

if TYPE_CHECKING:
    from translate.storage.base import TranslationUnit


class StandardUnitChecker(UnitChecker):
    """The standard checks for common checks on translation units."""

    @extraction
    def isfuzzy(self, unit: TranslationUnit) -> bool:
        """
        Check if the unit has been marked fuzzy.

        If a message is marked fuzzy in the PO file then it is extracted.
        Note this is different from ``--fuzzy`` and ``--nofuzzy`` options which
        specify whether tests should be performed against messages marked
        fuzzy.
        """
        return not unit.isfuzzy()

    @extraction
    def isreview(self, unit: TranslationUnit) -> bool:
        """
        Check if the unit has been marked review.

        If you have made use of the 'review' flags in your translations::

          # (review) reason for review
          # (pofilter) testname: explanation for translator

        Then if a message is marked for review in the PO file it will be
        extracted. Note this is different from ``--review`` and ``--noreview``
        options which specify whether tests should be performed against
        messages already marked as under review.
        """
        return not unit.isreview()

    @critical
    def nplurals(self, unit: TranslationUnit) -> bool:
        """
        Checks for the correct number of noun forms for plural translations.

        This uses the plural information in the language module of the
        Translate Toolkit. This is the same as the Gettext nplural value. It
        will check that the number of plurals required is the same as the
        number supplied in your translation.
        """
        if unit.hasplural():
            # if we don't have a valid nplurals value, don't run the test
            nplurals = self.config.lang.nplurals

            if nplurals > 0:
                return len(list(filter(None, unit.target.strings))) == nplurals

        return True

    @extraction
    def hassuggestion(self, unit: TranslationUnit) -> bool:
        """
        Checks if there is at least one suggested translation for this unit.

        If a message has a suggestion (an alternate translation stored in
        alt-trans units in XLIFF and .pending files in PO) then these will be
        extracted. This is used by Pootle and is probably only useful in
        pofilter when using XLIFF files.
        """
        self.suggestion_store = getattr(self, "suggestion_store", None)
        suggestions = []

        if self.suggestion_store:
            suggestions = self.suggestion_store.findunits(unit.source)
        elif getattr(unit, "getalttrans", None):
            # TODO: we probably want to filter them somehow
            suggestions = unit.getalttrans()

        return not bool(suggestions)
