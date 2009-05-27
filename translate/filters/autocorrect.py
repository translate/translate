#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2005, 2006, 2009 Zuza Software Foundation
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

"""A set of autocorrect functions that fix common punctuation and space problems automatically"""

from translate.filters import decoration

def correct(msgid, msgstr):
    """Runs a set of easy and automatic corrections

    Current corrections include:
      - Ellipses - align target to use source form of ellipses (either three dots or the Unicode ellipses characters)
      - Missing whitespace and start or end of the target
      - Missing punction (.:?) at the end of the target
    """
    assert isinstance(msgid, unicode)
    assert isinstance(msgstr, unicode)
    if msgstr == "":
        return msgstr
    if "..." in msgid and u"…" in msgstr:
        return msgstr.replace(u"…", "...")
    if u"…" in msgid and "..." in msgstr:
        return msgstr.replace("...", u"…")
    if decoration.spacestart(msgid) != decoration.spacestart(msgstr) or decoration.spaceend(msgid) != decoration.spaceend(msgstr):
        return decoration.spacestart(msgid) + msgstr.strip() + decoration.spaceend(msgid)
    punctuation = (".", ":", ". ", ": ", "?")
    puncendid = decoration.puncend(msgid, punctuation)
    puncendstr = decoration.puncend(msgstr, punctuation)
    if puncendid != puncendstr:
        if not puncendstr:
            return msgstr + puncendid
    if msgid[:1].isalpha() and msgstr[:1].isalpha():
        if msgid[:1].isupper() and msgstr[:1].islower():
            return msgstr[:1].upper() + msgstr[1:]
        elif msgid[:1].islower() and msgstr[:1].isupper():
            return msgstr[:1].lower() + msgstr[1:]
    return None
