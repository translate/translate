# Copyright 2002, 2003 St James Software
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

"""Implements a case-insensitive (on keys) dictionary and order-sensitive
dictionary
"""


class cidict(dict):
    def __init__(self, fromdict=None):
        """constructs the cidict, optionally using another dict to do so"""
        if fromdict is not None:
            self.update(fromdict)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                "cidict can only have str or unicode as key (got %r)" % type(key)
            )
        for akey in self.keys():
            if akey.lower() == key.lower():
                return super().__getitem__(akey)
        raise IndexError

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(
                "cidict can only have str or unicode as key (got %r)" % type(key)
            )
        for akey in self.keys():
            if akey.lower() == key.lower():
                return super().__setitem__(akey, value)
        return super().__setitem__(key, value)

    def update(self, updatedict):
        """D.update(E) -> None.
        Update D from E: for k in E.keys(): D[k] = E[k]
        """
        for key, value in updatedict.items():
            self[key] = value

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                "cidict can only have str or unicode as key (got %r)" % type(key)
            )
        for akey in self.keys():
            if akey.lower() == key.lower():
                return super().__delitem__(akey)
        raise IndexError

    def __contains__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                "cidict can only have str or unicode as key (got %r)" % type(key)
            )
        for akey in self.keys():
            if akey.lower() == key.lower():
                return 1
        return 0

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default
