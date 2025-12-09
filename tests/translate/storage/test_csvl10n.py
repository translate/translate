from io import BytesIO

import pytest

from translate.storage import csvl10n

from . import test_base


class TestCSVUnit(test_base.TestTranslationUnit):
    UnitClass = csvl10n.csvunit


class TestCSV(test_base.TestTranslationStore):
    StoreClass = csvl10n.csvfile

    def parse_store(self, source, **kwargs):
        """Helper that parses source without requiring files."""
        return self.StoreClass(BytesIO(source), **kwargs)

    def test_singlequoting(self):
        """Tests round trip on single quoting at start of string."""
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

    def test_dialect(self):
        payload = '"location","source","target"\r\n"foo.c:1","test","zkouška sirén"\r\n'.encode()
        store = self.StoreClass()
        store.parse(payload)
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"

        store = self.StoreClass()
        store.parse(payload, dialect="excel")
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"

        store = self.StoreClass()
        store.parse(payload, dialect="unix")
        assert len(store.units) == 1
        assert store.units[0].source == "test"
        assert store.units[0].target == "zkouška sirén"

        store = self.StoreClass()
        store.parse(payload, dialect="default")
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
        content = b'"location";"source";"target"\r\n"foo.c:1";"test\\none";"other\\nanother"\r\n'
        store = self.parse_store(content)
        assert len(store.units) == 1
        assert store.units[0].source == "test\\none"
        assert store.units[0].target == "other\\nanother"
        assert bytes(store) == content

    def test_parse_sample(self):
        content = b'"location";"source";"target"\r\n"foo.c:1";"test\\none";"other\\nanother"\r\n'
        store = self.StoreClass()
        store.parse(content, sample_length=None)
        assert len(store.units) == 1
        assert store.units[0].source == "test\\none"
        assert store.units[0].target == "other\\nanother"
        assert bytes(store) == content

    def test_utf_8_detection(self):
        content = (
            """"location","source","target","id","fuzzy","context","translator_comments","developer_comments"\r\n"""
            """"","Second","秒","","False","00029.00002","","# Filter Order|IDE_ORDER_FILTER"\r\n"""
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
            self.parse_store(content.encode("iso-8859-2"), encoding="utf-8")

    def test_corrupt(self):
        store = self.StoreClass()
        with pytest.raises(ValueError):
            store.parse(b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00b\xee\x9d")

    def test_encoding_save(self):
        content = '"foo.c:1";"test";"zkouška sirén"'
        # Use lines to avoid issues with newlines
        expected = [
            '"location";"source";"target"',
            '"foo.c:1";"test";"伐木"',
        ]
        store = self.parse_store(content.encode("utf-8"))
        assert len(store.units) == 1
        store.units[0].target = "伐木"
        assert bytes(store).decode().splitlines() == expected

        store = self.parse_store(content.encode("iso-8859-2"), encoding="iso-8859-2")
        assert len(store.units) == 1
        store.units[0].target = "伐木"
        with pytest.raises(UnicodeEncodeError):
            bytes(store)

        store = self.parse_store(content.encode("iso-8859-2"))
        assert len(store.units) == 1
        store.units[0].target = "伐木"
        assert bytes(store).decode().splitlines() == expected

    def test_monolingual_id_target(self):
        """Test monolingual CSV with id and target columns."""
        content = b'"id","target"\n"hello","Hola"\n"goodbye","Adios"'
        store = self.parse_store(content)
        assert len(store.units) == 2
        assert store.units[0].id == "hello"
        assert store.units[0].source == ""
        assert store.units[0].target == "Hola"
        assert store.units[1].id == "goodbye"
        assert store.units[1].source == ""
        assert store.units[1].target == "Adios"

    def test_monolingual_context_target(self):
        """Test monolingual CSV with context and target columns."""
        content = b'"context","target"\n"app.hello","Hola"\n"app.goodbye","Adios"'
        store = self.parse_store(content)
        assert len(store.units) == 2
        assert store.units[0].context == "app.hello"
        assert store.units[0].source == ""
        assert store.units[0].target == "Hola"
        assert store.units[1].context == "app.goodbye"
        assert store.units[1].source == ""
        assert store.units[1].target == "Adios"

    def test_monolingual_key_translation(self):
        """Test monolingual CSV with key (mapped to id) and translation (mapped to target)."""
        content = b'"key","translation"\n"hello_message","Hola"\n"bye_message","Adios"'
        store = self.parse_store(content)
        assert len(store.units) == 2
        assert store.units[0].id == "hello_message"
        assert store.units[0].source == ""
        assert store.units[0].target == "Hola"
        assert store.units[1].id == "bye_message"
        assert store.units[1].source == ""
        assert store.units[1].target == "Adios"

    def test_monolingual_roundtrip(self):
        """Test that monolingual CSV can be saved and loaded correctly."""
        content = b'"id","target"\n"hello","Hola"\n"goodbye","Adios"'
        store = self.parse_store(content)
        assert len(store.units) == 2

        # Modify a unit
        store.units[0].target = "Hello Spanish"

        # Roundtrip
        newstore = self.reparse(store)
        assert len(newstore.units) == 2
        assert newstore.units[0].id == "hello"
        assert newstore.units[0].target == "Hello Spanish"
        assert newstore.units[1].id == "goodbye"
        assert newstore.units[1].target == "Adios"

    def test_monolingual_context_roundtrip(self):
        """Test that monolingual CSV with context can be saved and loaded correctly."""
        content = b'"context","target"\n"app.hello","Hola"\n"app.goodbye","Adios"'
        store = self.parse_store(content)
        assert len(store.units) == 2

        # Modify a unit
        store.units[0].target = "Hello Application"

        # Roundtrip
        newstore = self.reparse(store)
        assert len(newstore.units) == 2
        assert newstore.units[0].context == "app.hello"
        assert newstore.units[0].target == "Hello Application"
        assert newstore.units[1].context == "app.goodbye"
        assert newstore.units[1].target == "Adios"

    def test_monolingual_id_context_roundtrip(self):
        """Test that monolingual CSV with both id and context can be saved and loaded correctly."""
        content = (
            b'"id","context","target"\n"msg1","app","Hello"\n"msg2","app","Goodbye"'
        )
        store = self.parse_store(content)
        assert len(store.units) == 2

        # Modify a unit
        store.units[0].target = "Hello World"

        # Roundtrip
        newstore = self.reparse(store)
        assert len(newstore.units) == 2
        assert newstore.units[0].id == "msg1"
        assert newstore.units[0].context == "app"
        assert newstore.units[0].target == "Hello World"
        assert newstore.units[1].id == "msg2"
        assert newstore.units[1].context == "app"
        assert newstore.units[1].target == "Goodbye"

    def test_monolingual_target_only_roundtrip(self):
        """Test that monolingual CSV with only target column can be saved and loaded correctly."""
        content = b'"target"\n"Translation 1"\n"Translation 2"'
        store = self.parse_store(content)
        assert len(store.units) == 2

        # Modify a unit
        store.units[0].target = "Updated Translation 1"

        # Roundtrip
        newstore = self.reparse(store)
        assert len(newstore.units) == 2
        assert newstore.units[0].target == "Updated Translation 1"
        assert newstore.units[1].target == "Translation 2"
