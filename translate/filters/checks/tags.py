#
# Copyright 2004-2011 Zuza Software Foundation
# 2013, 2016 F Wolff
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""Parsing of the XML/HTML tags found in translation units."""

from __future__ import annotations

import re

# The name of the XML tag
tagname_re = re.compile(r"<[\s]*([\w\/]*).*?(/)?[\s]*>", re.DOTALL)

# We allow escaped quotes, probably for old escaping style of OOo helpcontent
# TODO: remove escaped strings once usage is audited
property_re = re.compile(r""" (\w*)=((\\?".*?\\?")|(\\?'.*?\\?'))""")

# The whole tag
tag_re = re.compile(r"<[^>]+>")

TagProperty = tuple[str | None, str | None, str | None]


def tagname(string: str) -> str:
    """Returns the name of the XML/HTML tag in string."""
    tagname_match = tagname_re.match(string)
    assert tagname_match is not None, f"Expected tag in string: {string}"
    # Extract the tag name (group 1) and optional slash (group 2)
    group1 = tagname_match.group(1) or ""
    group2 = tagname_match.group(2) or ""
    return group1 + group2


def intuplelist(pair: TagProperty, patterns: list[TagProperty]) -> TagProperty:
    """
    Tests to see if pair == (a,b,c) is in list, but handles None entries in
    list as wildcards (only allowed in positions "a" and "c"). We take a
    shortcut by only considering "c" if "b" has already matched.
    """
    a, b, c = pair

    if (b, c) == (None, None):
        # This is a tagname
        return pair

    for pattern in patterns:
        x, y, z = pattern

        if (x, y) in {(a, b), (None, b)} and z in {None, c}:
            return pattern

    return pair


def tagproperties(matches: list[str], ignore: list[TagProperty]) -> list[TagProperty]:
    """
    Returns all the properties in the XML/HTML tag string as (tagname,
    propertyname, propertyvalue), but ignore those combinations specified in
    ignore.
    """
    properties: list[TagProperty] = []

    for match in matches:
        tag = tagname(match)
        properties += [(tag, None, None)]
        # Now we isolate the attribute pairs.
        pairs = property_re.findall(match)

        for property, value, _a, _b in pairs:
            # Strip the quotes:
            value = value[1:-1]

            canignore = False

            if (tag, property, value) in ignore or intuplelist(
                (tag, property, value), ignore
            ) != (tag, property, value):
                canignore = True
                break

            if not canignore:
                properties += [(tag, property, value)]

    return properties
