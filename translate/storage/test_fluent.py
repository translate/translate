#
# Copyright 2021 Jack Grigg
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

from io import BytesIO

from pytest import raises

from translate.storage import fluent, test_monolingual


class TestFluentUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = fluent.FluentUnit


class TestFluentFile(test_monolingual.TestMonolingualStore):
    StoreClass = fluent.FluentFile

    @staticmethod
    def fluent_parse(fluent_source):
        """Helper that parses Fluent source without requiring files."""
        dummyfile = BytesIO(fluent_source.encode())
        fluent_file = fluent.FluentFile(dummyfile)
        return fluent_file

    def fluent_regen(self, fluent_source):
        """Helper that converts Fluent source to a FluentFile object and back."""
        return bytes(self.fluent_parse(fluent_source)).decode("utf-8")

    def test_simpledefinition(self):
        """Checks that a simple Fluent definition is parsed correctly."""
        fluent_source = "test_me = I can code!"
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getid() == "test_me"
        assert fluent_unit.source == "I can code!"

    def test_simpledefinition_source(self):
        """Checks that a simple Fluent definition can be regenerated as source."""
        fluent_source = "test_me = I can code!"
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source + "\n" == fluent_regen

    def test_term(self):
        """Checks that a Fluent definition with a term is parsed correctly."""
        fluent_source = """-some-term = Fizz Buzz
term-usage = I can code { -some-term }!
"""
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 2

        term_unit = fluent_file.units[0]
        assert term_unit.getid() == "some-term"
        assert term_unit.source == "Fizz Buzz"

        term_unit = fluent_file.units[1]
        assert term_unit.getid() == "term-usage"
        assert term_unit.source == "I can code { -some-term }!"
        assert term_unit.getplaceables() == ["{ -some-term }"]

    def test_term_source(self):
        """Checks that a Fluent definition with a term can be regenerated as source."""
        fluent_source = """-some-term = Fizz Buzz
term-usage = I can code { -some-term }!
"""
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source == fluent_regen

    def test_comments(self):
        """Checks that we handle # comments."""
        fluent_source = """# A comment
key = value
"""
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getnotes() == "A comment"

        fluent_unit.addnote("Another comment", position="replace")
        assert bytes(fluent_file).decode() == fluent_source.replace(
            "A comment", "Another comment"
        )

    def test_multiline_comments(self):
        """Checks that we handle # comments across several lines."""
        fluent_source = """# A comment
# with a second line!
key = value
"""
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getnotes() == "A comment\nwith a second line!"

    # Example from https://projectfluent.org/fluent/guide/comments.html
    COMMENTS_EXAMPLE = """# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


### Localization for Server-side strings of Firefox Screenshots


## Global phrases shared across pages

my-shots = My Shots
home-link = Home
screenshots-description =
    Screenshots made simple. Take, save, and
    share screenshots without leaving Firefox.

## Creating page

# Note: { $title } is a placeholder for the title of the web page
# captured in the screenshot. The default, for pages without titles, is
# creating-page-title-default.
creating-page-title = Creating { $title }
creating-page-title-default = page
creating-page-wait-message = Saving your shot…
"""

    def test_standalone_comments(self):
        """Checks that we handle standalone comments."""
        fluent_source = self.COMMENTS_EXAMPLE
        fluent_file = self.fluent_parse(fluent_source)

        # ((istranslatable, isheader), comment.startswith)
        expected_units = [
            ((False, True), "This Source Code"),
            ((False, True), "Localization for Server-side"),
            ((False, True), "Global phrases shared across pages"),
            ((True, False), ""),
            ((True, False), ""),
            ((True, False), ""),
            ((False, True), "Creating page"),
            ((True, False), "Note: { $title } is a placeholder"),
            ((True, False), ""),
            ((True, False), ""),
        ]
        assert len(fluent_file.units) == len(expected_units)

        for expected, actual in zip(expected_units, fluent_file.units):
            assert (
                actual.istranslatable(),
                actual.isheader(),
            ) == expected[0]
            assert actual.getnotes().startswith(expected[1])

    def test_standalone_comments_source(self):
        """Checks that a Fluent definition with comments can be regenerated as source."""
        fluent_source = self.COMMENTS_EXAMPLE
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source == fluent_regen

    def test_source_with_selectors(self):
        """Checks that we handle selectors."""
        fluent_source = """emails =
    { $unreadEmails ->
        [one] You have one unread email.
       *[other] You have { $unreadEmails } unread emails.
    }
"""
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source == fluent_regen

    def test_errors(self):
        """Checks that errors are extracted."""
        fluent_source = """valid-unit = I'm great!
= I'm not.
"""
        with raises(ValueError):
            self.fluent_parse(fluent_source)

    def test_attributes(self):
        """Checks that we handle attributes."""
        fluent_source = """login-input = Predefined value
    .placeholder = email@example.com
    .aria-label = Login input value
    .title = Type your login email
"""
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getid() == "login-input"
        assert fluent_unit.source == "Predefined value"
        assert fluent_unit.getattributes() == {
            "placeholder": "email@example.com",
            "aria-label": "Login input value",
            "title": "Type your login email",
        }

    def test_attributes_source(self):
        """Checks that attributes can be regenerated as source."""
        fluent_source = """login-input = Predefined value
    .placeholder = email@example.com
    .aria-label = Login input value
    .title = Type your login email
"""
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source == fluent_regen
