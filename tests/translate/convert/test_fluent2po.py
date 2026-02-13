#
# Copyright 2026 Pere Orga <pere@orga.cat>
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

from io import BytesIO

from translate.convert import fluent2po
from translate.storage import fluent

from . import test_convert


class TestFluent2PO:
    @staticmethod
    def fluent2po(fluentsource, template=None):
        """Helper that converts Fluent source to PO without requiring files."""
        inputfile = BytesIO(fluentsource.encode())
        inputfluent = fluent.FluentFile(inputfile)
        convertor = fluent2po.fluent2po()
        if template is not None:
            templatefile = BytesIO(template.encode())
            templatefluent = fluent.FluentFile(templatefile)
            return convertor.merge_store(templatefluent, inputfluent)
        return convertor.convert_store(inputfluent)

    def test_simple(self) -> None:
        """Test the most basic Fluent conversion."""
        fluentsource = "hello = Hello World!\n"
        poresult = self.fluent2po(fluentsource)
        # header + 1 unit
        assert len(poresult.units) == 2
        unit = poresult.units[1]
        assert unit.source == "Hello World!"
        assert unit.getlocations() == ["hello"]

    def test_multiple_messages(self) -> None:
        """Test Fluent file with multiple messages."""
        fluentsource = """\
title = My App
greeting = Hello
farewell = Goodbye
"""
        poresult = self.fluent2po(fluentsource)
        # header + 3 units
        assert len(poresult.units) == 4
        assert poresult.units[1].source == "My App"
        assert poresult.units[2].source == "Hello"
        assert poresult.units[3].source == "Goodbye"

    def test_comments_skipped(self) -> None:
        """Test that resource comments and group comments are skipped."""
        fluentsource = """\
### Resource comment

## Group comment

hello = Hello

# Standalone comment
"""
        poresult = self.fluent2po(fluentsource)
        # header + 1 translatable unit (comments are skipped)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "Hello"

    def test_message_with_comment(self) -> None:
        """Test that message-attached comments become notes."""
        fluentsource = """\
# This is shown on the home page
hello = Hello World!
"""
        poresult = self.fluent2po(fluentsource)
        assert len(poresult.units) == 2
        unit = poresult.units[1]
        assert unit.source == "Hello World!"
        assert "This is shown on the home page" in unit.getnotes()

    def test_placeholders(self) -> None:
        """Test Fluent message with placeholders."""
        fluentsource = "greeting = Hello { $name }!\n"
        poresult = self.fluent2po(fluentsource)
        assert len(poresult.units) == 2
        unit = poresult.units[1]
        assert "{ $name }" in unit.source

    def test_merge(self) -> None:
        """Test merging template Fluent with translated Fluent."""
        template = """\
title = My App
greeting = Hello
"""
        translation = """\
title = La meva aplicació
greeting = Hola
"""
        poresult = self.fluent2po(translation, template=template)
        # header + 2 units
        assert len(poresult.units) == 3
        assert poresult.units[1].source == "My App"
        assert poresult.units[1].target == "La meva aplicació"
        assert poresult.units[2].source == "Hello"
        assert poresult.units[2].target == "Hola"

    def test_merge_missing_translation(self) -> None:
        """Test merge when a key exists in template but not in translation."""
        template = """\
title = My App
greeting = Hello
farewell = Goodbye
"""
        translation = """\
title = La meva aplicació
greeting = Hola
"""
        poresult = self.fluent2po(translation, template=template)
        # header + 3 units
        assert len(poresult.units) == 4
        assert poresult.units[3].source == "Goodbye"
        assert poresult.units[3].target == ""

    def test_merge_with_comments(self) -> None:
        """Test that comments in template are skipped during merge."""
        template = """\
### Resource comment

# Shown on home page
hello = Hello
"""
        translation = """\
hello = Hola
"""
        poresult = self.fluent2po(translation, template=template)
        # header + 1 unit (comment skipped)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "Hello"
        assert poresult.units[1].target == "Hola"


class TestFluent2POCommand(test_convert.TestConvertCommand, TestFluent2PO):
    """Tests running actual fluent2po commands on files."""

    convertmodule = fluent2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates",
        "-t TEMPLATE, --template=TEMPLATE",
    ]
