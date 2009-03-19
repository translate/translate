#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006-2009 Zuza Software Foundation
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

"""A class that does terminology matching"""

import re

# We don't want to miss certain forms of words that only change a little
# at the end. Now we are tying this code to English, but it should serve
# us well. For example "category" should be found in "categories",
# "copy" should be found in "copied"
#
# The tuples define a regular expression to search for, and what with
# what it should be replaced.
ignorepatterns = [
    ("y\s*$", "ie"),          #category/categories, identify/identifies, apply/applied
    ("[\s-]*", ""),           #down time / downtime, pre-order / preorder
    ("-", " "),               #pre-order / pre order
    (" ", "-"),               #pre order / pre-order
]

#TODO: compile regexes

class TerminologyComparer:
    def __init__(self, max_len=500):
        self.match_info = {}
        self.MAX_LEN = max_len

    def similarity(self, text, term, stoppercentage=40):
        """Returns the match quality of C{term} in the C{text}"""
        # We could segment the words, but mostly it will give less ideal
        # results, since we'll miss plurals, etc. Then we also can't search for
        # multiword terms, such as "Free Software". Ideally we should use a
        # stemmer, like the Porter stemmer.

        # So we just see if the word occurs anywhere. This is not perfect since
        # we might get more than we bargained for. The term "form" will be found
        # in the word "format", for example. A word like "at" will trigger too
        # many false positives.

        # First remove a possible disambiguating bracket at the end
        term = re.sub("\s+\(.*\)\s*$", "", term)
        text = text[:self.MAX_LEN]

        if len(term) <= 2:
            return 0

        pos = text.find(term)
        if pos >= 0:
            self.match_info[term] = { 'pos': pos }
            return 100 - pos * 10 / len(text)

        for ignorepattern in ignorepatterns:
            newterm = re.sub(ignorepattern[0], ignorepattern[1], term)
            if newterm in text:
                self.match_info[term] = {
                    'pos': text.find(newterm),
                    'newterm': newterm,
                    'newtermlen': len(newterm),
                }
                return 80
        return 0
