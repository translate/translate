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

from translate.convert import arb2po
from translate.storage import jsonl10n

from . import test_convert


class TestArb2PO:
    @staticmethod
    def arb2po(arbsource, template=None):
        """Helper that converts ARB source to PO without requiring files."""
        inputfile = BytesIO(arbsource.encode())
        inputarb = jsonl10n.ARBJsonFile(inputfile)
        convertor = arb2po.arb2po()
        if template is not None:
            templatefile = BytesIO(template.encode())
            templatearb = jsonl10n.ARBJsonFile(templatefile)
            return convertor.merge_store(templatearb, inputarb)
        return convertor.convert_store(inputarb)

    def test_simple(self) -> None:
        """Test the most basic ARB conversion."""
        arbsource = '{"helloWorld": "Hello World!"}'
        poresult = self.arb2po(arbsource)
        # header + 1 unit
        assert len(poresult.units) == 2
        unit = poresult.units[1]
        assert unit.source == "Hello World!"
        assert unit.getlocations() == ["helloWorld"]

    def test_multiple_units(self) -> None:
        """Test ARB with multiple translatable strings."""
        arbsource = """{
    "title": "My App",
    "greeting": "Hello",
    "farewell": "Goodbye"
}"""
        poresult = self.arb2po(arbsource)
        # header + 3 units
        assert len(poresult.units) == 4
        assert poresult.units[1].source == "My App"
        assert poresult.units[2].source == "Hello"
        assert poresult.units[3].source == "Goodbye"

    def test_header_filtered(self) -> None:
        """Test that @@locale and other ARB metadata are filtered out."""
        arbsource = """{
    "@@locale": "en",
    "@@last_modified": "2025-01-01",
    "title": "My App"
}"""
        poresult = self.arb2po(arbsource)
        # header + 1 unit (@@locale metadata filtered)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "My App"

    def test_description_as_note(self) -> None:
        """Test that @key.description becomes a developer note."""
        arbsource = """{
    "greeting": "Hello {name}!",
    "@greeting": {
        "description": "Greeting shown on the home page",
        "placeholders": {
            "name": {
                "type": "String",
                "example": "World"
            }
        }
    }
}"""
        poresult = self.arb2po(arbsource)
        assert len(poresult.units) == 2
        unit = poresult.units[1]
        assert unit.source == "Hello {name}!"
        assert "Greeting shown on the home page" in unit.getnotes()

    def test_merge(self) -> None:
        """Test merging template ARB with translated ARB."""
        template = """{
    "@@locale": "en",
    "title": "My App",
    "greeting": "Hello"
}"""
        translation = """{
    "@@locale": "ca",
    "title": "La meva aplicació",
    "greeting": "Hola"
}"""
        poresult = self.arb2po(translation, template=template)
        # header + 2 units
        assert len(poresult.units) == 3
        assert poresult.units[1].source == "My App"
        assert poresult.units[1].target == "La meva aplicació"
        assert poresult.units[2].source == "Hello"
        assert poresult.units[2].target == "Hola"

    def test_merge_missing_translation(self) -> None:
        """Test merge when a key exists in template but not in translation."""
        template = """{
    "title": "My App",
    "greeting": "Hello",
    "farewell": "Goodbye"
}"""
        translation = """{
    "title": "La meva aplicació",
    "greeting": "Hola"
}"""
        poresult = self.arb2po(translation, template=template)
        # header + 3 units
        assert len(poresult.units) == 4
        assert poresult.units[3].source == "Goodbye"
        assert poresult.units[3].target == ""


class TestArb2POCommand(test_convert.TestConvertCommand, TestArb2PO):
    """Tests running actual arb2po commands on files."""

    convertmodule = arb2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates",
        "-t TEMPLATE, --template=TEMPLATE",
    ]
