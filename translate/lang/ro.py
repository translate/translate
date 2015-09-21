# -*- coding: utf-8 -*-
#
# Copyright 2007-2009 Zuza Software Foundation
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

.. seealso:: https://en.wikipedia.org/wiki/Romanian_language
"""

import re

from translate.lang import common


def ghilimele(text):

    def convertquotation(match):
        prefix = match.group(1)
        # Let's see that we didn't perhaps match an XML tag property like
        # <a href="something">
        if prefix == u"=":
            return match.group(0)
        return u"%s„%s”" % (prefix, match.group(2))

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


class RoChecker(TranslationChecker):

    @critical
    def scedilla(self, str1, str2):
        """Checks whether target text contains a ş or Ş (s-cedilla).

           glyphs incorrectly used instead of the Romanian Șș (s-comma)
           they are not valid characters for Romanian (only Turkish) 
           ignore this test if there is a Turkish name or placename
        """
        if ("ş" in str2) or ("Ş" in str2):
            raise SeriousFilterFailure(u"S-cedilla detected: ş or Ş, please"
                                       "use T-comma instead: ș or Ș")
        else:
            return True


    @critical
    def tcedilla(self, str1, str2):
        """Checks whether target text contains a ţ or Ţ (t-cedilla).

           glyphs incorrectly used instead of the Romanian Țț (t-comma)
           they don't exist in any other language (not even Turkish)
        """
        if ("ţ" in str2) or ("Ţ" in str2):
            raise SeriousFilterFailure(u"T-cedilla detected: ţ or Ţ, please"
                                       "use T-comma instead: ț or Ț")
        else:
            return True


class ro(common.Common):
    """This class represents Romanian."""

    validaccel = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
                 u"1234567890"
    specialchars = u"ȘșȚțĂăÂâÎî«»„”"
    checker = RoChecker

    @classmethod
    def characters(cls, text):
        """Returns a list of characters in text."""
        return [c for c in cls.character_iter(text)]

    @classmethod
    def punctranslate(cls, text):
        """Implement some extra features for quotation marks.

        Known shortcomings:
            - % and $ are not touched yet for fear of variables
            - Double spaces might be introduced
        """
        text = super(cls, cls).punctranslate(text)
        # We might get problems where we got a space in URIs such as
        # http ://
        text = text.replace(u"\u00a0://", "://")
        return ghilimele(text)
