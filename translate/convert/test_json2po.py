from io import BytesIO

from translate.convert import json2po, test_convert
from translate.storage import jsonl10n


class TestJson2PO:
    @staticmethod
    def json2po(jsonsource, template=None, filter=None):
        """helper that converts json source to po source without requiring files"""
        inputfile = BytesIO(jsonsource.encode())
        inputjson = jsonl10n.JsonFile(inputfile, filter=filter)
        convertor = json2po.json2po()
        outputpo = convertor.convert_store(inputjson)
        return outputpo

    @staticmethod
    def singleelement(storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        print(bytes(storage))
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simple(self):
        """test the most basic json conversion"""
        jsonsource = """{ "text": "A simple string"}"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource)
        assert str(poresult.units[1]) == poexpected

    def test_filter(self):
        """test basic json conversion with filter option"""
        jsonsource = """{ "text": "A simple string", "number": 42 }"""
        poexpected = """#: .text
msgid "A simple string"
msgstr ""
"""
        poresult = self.json2po(jsonsource, filter=["text"])
        assert str(poresult.units[1]) == poexpected

    def test_miltiple_units(self):
        """test that we can handle json with multiple units"""
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
    """Tests running actual json2po commands on files"""

    convertmodule = json2po
    defaultoptions = {"progress": "none"}

    def test_help(self, capsys):
        """tests getting help"""
        options = super().test_help(capsys)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--duplicates")
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--filter", last=True)
