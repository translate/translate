# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""This module represents the Bengali language.

.. seealso:: http://en.wikipedia.org/wiki/Bengali_language
"""

import re

from translate.lang import common


class bn(common.Common):
    """This class represents Bengali."""

    sentenceend = u"।!?…"

    sentencere = re.compile(r"""(?s)    #make . also match newlines
                            .*?         #anything, but match non-greedy
                            [%s]        #the puntuation for sentence ending
                            \s+         #the spacing after the puntuation
                            (?=[^a-z\d])#lookahead that next part starts with caps
                            """ % sentenceend, re.VERBOSE)

    puncdict = {
        u". ": u"। ",
        u".\n": u"।\n",
    }

    numbertuple = (
        (u"0", u"০"),  # U+09E6 Bengali digit zero.
        (u"1", u"১"),  # U+09E7 Bengali digit one.
        (u"2", u"২"),  # U+09E8 Bengali digit two.
        (u"3", u"৩"),  # U+09E9 Bengali digit three.
        (u"4", u"৪"),  # U+09EA Bengali digit four.
        (u"5", u"৫"),  # U+09EB Bengali digit five.
        (u"6", u"৬"),  # U+09EC Bengali digit six.
        (u"7", u"৭"),  # U+09ED Bengali digit seven.
        (u"8", u"৮"),  # U+09EE Bengali digit eight.
        (u"9", u"৯"),  # U+09EF Bengali digit nine.
    )

    ignoretests = ["startcaps", "simplecaps"]
