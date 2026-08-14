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

"""Checks specific to GNOME."""

import re

from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.exceptions import FilterFailure
from translate.filters.checks.standard import StandardChecker
from translate.filters.decorators import functional

gconf_attribute_re = re.compile(r'"[a-z_]+?"')

gnomeconfig = CheckerConfig(
    accelmarkers=["_"],
    varmatches=[("%", 1), ("$(", ")")],
    credit_sources=["translator-credits"],
)


class GnomeChecker(StandardChecker):
    def __init__(self, **kwargs) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        checkerconfig.update(gnomeconfig)
        super().__init__(**kwargs)

    @functional
    def gconf(self, str1, str2) -> bool:
        """
        Checks if we have any gconf config settings translated.

        Gconf settings should not be translated so this check checks that gconf
        settings such as "name" or "modification_date" are not translated in
        the translation. It allows you to change the surrounding quotes but
        will ensure that the setting values remain untranslated.
        """
        for location in self.locations:
            if (
                location.find("schemas.in") != -1
                or location.find("gschema.xml.in") != -1
            ):
                gconf_attributes = gconf_attribute_re.findall(str1)
                # stopwords = [word for word in words1 if word in self.config.notranslatewords and word not in words2]
                stopwords = [
                    word for word in gconf_attributes if word[1:-1] not in str2
                ]

                if stopwords:
                    raise FilterFailure(
                        f"Do not translate GConf attributes: {', '.join(stopwords)}"
                    )

                return True

        return True
