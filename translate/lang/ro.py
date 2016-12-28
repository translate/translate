# -*- coding: utf-8 -*-
#
# Copyright 2007-2017 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""This module represents the Romanian language.

.. seealso:: http://en.wikipedia.org/wiki/Romanian_language
"""

from __future__ import unicode_literals

from translate.filters.checks import TranslationChecker
from translate.filters.decorators import cosmetic
from translate.lang import common


class RomanianChecker(TranslationChecker):
    """A Checker class for Romanian"""

    def contains_illegal(self, illegal_sequence, target_str):
        """
        Generic method for matching a sequence of strings against a target str.
        :param illegal_sequence: an iterable of illegal substrings
        :param target_str: the string to check against occurences of illegals
        :return: True if target_str doesn't match any of the elements in
                 illegal_sequence
        """
        for s in illegal_sequence:
            if s in target_str:
                return True
        return False

    @cosmetic
    def cedillas(self, str1, str2):
        """
        Checks if the translation strings contains an illegal cedilla character
          illegal_chars = [u'Ţ', u'Ş', u'ţ', u'ş']
        Cedillas are obsoleted diacritics for Romanian and should never be used
          where the target string is Romanian.
        Cedilla-letters are only valid for Turkish (S-cedilla)
          and Gagauz languages (S-cedilla and T-comma)
        Fun fact: Gagauz is the only known language to use T-cedilla
               :param str1: the source string
               :param str2: the target (translated) string
               :return: True if str2 contains a cedilla character
        """
        return self.contains_illegal(['Ţ', 'Ş', 'ţ', 'ş'], str2)

    @cosmetic
    def niciun_nicio(self, str1, str2):
        """
        Checks for sequences containing 'nici un'/'nici o' which are obsolete
        Romanian syntax. Correct is 'niciun'/'nicio'
        """
        return self.contains_illegal(['nici un', 'nici o'], str2)


class ro(common.Common):
    """This class represents Romanian"""

    checker = RomanianChecker
