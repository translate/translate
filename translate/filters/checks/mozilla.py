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

"""Checks specific to Mozilla."""

from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING, Unpack

from translate.filters import decoration
from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.exceptions import FilterFailure
from translate.filters.checks.standard import StandardChecker
from translate.filters.decorators import cosmetic, critical, extraction, functional

if TYPE_CHECKING:
    from translate.filters.checks.checker import CheckerKwargs, CheckFailures
    from translate.storage.base import TranslationUnit

mozillaconfig = CheckerConfig(
    accelmarkers=["&"],
    varmatches=[
        ("&", ";"),
        ("%", "%"),
        ("%", 1),
        ("$", "$"),
        ("$", None),
        ("#", 1),
        ("${", "}"),
        ("$(^", ")"),
        ("{{", "}}"),
    ],
    criticaltests=["accelerators"],
)


class MozillaChecker(StandardChecker):
    accelerators_skipped_scripts = [
        # spellchecker:off
        "Deva",
        "Beng",
        "Tibt",
        "Orya",
        "Gujr",
        "Khmr",
        "Knda",
        "Laoo",
        "Mlym",
        "Mymr",
        "Sind",
        "Taml",
        "assamese",
        "perso-arabic",
        "mon",
        "chinese",
        # spellchecker:on
    ]

    def __init__(self, **kwargs: Unpack[CheckerKwargs]) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        checkerconfig.update(mozillaconfig)
        super().__init__(**kwargs)

    @extraction
    def credits(self, str1: str, str2: str) -> bool:
        """
        Checks for messages containing translation credits instead of
        normal translations.

        Some projects have consistent ways of giving credit to translators by
        having a unit or two where translators can fill in their name and
        possibly their contact details. This test allows you to find these
        units easily to check that they are completed correctly and also
        disables other tests that might incorrectly get triggered for these
        units (such as urls, emails, etc.)
        """
        for location in self.locations:
            if location in {"MOZ_LANGPACK_CONTRIBUTORS", "credit.translation"}:
                raise FilterFailure("Don't translate. Just credit the translators.")

        return True

    mozilla_dialog_re = re.compile(
        r"""(                         # option pair "key: value;"
                                      (?P<key>[-a-z]+)           # key
                                      :\s+                       # separator
                                      (?P<number>\d+(?:[.]\d+)?) # number
                                      (?P<unit>[a-z][a-z]);?     # units
                                      )+                         # multiple pairs
                                   """,
        re.VERBOSE,
    )
    mozilla_dialog_valid_units = ["em", "px", "ch"]

    @critical
    def dialogsizes(self, str1: str, str2: str) -> bool:
        """
        Checks that dialog sizes are not translated.

        This is a Mozilla specific test. Mozilla uses a language called XUL to
        define dialogues and screens. This can make use of CSS to specify
        properties of the dialogue. These properties include things such as the
        width and height of the box. The size might need to be changed if the
        dialogue size changes due to longer translations. Thus translators can
        change these settings. But you are only meant to change the number not
        translate the words 'width' or 'height'. This check capture instances
        where these are translated. It will also catch other types of errors in
        these units.
        """
        # Example: "width: 635px; height: 400px;"
        if "width" in str1 or "height" in str1:
            str1pairs = self.mozilla_dialog_re.findall(str1)

            if str1pairs:
                str2pairs = self.mozilla_dialog_re.findall(str2)

                if len(str1pairs) != len(str2pairs):
                    raise FilterFailure("A dialog pair is missing")

                for i, pair1 in enumerate(str1pairs):
                    pair2 = str2pairs[i]

                    if pair1[0] != pair2[0]:  # Only check pairs that differ
                        if len(pair2) != 4:
                            raise FilterFailure("A part of the dialog pair is missing")

                        if pair1[1] not in pair2:  # key
                            raise FilterFailure(
                                f"Do not translate the key '{pair1[1]}'"
                            )

                        # FIXME we could check more carefully for numbers in pair1[2]
                        if pair2[3] not in self.mozilla_dialog_valid_units:
                            raise FilterFailure(
                                f"Units should be one of '{', '.join(self.mozilla_dialog_valid_units)}'. The source string uses '{pair1[3]}'"
                            )

        return True

    @functional
    def numbers(self, str1: str, str2: str) -> bool:
        """
        Checks that numbers are not translated.

        Special handling for Mozilla to ignore entries that are dialog sizes.
        """
        if self.mozilla_dialog_re.findall(str1):
            return True

        return super().numbers(str1, str2)

    @functional
    def unchanged(self, str1: str, str2: str) -> bool:
        """
        Checks whether a translation is basically identical to the original
        string.

        Special handling for Mozilla to ignore entries that are dialog sizes.
        """
        if (
            self.mozilla_dialog_re.findall(str1)
            or str1.strip().lstrip(string.digits) in self.mozilla_dialog_valid_units
        ):
            return True

        return super().unchanged(str1, str2)

    @cosmetic
    def accelerators(self, str1: str, str2: str) -> bool:
        """
        Checks whether accelerators are consistent between the
        two strings.

        For Mozilla we lower the severity to cosmetic, and for some languages
        it also ensures accelerators are absent in the target string since some
        languages do not use accelerators, for example Indic languages.
        """
        # Mozilla's specific no-accelerators behavior.
        if self.config.language_script in self.accelerators_skipped_scripts:
            str2 = self.filtervariables(str2)
            messages = []

            for accelmarker in self.config.accelmarkers:
                counter2 = decoration.countaccelerators(
                    accelmarker,
                    self.config.lang.validaccel,
                )
                if counter2(str2)[0] > 0:
                    messages.append(
                        f"Accelerator '{accelmarker}' should not appear in translation"
                    )

            if messages:
                raise FilterFailure(messages)

            return True

        # Default accelerators behavior.
        return super().accelerators(str1, str2)


class L20nChecker(MozillaChecker):
    excluded_filters_for_complex_units = [
        "escapes",
        "newlines",
        "tabs",
        "singlequoting",
        "doublequoting",
        "doublespacing",
        "brackets",
        "pythonbraceformat",
        "sentencecount",
        "variables",
    ]
    complex_unit_pattern = "->"

    def __init__(self, **kwargs: Unpack[CheckerKwargs]) -> None:
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        super().__init__(**kwargs)

    def run_filters(
        self, unit: TranslationUnit, categorised: bool = False
    ) -> CheckFailures:
        is_unit_complex = (
            self.complex_unit_pattern in unit.source
            or self.complex_unit_pattern in unit.target
        )

        saved_default_filters = {}
        if is_unit_complex:
            saved_default_filters = self.defaultfilters
            self.defaultfilters = {
                key: value
                for (key, value) in self.defaultfilters.items()
                if key not in self.excluded_filters_for_complex_units
            }

        result = super().run_filters(unit, categorised=categorised)

        if is_unit_complex:
            self.defaultfilters = saved_default_filters

        return result
