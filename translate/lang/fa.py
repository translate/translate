# -*- coding: utf-8 -*-
#
# Copyright 2007, 2010 Zuza Software Foundation
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

"""This module represents the Persian language.

.. seealso:: http://en.wikipedia.org/wiki/Persian_language
"""

import re

from translate.lang import common


def guillemets(text):

    def convertquotation(match):
        prefix = match.group(1)
        # Let's see that we didn't perhaps match an XML tag property like
        # <a href="something">
        if prefix == u"=":
            return match.group(0)
        return u"%s«%s»" % (prefix, match.group(2))

    # Check that there is an even number of double quotes, otherwise it is
    # probably not safe to convert them.
    if text.count(u'"') % 2 == 0:
        text = re.sub('(.|^)"([^"]+)"', convertquotation, text)
    singlecount = text.count(u"'")
    if singlecount:
        if singlecount == text.count(u'`'):
            text = re.sub("(.|^)`([^']+)'", convertquotation, text)
        elif singlecount % 2 == 0:
            text = re.sub("(.|^)'([^']+)'", convertquotation, text)
    text = re.sub(u'(.|^)“([^”]+)”', convertquotation, text)
    return text


class fa(common.Common):
    """This class represents Persian."""

    listseperator = u"، "

    puncdict = {
        u",": u"،",
        u";": u"؛",
        u"?": u"؟",
        #This causes problems with variables, so commented out for now:
        #u"%": u"٪",
    }

    numbertuple = (
        # It seems that Persian uses both Arabic-Indic and Extended
        # Arabic-Indic digits.

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

        (u"0", u"۰"),  # U+06F0 Extended Arabic-Indic digit zero.
        (u"1", u"۱"),  # U+06F1 Extended Arabic-Indic digit one.
        (u"2", u"۲"),  # U+06F2 Extended Arabic-Indic digit two.
        (u"3", u"۳"),  # U+06F3 Extended Arabic-Indic digit three.
        (u"4", u"۴"),  # U+06F4 Extended Arabic-Indic digit four.
        (u"5", u"۵"),  # U+06F5 Extended Arabic-Indic digit five.
        (u"6", u"۶"),  # U+06F6 Extended Arabic-Indic digit six.
        (u"7", u"۷"),  # U+06F7 Extended Arabic-Indic digit seven.
        (u"8", u"۸"),  # U+06F8 Extended Arabic-Indic digit eight.
        (u"9", u"۹"),  # U+06F9 Extended Arabic-Indic digit nine.
    )

    ignoretests = ["startcaps", "simplecaps"]
    #TODO: check persian numerics
    #TODO: zwj and zwnj?

    @classmethod
    def punctranslate(cls, text):
        """Implement "French" quotation marks."""
        text = super(cls, cls).punctranslate(text)
        return guillemets(text)
