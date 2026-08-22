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

"""Checks specific to LibreOffice."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Unpack

from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.exceptions import FilterFailure
from translate.filters.checks.openoffice import openofficeconfig
from translate.filters.checks.standard import StandardChecker
from translate.filters.checks.tags import tagname
from translate.filters.decorators import critical

if TYPE_CHECKING:
    from translate.filters.checks.checker import CheckerKwargs

# XML/HTML tags in LibreOffice help and readme, exclude short tags
lo_tag_re = re.compile(r"""</?(?P<tag>[a-z][a-z_-]+)(?: +[a-z]+="[^"]+")* */?>""")
lo_emptytags = frozenset(["br", "embed", "embedvar", "object", "help-id-missing"])

libreofficeconfig = CheckerConfig(
    accelmarkers=["~"],
    varmatches=[
        ("&", ";"),
        ("%", "%"),
        ("%", None),
        ("%", 0),
        ("$(", ")"),
        ("$", "$"),
        ("${", "}"),
        ("#", "#"),
        ("#", 1),
        ("#", 0),
        ("($", ")"),
        ("$[", "]"),
        ("[", "]"),
        ("@", "@"),
        ("$", None),
    ],
    ignoretags=[
        ("alt", "xml-lang", None),
        ("ahelp", "visibility", "visible"),
        ("img", "width", None),
        ("img", "height", None),
    ],
    canchangetags=[("link", "name", None)],
)


class LibreOfficeChecker(StandardChecker):
    def __init__(self, **kwargs: Unpack[CheckerKwargs]) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        checkerconfig.update(libreofficeconfig)
        checkerconfig.update(openofficeconfig)
        super().__init__(**kwargs)

    @critical
    def validxml(self, str1: str, str2: str) -> bool:
        """
        Check that all XML/HTML open/close tags has close/open pair in the
        translation.
        """
        for location in self.locations:
            if location.endswith((".xrm", ".xhp")):
                opentags = []
                match = re.search(lo_tag_re, str2)
                while match:
                    acttag = match.group(0)
                    if acttag.startswith("</"):
                        if match.group("tag") in lo_emptytags:
                            raise FilterFailure(
                                f"»{acttag}« should be self-closing/empty"
                            )
                        if len(opentags) == 0:
                            raise FilterFailure(f"There is no open tag for »{acttag}«")
                        opentag = opentags.pop()
                        if tagname(acttag) != f"/{tagname(opentag)}":
                            raise FilterFailure(
                                f"Open tag »{opentag}« and close tag »{acttag}« "
                                "don't match"
                            )
                    elif acttag.endswith("/>"):
                        if match.group("tag") not in lo_emptytags:
                            raise FilterFailure(
                                f"»{acttag}« should not be self-closing/empty"
                            )
                    else:
                        opentags.append(acttag)
                    str2 = str2[match.end(0) :]
                    match = re.search(lo_tag_re, str2)
                if len(opentags) != 0:
                    raise FilterFailure(f"There is no close tag for »{opentags.pop()}«")
        return True

    @critical
    def pythonbraceformat(self, str1: str, str2: str) -> bool:
        """Not used in LibreOffice."""
        return True
