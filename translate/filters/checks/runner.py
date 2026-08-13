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

"""Ad-hoc runner used to try out the checks from the command line."""

from translate.filters.checks.standard import StandardChecker
from translate.lang import data
from translate.storage import base


# TODO: convert these to proper unit tests
def runtests(str1, str2, ignorelist=()):
    """Verifies that the tests pass for a pair of strings."""
    str1 = data.normalize(str1)
    str2 = data.normalize(str2)
    unit = base.TranslationUnit(str1)
    unit.target = str2
    checker = StandardChecker(excludefilters=ignorelist)
    failures = checker.run_filters(unit)

    for test, value in failures.items():
        print(  # ruff:ignore[print]
            f"failure: {test}: {value['message']}\n  {str1!r}\n  {str2!r}"
        )

    return failures


def batchruntests(pairs) -> None:
    """Runs test on a batch of string pairs."""
    passed, numpairs = 0, len(pairs)

    for str1, str2 in pairs:
        if runtests(str1, str2):
            passed += 1

    print(f"\ntotal: {passed}/{numpairs} pairs passed")  # ruff:ignore[print]
