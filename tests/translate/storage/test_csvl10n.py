from io import BytesIO

import pytest

from translate.storage import csvl10n, test_base


class TestCSVUnit(test_base.TestTranslationUnit):
    UnitClass = csvl10n.csvunit


class TestCSV(test_base.TestTranslationStore):
    StoreClass = csvl10n.csvfile

    def parse_store(self, source, **kwargs):
        """Helper that parses source without requiring files."""
        return self.StoreClass(BytesIO(source), **kwargs)

    def test_singlequoting(self):
        """Tests round trip on single quoting at start of string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test 'String'")
        assert unit1.source == "Test 'String'"
        unit2 = store.addsourceunit("'Blessed' String")
        assert unit2.source == "'Blessed' String"
        unit3 = store.addsourceunit("'Quoted String'")
        assert unit3.source == "'Quoted String'"
        newstore = self.reparse(store)
        self.check_equality(store, newstore)
        assert store.units[2] == newstore.units[2]
        assert bytes(store) == bytes(newstore)

    def test_utf_8(self):
        store = self.parse_store("foo.c:1;test;zkouška sirén".encode())
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"

    def test_utf_8_sig(self):
        content = '"location";"source";"target"\r\n"foo.c:1";"test";"zkouška sirén"\r\n'.encode(
            "utf-8-sig"
        )
        store = self.parse_store(content)
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"
        assert bytes(store) == content

    def test_default(self):
        content = b"""ID,English
GENERAL@2|Notes,"cable, motor, switch"
*****END CALL*****|Ask,-"""
        store = self.parse_store(content)
        assert len(store.units) == 3
        assert store.units[0].location == "ID"
        assert store.units[0].source == "English"
        assert store.units[1].location == "GENERAL@2|Notes"
        assert store.units[1].source == "cable, motor, switch"
        assert store.units[2].location == "*****END CALL*****|Ask"
        assert store.units[2].source == "-"

    def test_location_is_parsed(self):
        """Tests that units with location are correctly parsed."""
        source = b'"65066","Ogre","Ogro"\n"65067","Ogra","Ogros"'
        store = self.parse_store(source)
        assert len(store.units) == 2
        unit1 = store.units[0]
        assert unit1.location == "65066"
        assert unit1.source == "Ogre"
        assert unit1.target == "Ogro"
        unit2 = store.units[1]
        assert unit2.location == "65067"
        assert unit2.source == "Ogra"
        assert unit2.target == "Ogros"
        assert unit1.getid() != unit2.getid()

    def test_context_is_parsed(self):
        """Tests that units with the same source are different based on context."""
        source = b'"context","source","target"\n"65066","Ogre","Ogro"\n"65067","Ogre","Ogros"'
        store = self.parse_store(source)
        assert len(store.units) == 2
        unit1 = store.units[0]
        assert unit1.context == "65066"
        assert unit1.source == "Ogre"
        assert unit1.target == "Ogro"
        unit2 = store.units[1]
        assert unit2.context == "65067"
        assert unit2.source == "Ogre"
        assert unit2.target == "Ogros"
        assert unit1.getid() != unit2.getid()

    def test_newline(self):
        content = b'"location";"source";"target"\r\n"foo.c:1";"te\\nst";"ot\\nher"\r\n'
        store = self.parse_store(content)
        assert len(store.units) == 1
        assert store.units[0].source == "te\\nst"
        assert store.units[0].target == "ot\\nher"
        assert bytes(store) == content

    def test_parse_sample(self):
        content = b'"location";"source";"target"\r\n"foo.c:1";"te\\nst";"ot\\nher"\r\n'
        store = self.StoreClass()
        store.parse(content, sample_length=None)
        assert len(store.units) == 1
        assert store.units[0].source == "te\\nst"
        assert store.units[0].target == "ot\\nher"
        assert bytes(store) == content

    def test_utf_8_detection(self):
        content = (
            """"location","source","target","id","fuzzy","context","translator_comments","developer_comments"\r\n"""
            """"","Second","秒","","False","00029.00002","","# Filter Order|IDE_2ND_ORDER_FILTER"\r\n"""
        )
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert store.units[0].source == "Second"
        assert store.units[0].target == "秒"
        assert bytes(store).decode() == content

    def test_encoding(self):
        content = "foo.c:1;test;zkouška sirén"
        store = self.parse_store(content.encode("utf-8"))
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"
        store = self.parse_store(content.encode("utf-8"), encoding="utf-8")
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"
        store = self.parse_store(content.encode("iso-8859-2"), encoding="iso-8859-2")
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"
        with pytest.raises(UnicodeDecodeError):
            store = self.parse_store(content.encode("iso-8859-2"), encoding="utf-8")
