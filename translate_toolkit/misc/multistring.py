#
# Copyright 2006 Zuza Software Foundation
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

"""Supports a hybrid Unicode string that can also have a list of alternate
strings in the strings attribute
"""


class multistring(str):
    def __new__(newtype, string=""):
        if isinstance(string, list):
            if not string:
                raise ValueError("multistring must contain at least one string")
            newstring = str.__new__(newtype, string[0])
            newstring.strings = [newstring] + [
                multistring.__new__(newtype, altstring) for altstring in string[1:]
            ]
        else:
            newstring = str.__new__(newtype, string)
            newstring.strings = [newstring]
        return newstring

    def __init__(self, *args, **kwargs):
        super().__init__()
        if not hasattr(self, "strings"):
            self.strings = []

    def __cmp__(self, otherstring):
        def cmp_compat(s1, s2):
            # Python 3 compatible cmp() equivalent
            return (s1 > s2) - (s1 < s2)

        if isinstance(otherstring, multistring):
            parentcompare = cmp_compat(str(self), otherstring)
            if parentcompare:
                return parentcompare
            else:
                return cmp_compat(self.strings[1:], otherstring.strings[1:])
        elif isinstance(otherstring, str):
            return cmp_compat(str(self), otherstring)
        elif isinstance(otherstring, list) and otherstring:
            return cmp_compat(self, multistring(otherstring))
        else:
            return cmp_compat(str(type(self)), str(type(otherstring)))

    def __hash__(self):
        return hash(str(self))

    def __ne__(self, otherstring):
        return self.__cmp__(otherstring) != 0

    def __eq__(self, otherstring):
        return self.__cmp__(otherstring) == 0

    def __repr__(self):
        return "multistring(%r)" % ([str(item) for item in self.strings])

    def replace(self, old, new, count=None):
        if count is None:
            newstr = multistring(super().replace(old, new))
        else:
            newstr = multistring(super().replace(old, new, count))
        for s in self.strings[1:]:
            if count is None:
                newstr.strings.append(s.replace(old, new))
            else:
                newstr.strings.append(s.replace(old, new, count))
        return newstr
