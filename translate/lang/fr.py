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

"""This module represents the French language.

.. seealso:: http://en.wikipedia.org/wiki/French_language
"""


import re

from translate.lang import common


def guillemets(text):
    def convertquotation(match):
        prefix = match.group(1)
        # Let's see that we didn't perhaps match an XML tag property like
        # <a href="something">
        if prefix == "=":
            return match.group(0)
        return "{}«\u00a0{}\u00a0»".format(prefix, match.group(2))  # \u00a0 is NBSP

    # Check that there is an even number of double quotes, otherwise it is
    # probably not safe to convert them.
    if text.count('"') % 2 == 0:
        text = re.sub('(.|^)"([^"]+)"', convertquotation, text)
    singlecount = text.count("'")
    if singlecount:
        if singlecount == text.count("`"):
            text = re.sub("(.|^)`([^']+)'", convertquotation, text)
        elif singlecount % 2 == 0:
            text = re.sub("(.|^)'([^']+)'", convertquotation, text)
    text = re.sub("(.|^)“([^”]+)”", convertquotation, text)
    return text


class fr(common.Common):
    """This class represents French."""

    validaccel = (
        "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "1234567890" "é" "É"
    )

    # According to http://french.about.com/library/writing/bl-punctuation.htm,
    # in French, a space is required both before and after all two- (or more)
    # part punctuation marks and symbols, including : ; « » ! ? % $ # etc.
    puncdict = {}
    for c in ":;!?#":
        puncdict[c] = "\u00a0%s" % c
    # TODO: consider adding % and $, but think about the consequences of how
    # they could be part of variables

    @classmethod
    def punctranslate(cls, text):
        """Implement some extra features for quotation marks.

        Known shortcomings:
            - % and $ are not touched yet for fear of variables
            - Double spaces might be introduced
        """
        text = super().punctranslate(text)
        # We might get problems where we got a space in URIs such as
        # http ://
        text = text.replace("\u00a0://", "://")
        return guillemets(text)
