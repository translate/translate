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

"""Checks specific to KDE."""

from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.standard import StandardChecker

kdeconfig = CheckerConfig(
    accelmarkers=["&"],
    varmatches=[("%", 1)],
    credit_sources=["Your names", "Your emails", "ROLES_OF_TRANSLATORS"],
)


class KdeChecker(StandardChecker):
    def __init__(self, **kwargs) -> None:
        # TODO allow setup of KDE plural and translator comments so that they do
        # not create false positives
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        checkerconfig.update(kdeconfig)
        super().__init__(**kwargs)
