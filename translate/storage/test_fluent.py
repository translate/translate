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

from translate.storage import fluent, test_monolingual


class TestFluentUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = fluent.FluentUnit


class TestFluentFile(test_monolingual.TestMonolingualStore):
    StoreClass = fluent.FluentFile

    def fluent_parse(self, fluent_source):
        """Helper that parses Fluent source without requiring files."""
        dummyfile = BytesIO(fluent_source.encode())
        fluent_file = fluent.FluentFile(dummyfile)
        return fluent_file

    def fluent_regen(self, fluent_source):
        """Helper that converts Fluent source to a FluentFile object and back."""
        return bytes(self.fluent_parse(fluent_source)).decode('utf-8')

    def test_simpledefinition(self):
        """Checks that a simple Fluent definition is parsed correctly."""
        fluent_source = 'test_me = I can code!'
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getid() == "test_me"
        assert fluent_unit.source == "I can code!"

    def test_simpledefinition_source(self):
        """Checks that a simple Fluent definition can be regenerated as source."""
        fluent_source = 'test_me = I can code!'
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source + '\n' == fluent_regen

    def test_comments(self):
        """Checks that we handle # comments."""
        fluent_source = '''# A comment
key = value
'''
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getnotes() == 'A comment'

    def test_multiline_comments(self):
        """Checks that we handle # comments across several lines."""
        fluent_source = '''# A comment
# with a second line!
key = value
'''
        fluent_file = self.fluent_parse(fluent_source)
        assert len(fluent_file.units) == 1
        fluent_unit = fluent_file.units[0]
        assert fluent_unit.getnotes() == 'A comment\nwith a second line!'

    def test_source_with_selectors(self):
        """Checks that we handle selectors."""
        fluent_source = '''emails =
    { $unreadEmails ->
        [one] You have one unread email.
       *[other] You have { $unreadEmails } unread emails.
    }
'''
        fluent_regen = self.fluent_regen(fluent_source)
        assert fluent_source == fluent_regen
