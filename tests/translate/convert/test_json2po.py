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

    def test_simple(self):
        """Test the most basic json conversion."""
        jsonsource = """{ "text": "A simple string"}"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource)
        assert str(poresult.units[1]) == poexpected

    def test_filter(self):
        """Test basic json conversion with filter option."""
        jsonsource = """{ "text": "A simple string", "number": 42 }"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource, filter=["text"])
        assert str(poresult.units[1]) == poexpected

    def test_miltiple_units(self):
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
