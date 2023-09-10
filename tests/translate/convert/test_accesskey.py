#
# Copyright 2008 Zuza Software Foundation
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

"""
Test the various functions for combining and extracting accesskeys and
labels
"""

from translate.convert import accesskey


def test_get_label_and_accesskey():
    """
    test that we can extract the label and accesskey components from an
    accesskey+label string
    """
    assert accesskey.extract("") == ("", "")
    assert accesskey.extract("File") == ("File", "")
    assert accesskey.extract("&File") == ("File", "F")
    assert accesskey.extract("~File", "~") == ("File", "F")
    assert accesskey.extract("_File", "_") == ("File", "F")


def test_extract_bad_accesskeys():
    """Test what we do in situations that are bad fof accesskeys"""
    # Space is not valid accesskey so we don't extract anything
    assert accesskey.extract("More& Whitespace") == ("More& Whitespace", "")


def test_ignore_entities():
    """
    test that we don't get confused with entities and a & access key
    marker
    """
    assert accesskey.extract("Set &browserName; as &Default") != (
        "Set &browserName; as &Default",
        "b",
    )
    assert accesskey.extract("Set &browserName; as &Default") == (
        "Set &browserName; as Default",
        "D",
    )


def test_alternate_accesskey_marker():
    """check that we can identify the accesskey if the marker is different"""
    assert accesskey.extract("~File", "~") == ("File", "F")
    assert accesskey.extract("&File", "~") == ("&File", "")


def test_unicode():
    """test that we can do the same with unicode strings"""
    assert accesskey.extract("Eḓiṱ") == ("Eḓiṱ", "")
    assert accesskey.extract("E&ḓiṱ") == ("Eḓiṱ", "ḓ")
    assert accesskey.extract("E_ḓiṱ", "_") == ("Eḓiṱ", "ḓ")
    label, akey = accesskey.extract("E&ḓiṱ")
    assert label, akey == ("Eḓiṱ", "ḓ")
    assert isinstance(label, str) and isinstance(akey, str)
    assert accesskey.combine("Eḓiṱ", "ḓ") == ("E&ḓiṱ")


def test_numeric():
    """test combining and extracting numeric markers"""
    assert accesskey.extract("&100%") == ("100%", "1")
    assert accesskey.combine("100%", "1") == "&100%"


def test_empty_string():
    """test that we can handle and empty label+accesskey string"""
    assert accesskey.extract("") == ("", "")
    assert accesskey.extract("", "~") == ("", "")


def test_end_of_string():
    """test that we can handle an accesskey at the end of the string"""
    assert accesskey.extract("Hlola&") == ("Hlola&", "")


def test_combine_label_accesskey():
    """
    test that we can combine accesskey and label to create a label+accesskey
    string
    """
    assert accesskey.combine("File", "F") == "&File"
    assert accesskey.combine("File", "F", "~") == "~File"


def test_combine_label_accesskey_different_capitals():
    """
    test that we can combine accesskey and label to create a label+accesskey
    string when we have more then one case or case is wrong.
    """
    # Prefer the correct case, even when an alternate case occurs first
    assert accesskey.combine("Close Other Tabs", "o") == "Cl&ose Other Tabs"
    assert accesskey.combine("Other Closed Tab", "o") == "Other Cl&osed Tab"
    assert accesskey.combine("Close Other Tabs", "O") == "Close &Other Tabs"
    # Correct case is missing from string, so use alternate case
    assert accesskey.combine("Close Tabs", "O") == "Cl&ose Tabs"
    assert accesskey.combine("Other Tabs", "o") == "&Other Tabs"


def test_uncombinable():
    """test our behaviour when we cannot combine label and accesskey"""
    assert accesskey.combine("File", "D") is None
    assert accesskey.combine("File", "") is None
    assert accesskey.combine("", "") is None


def test_accesskey_already_in_text():
    """test that we can combine if the accesskey is already in the text"""
    assert accesskey.combine("Mail & Newsgroups", "N") == "Mail & &Newsgroups"
    assert accesskey.extract("Mail & &Newsgroups") == ("Mail & Newsgroups", "N")
