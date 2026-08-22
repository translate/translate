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

"""Configuration of the checkers."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from translate.lang import data, factory

if TYPE_CHECKING:
    from translate.filters.checks.tags import TagProperty

_T = TypeVar("_T")

# (tag, attribute, value) specifies a certain attribute which can be changed/
# ignored if it exists inside tag. In the case where there is a third element
# in the tuple, it indicates a property value that can be ignored if present
# (like defaults, for example)
# If a certain item is None, it indicates that it is relevant for all values of
# the property/tag that is specified as None. A non-None value of "value"
# indicates that the value of the attribute must be taken into account.
common_ignoretags: list[TagProperty] = [(None, "xml-lang", None)]
common_canchangetags: list[TagProperty] = [
    ("img", "alt", None),
    (None, "title", None),
    (None, "dir", None),
    (None, "lang", None),
]
# Actually the title tag is allowed on many tags in HTML (but probably not all)


class CheckerConfig:
    """Object representing the configuration of a checker."""

    def __init__(
        self,
        targetlanguage: str | None = None,
        accelmarkers: list[str] | None = None,
        varmatches: list[tuple[str, str | int | None]] | None = None,
        notranslatewords: list[str] | None = None,
        musttranslatewords: list[str] | None = None,
        validchars: str | None = None,
        punctuation: str | None = None,
        endpunctuation: str | None = None,
        ignoretags: list[TagProperty] | None = None,
        canchangetags: list[TagProperty] | None = None,
        criticaltests: list[str] | None = None,
        credit_sources: list[str] | None = None,
    ) -> None:
        # Init lists
        self.accelmarkers = self._init_list(accelmarkers)
        self.varmatches = self._init_list(varmatches)
        self.criticaltests = self._init_list(criticaltests)
        self.credit_sources = self._init_list(credit_sources)

        # Lang data
        self.updatetargetlanguage(targetlanguage)
        self.sourcelang = factory.getlanguage("en")

        # Inits with default values
        self.punctuation = self._init_default(
            data.normalize(punctuation), self.lang.punctuation
        )
        self.endpunctuation = self._init_default(
            data.normalize(endpunctuation), self.lang.sentenceend
        )
        self.ignoretags = self._init_default(ignoretags, common_ignoretags)
        self.canchangetags = self._init_default(canchangetags, common_canchangetags)

        # Other data
        # TODO: allow user configuration of untranslatable words
        self.notranslatewords = dict.fromkeys(
            [data.normalize(key) for key in self._init_list(notranslatewords)]
        )
        self.musttranslatewords = dict.fromkeys(
            [data.normalize(key) for key in self._init_list(musttranslatewords)]
        )
        validchars = data.normalize(validchars)
        self.validcharsmap = {}
        self.updatevalidchars(validchars)

    @staticmethod
    def _init_list(list: list[_T] | None) -> list[_T]:
        """
        Initialise configuration parameters that are lists.

        :param list: None (we'll initialise a blank list) or a list parameter
        """
        if list is None:
            list = []

        return list

    @staticmethod
    def _init_default(param: _T | None, default: _T) -> _T:
        """
        Initialise parameters that can have default options.

        :param param: the user supplied parameter value
        :param default: default values when param is not specified
        :return: the parameter as specified by the user of the default settings
        """
        if param is None:
            return default

        return param

    def update(self, otherconfig: CheckerConfig) -> None:
        """Combines the info in ``otherconfig`` into this config object."""
        self.targetlanguage = otherconfig.targetlanguage or self.targetlanguage
        self.updatetargetlanguage(self.targetlanguage)
        self.accelmarkers.extend(
            [c for c in otherconfig.accelmarkers if c not in self.accelmarkers]
        )
        self.varmatches.extend(otherconfig.varmatches)
        self.notranslatewords.update(otherconfig.notranslatewords)
        self.musttranslatewords.update(otherconfig.musttranslatewords)
        self.validcharsmap.update(otherconfig.validcharsmap)
        self.punctuation += otherconfig.punctuation
        self.endpunctuation += otherconfig.endpunctuation
        # TODO: consider also updating in the following cases:
        self.ignoretags = otherconfig.ignoretags
        self.canchangetags = otherconfig.canchangetags
        self.criticaltests.extend(otherconfig.criticaltests)
        self.credit_sources = otherconfig.credit_sources

    def updatevalidchars(self, validchars: str | None) -> None:
        """Updates the map that eliminates valid characters."""
        if validchars is None:
            return

        validcharsmap = {
            ord(validchar): None for validchar in data.normalize(validchars)
        }
        self.validcharsmap.update(validcharsmap)

    def updatetargetlanguage(self, langcode: str | None) -> None:
        """
        Updates the target language in the config to the given target
        language and sets its script.
        """
        self.targetlanguage = langcode
        self.lang = factory.getlanguage(langcode)
        self.language_script = ""

        for script, langs in data.scripts.items():
            if langcode in langs or data.simplercode(langcode) in langs:
                self.language_script = script
                break
