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

import pytest

from translate.convert import json2po
from translate.storage import jsonl10n

from . import test_convert


class TestJson2PO:
    @staticmethod
    def json2po(jsonsource, template=None, filter=None, personality="default"):
        """Helper that converts json source to po source without requiring files."""
        inputfile = BytesIO(jsonsource.encode())
        store_class = json2po.JSON_PERSONALITIES[personality]
        inputjson = store_class(inputfile, filter=filter)
        convertor = json2po.json2po()
        if template is not None:
            templatefile = BytesIO(template.encode())
            templatejson = store_class(templatefile)
            return convertor.merge_store(templatejson, inputjson)
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
        jsonsource = (
            """{ "text": "A simple string", "max": 5, "ratio": 1.5, "rtl": false }"""
        )
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

    def test_webextension_comments(self) -> None:
        """WebExtension JSON descriptions are extracted as developer comments."""
        jsonsource = """{
    "greeting": {
        "message": "Hello, world!",
        "description": "Greeting shown on the popup."
    },
    "plain": {
        "message": "Plain text"
    }
}
"""
        poresult = self.json2po(jsonsource, personality="webextension")
        assert len(poresult.units) == 3
        assert poresult.units[1].getlocations() == ["greeting"]
        assert poresult.units[1].source == "Hello, world!"
        assert poresult.units[1].getnotes("developer") == "Greeting shown on the popup."
        assert poresult.units[2].getlocations() == ["plain"]
        assert poresult.units[2].source == "Plain text"
        assert poresult.units[2].getnotes("developer") == ""

    def test_webextension_merge(self) -> None:
        """Merging WebExtension JSON files keeps template developer comments."""
        templatesource = """{
    "greeting": {
        "message": "Hello, $USER$!",
        "description": "Greets the active user.",
        "placeholders": {
            "user": {
                "content": "$1"
            }
        }
    }
}
"""
        translatedsource = """{
    "greeting": {
        "message": "Ahoj, $USER$!"
    }
}
"""
        poresult = self.json2po(
            translatedsource, template=templatesource, personality="webextension"
        )
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "Hello, $USER$!"
        assert poresult.units[1].target == "Ahoj, $USER$!"
        assert poresult.units[1].getnotes("developer") == "Greets the active user."

    def test_convertjson_invalid_personality(self) -> None:
        """Unsupported JSON personality raises a ValueError."""
        with pytest.raises(ValueError, match="Unsupported JSON personality"):
            json2po.convertjson(
                BytesIO(b'{"a": "b"}'), BytesIO(), None, personality="unknown"
            )


class TestJson2POCommand(test_convert.TestConvertCommand, TestJson2PO):
    """Tests running actual json2po commands on files."""

    convertmodule = json2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "--duplicates",
        "-t TEMPLATE, --template=TEMPLATE",
        "--filter",
        "--personality=TYPE",
    ]

    def test_webextension_personality(self) -> None:
        """Test CLI conversion with --personality=webextension."""
        jsonsource = """{
    "title": {
        "message": "Extension title",
        "description": "Comment for translator"
    }
}
"""
        self.create_testfile("messages.json", jsonsource)
        self.run_command(i="messages.json", o="messages.po", personality="webextension")
        output = self.read_testfile("messages.po").decode("utf-8")
        assert "#. Comment for translator" in output
        assert 'msgid "Extension title"' in output

    def test_webextension_template_command(self) -> None:
        """Test CLI merge with --template and --personality=webextension."""
        templatesource = """{
    "title": {
        "message": "Extension title",
        "description": "Comment for translator"
    }
}
"""
        translatedsource = """{
    "title": {
        "message": "Název rozšíření"
    }
}
"""
        self.create_testfile("en.json", templatesource)
        self.create_testfile("cs.json", translatedsource)
        self.run_command(
            i="cs.json", template="en.json", o="cs.po", personality="webextension"
        )
        output = self.read_testfile("cs.po").decode("utf-8")
        assert "#. Comment for translator" in output
        assert 'msgid "Extension title"' in output
        assert 'msgstr "Název rozšíření"' in output
