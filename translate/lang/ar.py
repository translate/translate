# -*- coding: utf-8 -*-
#
# Copyright 2007,2009,2011 Zuza Software Foundation
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

"""This module represents the Arabic language.

.. seealso:: http://en.wikipedia.org/wiki/Arabic_language
"""

import re

from translate.lang import common


def reverse_quotes(text):
    def convertquotation(match):
        return u"”%s“" % match.group(1)
    return re.sub(u'“([^”]+)”', convertquotation, text)


class ar(common.Common):
    """This class represents Arabic."""

    listseperator = u"، "

    puncdict = {
        u",": u"،",
        u";": u"؛",
        u"?": u"؟",
        #This causes problems with variables, so commented out for now:
        #u"%": u"٪",
    }

    numbertuple = (
        (u"0", u"٠"),  # U+0660 Arabic-Indic digit zero.
        (u"1", u"١"),  # U+0661 Arabic-Indic digit one.
        (u"2", u"٢"),  # U+0662 Arabic-Indic digit two.
        (u"3", u"٣"),  # U+0663 Arabic-Indic digit three.
        (u"4", u"٤"),  # U+0664 Arabic-Indic digit four.
        (u"5", u"٥"),  # U+0665 Arabic-Indic digit five.
        (u"6", u"٦"),  # U+0666 Arabic-Indic digit six.
        (u"7", u"٧"),  # U+0667 Arabic-Indic digit seven.
        (u"8", u"٨"),  # U+0668 Arabic-Indic digit eight.
        (u"9", u"٩"),  # U+0669 Arabic-Indic digit nine.
    )

    ignoretests = ["startcaps", "simplecaps", "acronyms"]

    @classmethod
    def punctranslate(cls, text):
        text = super(cls, cls).punctranslate(text)
        return reverse_quotes(text)
