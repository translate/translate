# -*- coding: utf-8 -*-
#
# Copyright 2002-2009,2011 Zuza Software Foundation
#
# This file is part of The Translate Toolkit.
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

"""functions used to manipulate access keys in strings"""

from translate.storage.placeables.general import XMLEntityPlaceable

DEFAULT_ACCESSKEY_MARKER = u"&"


def match_entities(dtd_store, labelsuffixes, accesskeysuffixes):
    """Populates mixedentities from the dtd file."""
    #: Entities which have a .label/.title and .accesskey combined
    mixedentities = {}
    for entity in dtd_store.index.keys():
        for labelsuffix in labelsuffixes:
            if entity.endswith(labelsuffix):
                entitybase = entity[:entity.rfind(labelsuffix)]
                # see if there is a matching accesskey in this line,
                # making this a mixed entity
                for akeytype in accesskeysuffixes:
                    if (entitybase + akeytype) in dtd_store.index:
                        # add both versions to the list of mixed entities
                        mixedentities[entity] = {}
                        mixedentities[entitybase+akeytype] = {}
                # check if this could be a mixed entity (labelsuffix and
                # ".accesskey")
    return mixedentities


def extract(string, accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """Extract the label and accesskey from a label+accesskey string

    The function will also try to ignore &entities; which would obviously not
    contain accesskeys.

    :type string: Unicode
    :param string: A string that might contain a label with accesskey marker
    :type accesskey_marker: Char
    :param accesskey_marker: The character that is used to prefix an access key
    """
    assert isinstance(string, unicode)
    assert isinstance(accesskey_marker, unicode)
    assert len(accesskey_marker) == 1
    if string == u"":
        return u"", u""
    accesskey = u""
    label = string
    marker_pos = 0
    while marker_pos >= 0:
        marker_pos = string.find(accesskey_marker, marker_pos)
        if marker_pos != -1:
            marker_pos += 1
            if marker_pos == len(string):
                break
            if (accesskey_marker == '&' and
                XMLEntityPlaceable.regex.match(string[marker_pos-1:])):
                continue
            label = string[:marker_pos-1] + string[marker_pos:]
            accesskey = string[marker_pos]
            break
    return label, accesskey


def combine(label, accesskey,
            accesskey_marker=DEFAULT_ACCESSKEY_MARKER):
    """Combine a label and and accesskey to form a label+accesskey string

    We place an accesskey marker before the accesskey in the label and this
    creates a string with the two combined e.g. "File" + "F" = "&File"

    :type label: unicode
    :param label: a label
    :type accesskey: unicode char
    :param accesskey: The accesskey
    :rtype: unicode or None
    :return: label+accesskey string or None if uncombineable
    """
    assert isinstance(label, unicode)
    assert isinstance(accesskey, unicode)
    if len(accesskey) == 0:
        return None
    searchpos = 0
    accesskeypos = -1
    in_entity = False
    accesskeyaltcasepos = -1
    while (accesskeypos < 0) and searchpos < len(label):
        searchchar = label[searchpos]
        if searchchar == '&':
            in_entity = True
        elif searchchar == ';':
            in_entity = False
        else:
            if not in_entity:
                if searchchar == accesskey.upper():
                    # always prefer uppercase
                    accesskeypos = searchpos
                if searchchar == accesskey.lower():
                    # take lower case otherwise...
                    if accesskeyaltcasepos == -1:
                        # only want to remember first altcasepos
                        accesskeyaltcasepos = searchpos
                        # note: we keep on looping through in hope
                        # of exact match
        searchpos += 1
    # if we didn't find an exact case match, use an alternate one if available
    if accesskeypos == -1:
        accesskeypos = accesskeyaltcasepos
    # now we want to handle whatever we found...
    if accesskeypos >= 0:
        string = label[:accesskeypos] + accesskey_marker + label[accesskeypos:]
        string = string.encode("UTF-8", "replace")
        return string
    else:
        # can't currently mix accesskey if it's not in label
        return None
