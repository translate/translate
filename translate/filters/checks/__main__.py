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

"""Run the standard checks over a few sample string pairs."""

from translate.filters.checks.runner import batchruntests

if __name__ == "__main__":
    testset = [
        (r"simple", r"somple"),
        (r"\this equals \that", r"does \this equal \that?"),
        (r"this \'equals\' that", r"this 'equals' that"),
        (r" start and end! they must match.", r"start and end! they must match."),
        (
            r"check for matching %variables marked like %this",
            r"%this %variable is marked",
        ),
        (
            r"check for mismatching %variables marked like %this",
            r"%that %variable is marked",
        ),
        (r"check for mismatching %variables% too", r"how many %variable% are marked"),
        (r"%% %%", r"%%"),
        (r"Row: %1, Column: %2", r"Mothalo: %1, Kholomo: %2"),
        (r"simple lowercase", r"it is all lowercase"),
        (r"simple lowercase", r"It Is All Lowercase"),
        (r"Simple First Letter Capitals", r"First Letters"),
        (r"SIMPLE CAPITALS", r"First Letters"),
        (r"SIMPLE CAPITALS", r"ALL CAPITALS"),
        (r"forgot to translate", r"  "),
    ]
    batchruntests(testset)
