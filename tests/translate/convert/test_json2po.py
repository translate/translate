#
# Copyright 2023 Stuart Prescott
# Copyright 2023 Michal Čihař <michal@cihar.com>
# Copyright 2024 gemmaro <gemmaro.dev@gmail.com>
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

from io import BytesIO

from translate.convert import json2po
from translate.storage import jsonl10n

from . import test_convert


class TestJson2PO:
    @staticmethod
    def json2po(jsonsource, template=None, filter=None):
        """Helper that converts json source to po source without requiring files."""
        inputfile = BytesIO(jsonsource.encode())
        inputjson = jsonl10n.JsonFile(inputfile, filter=filter)
        convertor = json2po.json2po()
        return convertor.convert_store(inputjson)

    @staticmethod
    def singleelement(storage):
        """Checks that the pofile contains a single non-header element, and returns it."""
        print(bytes(storage))
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simple(self) -> None:
        """Test the most basic json conversion."""
        jsonsource = """{ "text": "A simple string"}"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource)
        assert str(poresult.units[1]) == poexpected

    def test_three_same_keys(self) -> None:
        """Test that we can handle JSON with three (or more) same keys."""
        jsonsource = """{
    "a": {
        "x": "X"
    },
    "b": {
        "x": "X"
    },
    "c": {
        "x": "X"
    }
}
"""
        poresult = self.json2po(jsonsource)
        assert len(poresult.units) == 4
        assert poresult.units[1].msgctxt == ['".a.x"']
        assert poresult.units[2].msgctxt == ['".b.x"']
        assert poresult.units[3].msgctxt == ['".c.x"']

    def test_filter(self) -> None:
        """Test basic json conversion with filter option."""
        jsonsource = """{ "text": "A simple string", "number": 42 }"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource, filter=["text"])
        assert str(poresult.units[1]) == poexpected

    def test_non_string_values(self) -> None:
        """Numbers and booleans are not extracted and do not stop the conversion."""
        jsonsource = """{ "text": "A simple string", "max": 5, "rtl": false }"""
        poresult = self.json2po(jsonsource)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "A simple string"

    def test_non_string_template_value(self) -> None:
        """A number in the template is skipped even if the translation has a string."""
        template = jsonl10n.JsonFile(BytesIO(b'{"a": "A", "count": 5}'))
        translated = jsonl10n.JsonFile(BytesIO(b'{"a": "Ahoj", "count": "5"}'))
        poresult = json2po.json2po().merge_store(template, translated)
        assert len(poresult.units) == 2
        assert poresult.units[1].target == "Ahoj"

    def test_multiple_units(self) -> None:
        """Test that we can handle json with multiple units."""
        jsonsource = """
{
     "name": "John",
     "surname": "Smith",
     "address":
     {
         "streetAddress": "Koeistraat 21",
         "city": "Pretoria",
         "country": "South Africa",
         "postalCode": "10021"
     },
     "phoneNumber":
     [
         {
           "type": "home",
           "number": "012 345-6789"
         },
         {
           "type": "fax",
           "number": "012 345-6788"
         }
     ]
 }
 """

        poresult = self.json2po(jsonsource)
        assert poresult.units[0].isheader()
        print(len(poresult.units))
        assert len(poresult.units) == 11


class TestJson2POCommand(test_convert.TestConvertCommand, TestJson2PO):
    """Tests running actual json2po commands on files."""

    convertmodule = json2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates",
        "-t TEMPLATE, --template=TEMPLATE",
        "--filter",
    ]
