import json
from io import BytesIO

from pytest import mark, raises

from translate.misc.multistring import multistring
from translate.storage import base, jsonl10n

from . import test_monolingual

JSON_I18NEXT = """{
    "key": "value",
    "keyDeep": {
        "inner": "value"
    },
    "keyPluralSimple": "the singular",
    "keyPluralSimple_plural": "the plural",
    "keyPluralMultipleEgArabic_0": "the plural form 0",
    "keyPluralMultipleEgArabic_1": "the plural form 1",
    "keyPluralMultipleEgArabic_2": "the plural form 2",
    "keyPluralMultipleEgArabic_3": "the plural form 3",
    "keyPluralMultipleEgArabic_4": "the plural form 4",
    "keyPluralMultipleEgArabic_5": "the plural form 5"
}
"""

JSON_I18NEXT_V4 = """{
    "key": "value",
    "keyDeep": {
        "inner": "value"
    },
    "keyPluralSimple_one": "the singular",
    "keyPluralSimple_other": "the plural",
    "keyPluralMultipleEgArabic_zero": "the plural form 0",
    "keyPluralMultipleEgArabic_one": "the plural form 1",
    "keyPluralMultipleEgArabic_two": "the plural form 2",
    "keyPluralMultipleEgArabic_few": "the plural form 3",
    "keyPluralMultipleEgArabic_many": "the plural form 4",
    "keyPluralMultipleEgArabic_other": "the plural form 5"
}
"""

JSON_I18NEXT_V4_FIXED = """{
    "key": "value",
    "keyDeep": {
        "inner": "value"
    },
    "keyPluralSimple_zero": "",
    "keyPluralSimple_one": "the singular",
    "keyPluralSimple_two": "",
    "keyPluralSimple_few": "",
    "keyPluralSimple_many": "",
    "keyPluralSimple_other": "the plural",
    "keyPluralMultipleEgArabic_zero": "the plural form 0",
    "keyPluralMultipleEgArabic_one": "the plural form 1",
    "keyPluralMultipleEgArabic_two": "the plural form 2",
    "keyPluralMultipleEgArabic_few": "the plural form 3",
    "keyPluralMultipleEgArabic_many": "the plural form 4",
    "keyPluralMultipleEgArabic_other": "the plural form 5"
}
"""

JSON_FLAT_I18NEXT_V4 = """{
    "key": "value",
    "keyDeep.inner": "value",
    "keyPluralSimple_one": "the singular",
    "keyPluralSimple_other": "the plural",
    "keyPluralMultipleEgArabic_zero": "the plural form 0",
    "keyPluralMultipleEgArabic_one": "the plural form 1",
    "keyPluralMultipleEgArabic_two": "the plural form 2",
    "keyPluralMultipleEgArabic_few": "the plural form 3",
    "keyPluralMultipleEgArabic_many": "the plural form 4",
    "keyPluralMultipleEgArabic_other": "the plural form 5"
}
"""

JSON_FLAT_I18NEXT_V4_FIXED = """{
    "key": "value",
    "keyDeep.inner": "value",
    "keyPluralSimple_zero": "",
    "keyPluralSimple_one": "the singular",
    "keyPluralSimple_two": "",
    "keyPluralSimple_few": "",
    "keyPluralSimple_many": "",
    "keyPluralSimple_other": "the plural",
    "keyPluralMultipleEgArabic_zero": "the plural form 0",
    "keyPluralMultipleEgArabic_one": "the plural form 1",
    "keyPluralMultipleEgArabic_two": "the plural form 2",
    "keyPluralMultipleEgArabic_few": "the plural form 3",
    "keyPluralMultipleEgArabic_many": "the plural form 4",
    "keyPluralMultipleEgArabic_other": "the plural form 5"
}
"""

JSON_FLAT_I18NEXT_V4_PLURAL = b"""{
    "key": "value",
    "keyDeep.inner": "value",
    "keyPluralSimple": "Ahoj",
    "keyPluralMultipleEgArabic": "Nazdar"
}
"""

JSON_I18NEXT_PLURAL = b"""{
    "key": "value",
    "keyDeep": {
        "inner": "value"
    },
    "keyPluralSimple": "Ahoj",
    "keyPluralMultipleEgArabic": "Nazdar"
}
"""

JSON_I18NEXT_NESTED_ARRAY_BEFORE = """{
    "apps": {
        "legacy": "app1"
    }
}
"""
JSON_I18NEXT_NESTED_ARRAY = """{
    "apps": [
        {
            "title": "app1",
            "description": "test description"
        },
        {
            "title": "app2",
            "description": "test description 2"
        }
    ]
}
"""
JSON_ARRAY = b"""{
    "key": [
        "One",
        "Two",
        "Three"
    ]
}
"""
JSON_COMPLEX = b"""{
    "key": "value",
    "key.key": "value",
    "key[0]": "value2",
    "key3": [
        "one",
        "two"
    ],
    "key4": [
        {
            "nested": "one"
        },
        [
            "one",
            "two"
        ]
    ]
}
"""
# spellchecker:off
JSON_COMPLEX_ARRAY = r"""[
    {
        "url": "massivholztische",
        "heading": "Welche Tischgröße ist für mich die richtige?",
        "content": "Überlege zunächst wie viele Personen regelmäßig\r\n"
    },
    {
        "url": "massivholztische",
        "heading": "Bietet Öl genügend Schutz für meinen Massivholztisch?",
        "content": "<p>Holzöl bietet bei normaler Nutzung"
    }
]
""".encode()
# spellchecker:on
JSON_GOTEXT = b"""{
    "language": "en-US",
    "messages": [
        {
            "id": "tag",
            "message": "{N} tags",
            "translatorComment": "a piece or strip of strong paper, plastic, metal, leather, etc., for attaching by one end to something as a mark or label",
            "translation": {
                "select": {
                    "feature": "plural",
                    "arg": "N",
                    "cases": {
                        "one": {
                            "msg": "{N} tag"
                        },
                        "other": {
                            "msg": "{N} tags"
                        }
                    }
                }
            },
            "placeholders": [
                {
                    "id": "N",
                    "string": "%[1]d",
                    "type": "int",
                    "underlyingType": "int",
                    "argNum": 1,
                    "expr": "n"
                }
            ]
        },
        {
            "id": "table",
            "message": "Table",
            "translatorComment": "an article of furniture consisting of a flat, slablike top supported on one or more legs or other supports",
            "translation": "Table"
        }
    ]
}
"""
JSON_GOI18N = b"""[
    {
        "id": "tag",
        "description": "a piece or strip of strong paper, plastic, metal, leather, etc., for attaching by one end to something as a mark or label",
        "translation": {
            "one": "{{.count}} tag",
            "other": "{{.count}} tags"
        }
    },
    {
        "id": "table",
        "description": "an article of furniture consisting of a flat, slablike top supported on one or more legs or other supports",
        "translation": "Table"
    }
]
"""

JSON_GOI18N_V2 = """{
    "simple": "value",
    "plural": {
        "zero": "the plural form 0",
        "one": "the plural form 1",
        "two": "the plural form 2",
        "few": "the plural form 3",
        "many": "the plural form 4",
        "other": "the plural form 5"
    }
}
"""

JSON_GOI18N_V2_PLURAL = """{
    "simple": "value",
    "plural": "plural"
}
"""


JSON_GOI18N_V2_SIMPLE = """{
    "key": "value",
    "table": {
        "description": "an article of furniture consisting of a flat, slablike top supported on one or more legs or other supports",
        "other": "Table"
    },
    "tag": {
        "description": "a piece or strip of strong paper, plastic, metal, leather, etc., for attaching by one end to something as a mark or label",
        "one": "{{.count}} tag",
        "other": "{{.count}} tags"
    },
    "nested.key.hello": "world",
    "nested.key.world": "hello",
    ".world": "hello"
}
"""

JSON_GOI18N_V2_COMPLEX = """{
    "key": {
        "other": "value"
    },
    "table": {
        "description": "an article of furniture consisting of a flat, slablike top supported on one or more legs or other supports",
        "other": "Table"
    },
    "tag": {
        "description": "a piece or strip of strong paper, plastic, metal, leather, etc., for attaching by one end to something as a mark or label",
        "one": "{{.count}} tag",
        "other": "{{.count}} tags"
    },
    "nested.key.hello": {
        "other": "world"
    },
    "nested.key.world": {
        "other": "hello"
    },
    ".world": {
        "other": "hello"
    }
}
"""

JSON_ARB = b"""{
  "@@last_modified": "2019-11-06T22:41:37.002648",
  "Back": "Back",
  "@Back": {
    "type": "text",
    "placeholders": {}
  },
  "Next": "Next",
  "@Next": {
    "type": "text",
    "placeholders": {}
  },
  "Done": "Done",
  "@Done": {
    "type": "text",
    "placeholders": {}
  }
}
"""


class TestJSONResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.BaseJsonUnit


class TestJSONResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.JsonFile

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": "value"}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": "value"\n}\n'

    def test_can_not_detect(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(
                b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00b\xee\x9dh^\x01\x00\x00\x90\x04\x00\x00\x13\x00\x08\x02"
            )

    def test_error(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": "value"')

    def test_filter(self) -> None:
        store = self.StoreClass(filter=["key"])
        store.parse('{"key": "value", "other": "second"}')
        assert len(store.units) == 1
        assert store.units[0].source == "value"

    def test_ordering(self) -> None:
        store = self.StoreClass()
        store.parse(
            """{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz"
}"""
        )

        assert store.units[0].source == "foo"
        assert store.units[2].source == "baz"

    def test_args(self) -> None:
        store = self.StoreClass()
        store.parse(
            """{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz"
}"""
        )
        store.dump_args["sort_keys"] = True

        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b"""{
    "bar": "bar",
    "baz": "baz",
    "foo": "foo"
}
"""
        )

    def test_bom(self) -> None:
        content = "{}\n".encode("utf-8-sig")
        store = self.StoreClass()
        store.parse(content)
        assert len(store.units) == 0
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == content

    def test_complex(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_COMPLEX)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_COMPLEX

    def test_complex_array(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_COMPLEX_ARRAY)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_COMPLEX_ARRAY

    def test_add(self) -> None:
        expected = """{
    "simple.key": "source"
}
"""
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass(
            "source",
        )
        assert str(unit) != expected.strip()
        unit.setid("simple.key")
        store.addunit(unit)

        assert str(unit) == expected.strip()
        assert bytes(store).decode() == expected

    def test_add_list_like(self) -> None:
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass("source")
        unit.setid("[0]")
        store.addunit(unit)

        unit = self.StoreClass.UnitClass("source2")
        unit.setid("key")
        store.addunit(unit)

        assert (
            bytes(store).decode()
            == """{
    "[0]": "source",
    "key": "source2"
}
"""
        )
        unit.setid("[1]")
        assert (
            bytes(store).decode()
            == """{
    "[0]": "source",
    "[1]": "source2"
}
"""
        )

    def test_add_blank(self) -> None:
        expected = """{
    "simple.key": "source"
}
"""
        store = self.StoreClass()
        store.parse("true")

        unit = self.StoreClass.UnitClass(
            "source",
        )
        assert str(unit) != expected.strip()
        unit.setid("simple.key")
        store.addunit(unit)

        assert str(unit) == expected.strip()
        assert bytes(store).decode() == expected

    def test_types(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": 1}')
        assert store.units[0].target == 1
        store.units[0].target = 2

        assert (
            bytes(store).decode()
            == """{
    "key": 2
}
"""
        )
        store.units[0].target = "two"

        assert (
            bytes(store).decode()
            == """{
    "key": "two"
}
"""
        )

    def test_null(self) -> None:
        jsondata = """{
    "foo": [
        null,
        null,
        "Text"
    ]
}
"""
        store = self.StoreClass()
        store.parse(jsondata)
        assert len(store.units) == 3

        assert store.units[0].target is None
        assert store.units[1].target is None
        assert store.units[2].target == "Text"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == jsondata


class TestJSONNestedResourceStore(test_monolingual.TestMonolingualUnit):
    StoreClass = jsonl10n.JsonNestedFile

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": {"second": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue() == b'{\n    "key": {\n        "second": "value"\n    }\n}\n'
        )

    def test_ordering(self) -> None:
        # spellchecker:off
        data = b"""{
    "foo": "foo",
    "bar": {
        "ba1": "bag",
        "ba2": "bag",
        "ba3": "bag",
        "ba4": "baz"
    }
}
"""
        store = self.StoreClass()
        store.parse(data)

        assert store.units[0].source == "foo"
        assert store.units[1].getid() == ".bar.ba1"
        assert store.units[2].getid() == ".bar.ba2"
        assert store.units[3].getid() == ".bar.ba3"
        assert store.units[4].getid() == ".bar.ba4"
        # spellchecker:on

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == data

    def test_array(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_ARRAY)

        assert store.units[0].source == "One"
        assert store.units[0].getid() == ".key[0]"
        assert store.units[1].getid() == ".key[1]"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_ARRAY

    def test_add(self) -> None:
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass("source")
        unit.setid("simple.key")
        store.addunit(unit)

        expected = """{
    "simple": {
        "key": "source"
    }
}
"""
        assert bytes(store).decode() == expected

    def test_add_index(self) -> None:
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass("source")
        unit.setid("simple.list[2].key")
        store.addunit(unit)

        expected = """{
    "simple": {
        "list": [
            {},
            {},
            {
                "key": "source"
            }
        ]
    }
}
"""
        assert bytes(store).decode() == expected

    def test_add_index_nested(self) -> None:
        store = self.StoreClass()
        store.parse('{"foo":[["x", "y"]]}')

        assert len(store.units) == 2
        assert store.units[0].getid() == ".foo[0][0]"
        assert store.units[1].getid() == ".foo[0][1]"

        unit = self.StoreClass.UnitClass("source")
        unit.setid("values[2][0]")
        store.addunit(unit)

        expected = """{
    "foo": [
        [
            "x",
            "y"
        ]
    ],
    "values": [
        [],
        [],
        [
            "source"
        ]
    ]
}
"""
        assert bytes(store).decode() == expected

    @mark.parametrize(
        ("nested_id", "expected"),
        [
            ("values[0][1]", {"values": [[None, "new"]]}),
            ("values[0].child", {"values": [{"child": "new"}]}),
        ],
    )
    def test_replace_scalar_with_nested_structure(
        self, nested_id: str, expected: dict
    ) -> None:
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass("old")
        unit.setid("values[0]")
        store.addunit(unit)

        unit = self.StoreClass.UnitClass("new")
        unit.setid(nested_id)
        store.addunit(unit)

        assert json.loads(bytes(store)) == expected

    def test_nested_list_mixed(self) -> None:
        data = """{
    "story_9795": {
        "tsr_0": [
            [
                "‥",
                "Combination Carcer Tullianum & parco"
            ],
            "Archeologico del Colosseo"
        ]
    }
}
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getid() == ".story_9795.tsr_0[0][0]"
        assert store.units[1].getid() == ".story_9795.tsr_0[0][1]"
        assert store.units[2].getid() == ".story_9795.tsr_0[1]"

        assert bytes(store).decode() == data

        store = self.StoreClass()
        unit = self.StoreClass.UnitClass("Archeologico del Colosseo")
        unit.setid(".story_9795.tsr_0[1]")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("Combination Carcer Tullianum & parco")
        unit.setid(".story_9795.tsr_0[0][1]")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("‥")
        unit.setid(".story_9795.tsr_0[0][0]")
        store.addunit(unit)

        assert bytes(store).decode() == data

    def test_list_to_dict(self) -> None:
        data = """{
    "userInfoPage": [
        "Name"
    ]
}
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store).decode() == data

        unit = self.StoreClass.UnitClass("Test")
        unit.setid("userInfoPage.nesting")
        store.addunit(unit)
        assert (
            bytes(store).decode()
            == """{
    "userInfoPage": {
        "0": "Name",
        "nesting": "Test"
    }
}
"""
        )

    def test_complex_keys(self) -> None:
        data = """{
    "view": {
        "([^.,0-9]|^)1([^.,0-9]|$)": "View `x` comment",
        "": "View `x` comments"
    }
}
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert bytes(store).decode() == data

    def test_add_other(self) -> None:
        jsontext = """{
    "simple.key": "source"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)

        assert len(store.units) == 1
        assert store.units[0].source == "source"
        assert store.units[0].getid() == ".simple.key"

        assert bytes(store).decode() == jsontext

        newstore = self.StoreClass()
        newstore.addunit(store.units[0])

        assert bytes(newstore).decode() == jsontext

    @mark.parametrize(
        ("id_string", "expected"),
        [
            ("[0]", [("index", 0)]),
            ("test[0]", [("key", "test"), ("index", 0)]),
            (
                "test[0][1][2][3]",
                [
                    ("key", "test"),
                    ("index", 0),
                    ("index", 1),
                    ("index", 2),
                    ("index", 3),
                ],
            ),
            ("[test]selection", [("key", "[test]selection")]),
            ("[test][0]selection", [("key", "[test][0]selection")]),
            ("[0][test]selection", [("index", 0), ("key", "[test]selection")]),
            ("", [("key", "")]),
        ],
    )
    def test_from_string(self, id_string, expected) -> None:
        id_class = self.StoreClass.UnitClass.IdClass
        from_string = id_class.from_string
        assert from_string(id_string) == id_class(expected)

    def test_dot_keys(self) -> None:
        jsontext = """{
    "key.dot": "message"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        # Edit target
        store.units[0].target = "message"
        assert bytes(store).decode() == jsontext


class TestWebExtensionUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.WebExtensionJsonUnit


class TestWebExtensionStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.WebExtensionJsonFile

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key": {\n        "message": "value",\n        "description": "note"\n    }\n}\n'
        )

    def test_dot_keys(self) -> None:
        store = self.StoreClass()
        store.parse('{"key.dot": {"message": "value", "description": "note"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key.dot": {\n        "message": "value",\n        "description": "note"\n    }\n}\n'
        )

    def test_leading_dot_keys(self) -> None:
        jsontext = """{
    ".dot": {
        "message": "value",
        "description": "note"
    }
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert bytes(store).decode() == jsontext

    def test_serialize_no_description(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": {"message": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue() == b'{\n    "key": {\n        "message": "value"\n    }\n}\n'
        )

    def test_set_target(self) -> None:
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        store.units[0].target = "another"
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key": {\n        "message": "another",\n        "description": "note"\n    }\n}\n'
        )

    def test_placeholders(self) -> None:
        DATA = """{
    "youCanClose": {
        "message": "Bravo ! Votre compte $SITE$ est relié à Scrobbly. Vous pouvez fermer et revenir en arrière",
        "placeholders": {
            "site": {
                "content": "$1",
                "example": "AniList"
            }
        }
    }
}
""".encode()

        store = self.StoreClass()
        store.parse(DATA)
        assert store.units[0].placeholders is not None
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == DATA

    def test_comments(self) -> None:
        DATA = """{
    "test": {
        // Comment
        "message": "Message //"
    },
    "test//": { // Comment
        "message": "Message // Other"
    }
}
"""
        store = self.StoreClass()
        store.parse(DATA)
        assert len(store.units) == 2
        # Any comments will be stripped
        assert (
            bytes(store).decode()
            == """{
    "test": {
        "message": "Message //"
    },
    "test//": {
        "message": "Message // Other"
    }
}
"""
        )

    def test_invalid_top_level_entry(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": "value"}')

    def test_invalid_message_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"message": {"nested": "value"}}}')

    def test_invalid_description_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"message": "value", "description": {}}}')

    def test_invalid_placeholders_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"message": "value", "placeholders": []}}')


class TestI18NextStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.I18NextFile

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_I18NEXT)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == JSON_I18NEXT

    def test_units(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_I18NEXT)
        assert len(store.units) == 4

    def test_plurals(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_I18NEXT)

        # Remove plurals
        store.units[2].target = "Ahoj"
        store.units[3].target = "Nazdar"
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_I18NEXT_PLURAL

        # Bring back plurals
        store.units[2].target = multistring(
            [
                "the singular",
                "the plural",
            ]
        )
        store.units[3].target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
                "the plural form 5",
            ]
        )
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == JSON_I18NEXT

    def test_nested_array(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_I18NEXT_NESTED_ARRAY)

        assert len(store.units) == 4
        assert store.units[0].getid() == ".apps[0].title"
        assert store.units[1].getid() == ".apps[0].description"
        assert store.units[2].getid() == ".apps[1].title"
        assert store.units[3].getid() == ".apps[1].description"

        assert bytes(store).decode() == JSON_I18NEXT_NESTED_ARRAY

    def test_new_plural(self) -> None:
        EXPECTED = """{
    "simple": "the singular",
    "simple_plural": "the plural",
    "simple2": "the singular",
    "simple2_plural": "the plural",
    "complex_0": "the plural form 0",
    "complex_1": "the plural form 1",
    "complex_2": "the plural form 2",
    "complex_3": "the plural form 3",
    "complex_4": "the plural form 4",
    "complex_5": "the plural form 5"
}
"""
        store = self.StoreClass()
        store.settargetlanguage("ar")

        unit = self.StoreClass.UnitClass(
            multistring(
                [
                    "the singular",
                    "the plural",
                ]
            ),
            "simple",
        )
        store.addunit(unit)

        unit = self.StoreClass.UnitClass(
            multistring(
                [
                    "the singular",
                    "the plural",
                ]
            ),
        )
        unit.setid("simple2")
        store.addunit(unit)

        unit = self.StoreClass.UnitClass(
            "complex",
            "complex",
        )
        unit.target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
                "the plural form 5",
                "the plural form 6",
            ]
        )
        store.addunit(unit)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == EXPECTED

    def test_new_plural_id(self) -> None:
        EXPECTED = """{
    "simple_0": "the singular"
}
"""
        store = self.StoreClass()
        store.settargetlanguage("id")

        unit = self.StoreClass.UnitClass(
            multistring(
                [
                    "the singular",
                ]
            ),
            "simple",
        )
        store.addunit(unit)

        assert bytes(store).decode() == EXPECTED


class TestGoTextJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.GoTextJsonFile

    def test_plurals(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOTEXT)

        assert len(store.units) == 2
        assert store.units[0].target == multistring(["{N} tag", "{N} tags"])
        assert store.units[1].target == "Table"

        assert bytes(store).decode() == JSON_GOTEXT.decode()

    def test_plurals_missing(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOTEXT)

        store.units[0].target = multistring(["{N} tag"])

        assert (
            "other"
            not in json.loads(bytes(store))["messages"][0]["translation"]["select"][
                "cases"
            ]
        )

    def test_case_no_msg(self) -> None:
        store = self.StoreClass()
        store.parse(
            """{
    "language": "en-US",
    "messages": [
        {
            "id": "{N} more files remaining!",
            "key": "%d more files remaining!",
            "message": "{N} more files remaining!",
            "translation": {
                "select": {
                    "feature": "plural",
                    "cases": {
                        "one": "One file remaining!",
                        "other": "There are {N} more files remaining!"
                    }
                }
            }
        }
    ]
}
"""
        )

        assert len(store.units) == 1
        assert store.units[0].target == multistring(
            ["One file remaining!", "There are {N} more files remaining!"]
        )

        assert (
            bytes(store).decode()
            == """{
    "language": "en-US",
    "messages": [
        {
            "id": "{N} more files remaining!",
            "message": "{N} more files remaining!",
            "key": "%d more files remaining!",
            "translation": {
                "select": {
                    "feature": "plural",
                    "cases": {
                        "one": "One file remaining!",
                        "other": "There are {N} more files remaining!"
                    }
                }
            }
        }
    ]
}
"""
        )

    def test_sparse_selector_edits(self) -> None:
        message = {
            "id": "k",
            "translation": {
                "select": {
                    "feature": "plural",
                    "arg": "n",
                    "cases": {
                        "other": {"msg": "old", "note": "keep"},
                        "=2": {"msg": "two"},
                    },
                }
            },
        }
        store = self.StoreClass()
        store.parse(json.dumps({"language": "en", "messages": [message]}))
        unit = store.units[0]
        unit.rich_source = unit.multistring_to_rich("edited")
        cases = message["translation"]["select"]["cases"]
        cases["other"]["msg"] = "edited"
        assert json.loads(bytes(store))["messages"] == [message]
        unit.update_plural_forms({"many": "fraction"})
        clone = unit.buildfromunit(unit)
        assert clone == unit
        clone.update_plural_forms({"many": "other fraction"})
        assert clone != unit
        clone.target.extra_strings.append("single")
        assert clone.plural_forms == {
            "other": "edited",
            "many": "other fraction",
            "one": "single",
        }
        clone.update_plural_forms({"other": "clone"})
        assert unit.plural_forms["other"] == "edited"

    def test_native_merge_before_binding_keeps_sparse_label(self) -> None:
        store = self.StoreClass.parsestring(
            b'{"language":"en","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"other":"rest"}}}}]}'
        )
        unit = store.UnitClass("old")
        unit.merge(store.units[0], overwrite=True)
        destination = self.StoreClass()
        destination.settargetlanguage("cs")
        destination.addunit(unit)
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(destination))["messages"][0]["translation"]["select"][
            "cases"
        ] == {"other": "rest"}

    def test_rich_edit_after_retargeting_selector(self) -> None:
        store = self.StoreClass()
        selector = {"feature": "plural", "cases": {"one": "1", "few": "2", "many": "5"}}
        store.parse(
            json.dumps(
                {
                    "language": "ru",
                    "messages": [{"id": "k", "translation": {"select": selector}}],
                }
            )
        )
        store.settargetlanguage("cs")
        unit = store.units[0]
        unit.rich_target = unit.multistring_to_rich(multistring(["one", "few", "rest"]))
        assert unit.plural_forms == {
            "one": "one",
            "few": "few",
            "many": "5",
            "other": "rest",
        }

    def test_rich_roundtrip_exact_cases(self) -> None:
        selector = {"feature": "plural", "arg": "n", "cases": {"=2": {"msg": "two"}}}
        catalog = {
            "language": "en",
            "messages": [{"id": "k", "translation": {"select": selector}}],
        }
        store = self.StoreClass()
        store.parse(json.dumps(catalog))
        unit = store.units[0]
        assert unit.plural_forms == {}
        unit.plural_forms = {}
        assert unit.istranslated()
        assert store.findid("k") is unit
        unit.merge(jsonl10n.FlatJsonUnit("replacement"))
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(store)) == catalog

    def test_scalar_merge_into_exact_selector(self) -> None:
        store = self.StoreClass.parsestring(
            '{"language":"en","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"=2":{"msg":"two"}}}}}]}'
        )
        store.units[0].merge(jsonl10n.FlatJsonUnit("replacement"), overwrite=True)
        cases = json.loads(bytes(store))["messages"][0]["translation"]["select"][
            "cases"
        ]
        assert cases == {"=2": {"msg": "two"}, "other": {"msg": "replacement"}}

    def test_detached_scalar_then_plural(self) -> None:
        store = self.StoreClass.parsestring(
            '{"language":"en","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"one":"old","other":"rest"}}}}]}'
        )
        unit = store.units[0].copy()
        unit.target = "scalar"
        unit.target = multistring(["new one", "new rest"])
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert self.StoreClass.parsestring(bytes(destination)).units[
            0
        ].plural_forms == {"one": "new one", "other": "new rest"}

    def test_unattached_positional_donor(self) -> None:
        store = self.StoreClass.parsestring(
            '{"language":"en","messages":[{"id":"k","translation":"old"}]}'
        )
        donor = jsonl10n.GoTextJsonUnit(multistring(["single", "rest"]))
        store.units[0].merge(donor, overwrite=True)
        saved = self.StoreClass.parsestring(bytes(store))
        assert saved.units[0].plural_forms == {"one": "single", "other": "rest"}
        assert donor.plural_forms is None

    def test_nonplural_selector_retains_cases(self) -> None:
        selector = {"feature": "gender", "cases": {"one": "a", "other": "b"}}
        catalog = {"messages": [{"id": "k", "translation": {"select": selector}}]}
        store = self.StoreClass.parsestring(json.dumps(catalog))
        unit = store.units[0]
        assert unit.plural_forms is None
        unit.target.extra_strings[0] = "edit"
        assert (
            json.loads(bytes(store))["messages"][0]["translation"]["select"] == selector
        )

    def test_bind_detached_append(self) -> None:
        store = self.StoreClass()
        store.parse(
            '{"language":"cs","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"one":"one"}}}}]}'
        )
        unit = store.units[0].copy()
        unit.target.extra_strings.append("few")
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert unit.plural_forms == {"one": "one", "few": "few"}

    def test_merge_native_selector(self) -> None:
        store = self.StoreClass()
        donor = self.StoreClass()
        selector = {
            "feature": "plural",
            "arg": "n",
            "cases": {"many": {"msg": "fraction"}, "=2": {"msg": "two"}},
        }
        donor.parse(
            json.dumps(
                {
                    "language": "en",
                    "messages": [{"id": "k", "translation": {"select": selector}}],
                }
            )
        )
        store.parse(
            '{"language":"en","messages":[{"id":"k","translation":"old","comment":"keep"}]}'
        )
        store.units[0].merge(donor.units[0], overwrite=True)
        result = json.loads(bytes(store))["messages"][0]
        assert result["comment"] == "keep"
        assert (
            result["translation"]
            == json.loads(bytes(donor))["messages"][0]["translation"]
        )

    def test_merge_foreign_plural_categories(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse(
            '{"language":"cs","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"one":"1","many":"fraction","other":"5"}}}}]}'
        )
        unit = store.units[0]
        donor = jsonl10n.I18NextV4File()
        donor.settargetlanguage("cs")
        donor.parse('{"k_one":"single","k_few":"several","k_other":"rest"}')
        unit.merge(donor.units[0], overwrite=True)
        assert unit.plural_forms == {"one": "single", "few": "several", "other": "rest"}
        assert (
            type(store).parsestring(bytes(store)).units[0].plural_forms
            == unit.plural_forms
        )

    def test_foreign_scalar_merge(self) -> None:
        store = self.StoreClass()
        store.parse(
            '{"language":"en","messages":[{"id":"k","translation":{"select":{"feature":"plural","cases":{"one":"one","other":"rest"}}}}]}'
        )
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = "replacement"
        store.settargetlanguage("cs")
        unit.merge(donor, overwrite=True)
        assert unit.plural_forms["other"] == "replacement"
        unit.rich_target = unit.rich_target
        assert unit.plural_forms["other"] == "replacement"

    def test_named_forms(self) -> None:
        cases = {
            "other": "",
            "many": {"msg": "fraction", "note": "keep"},
            "=2": {"msg": "two"},
        }
        selector = {"feature": "plural", "arg": "count", "cases": cases}
        msg = {"id": "k", "translation": {"select": selector}}
        store = self.StoreClass()
        store.parse(json.dumps({"language": "cs", "messages": [msg]}))
        assert json.loads(bytes(store))["messages"][0] == msg
        unit = store.units[0]
        assert unit.plural_forms == {"many": "fraction", "other": ""}
        unit.update_plural_forms({"many": "updated", "other": None, "few": "few"})
        with raises(ValueError):
            unit.plural_forms = {}
        expected = {
            "many": {"msg": "updated", "note": "keep"},
            "=2": {"msg": "two"},
            "few": {"msg": "few"},
        }
        assert json.loads(bytes(store))["messages"][0]["translation"]["select"] == {
            **selector,
            "cases": expected,
        }
        assert self.reparse(store).units[0].plural_forms == unit.plural_forms

    def test_complex_id(self) -> None:
        text = """{
    "language": "en-US",
    "messages": [
        {
            "id": [
                "msgOutOfOrder",
                "{Device} is out of order!"
            ],
            "message": "{Device} is out of order!",
            "key": "%s is out of order!",
            "translation": ""
        },
        {
            "id": "[DEBUG] msg",
            "message": "[DEBUG] msg",
            "key": "[DEBUG] msg",
            "translation": ""
        }
    ]
}
"""
        store = self.StoreClass()
        store.parse(text)

        assert len(store.units) == 2
        assert (
            store.units[0].getid() == "['msgOutOfOrder', '{Device} is out of order!']"
        )
        assert store.units[1].getid() == "[DEBUG] msg"

        assert bytes(store).decode() == text

    def test_invalid_messages_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"language": "en-US", "messages": {}}')

    def test_invalid_message_entry(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"language": "en-US", "messages": ["text"]}')

    def test_invalid_translation_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"language": "en-US", "messages": [{"translation": []}]}')

    def test_invalid_plural_case_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(
                '{"language": "en-US", "messages": [{"translation": '
                '{"select": {"cases": {"one": {}}}}}]}'
            )


class TestI18NextV4Store(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.I18NextV4File
    DeepUnpluralizedJson = JSON_I18NEXT_PLURAL
    PartiallyPluralizedJson = JSON_I18NEXT_V4
    CorrectlyPluralizedJson = JSON_I18NEXT_V4_FIXED

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "ar"
        store.parse(JSON_I18NEXT_V4)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == JSON_I18NEXT_V4

    def test_units(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "ar"
        store.parse(self.PartiallyPluralizedJson)
        assert len(store.units) == 4

    def test_named_forms(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "cs"
        data = {
            "k_many": "fraction",
            "k_unknown": "ordinary",
            "k_other": "",
            "k_one": "unit",
        }
        store.parse(json.dumps(data))
        unit = store.units[0]
        snapshot = unit.plural_forms
        assert snapshot == {"many": "fraction", "other": "", "one": "unit"}
        assert unit.target.strings == ["unit", "", ""]
        unit.plural_forms = snapshot
        assert list(json.loads(bytes(store)).items()) == list(data.items())
        unit.update_plural_forms({"few": "few", "other": "other"})
        unit.target = multistring(["one", "few", "several"])
        assert unit.plural_forms == {
            "one": "one",
            "few": "few",
            "many": "fraction",
            "other": "several",
        }
        assert snapshot["other"] == ""
        with raises(ValueError):
            unit.update_plural_forms({"many": "lost", "invalid": "bad"})
        with raises(ValueError):
            unit.plural_forms = {}
        unit.update_plural_forms({"other": None})
        assert "other" not in unit.plural_forms
        unit.plural_forms = {"many": "fraction", "few": ""}
        reparsed = self.StoreClass()
        reparsed.parse(bytes(store))
        assert reparsed.units[0].plural_forms == unit.plural_forms
        assert json.loads(bytes(store)) == {
            "k_many": "fraction",
            "k_unknown": "ordinary",
            "k_few": "",
        }

    def test_fractional_status_and_index(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "cs"
        store.parse('{"k_many": "fraction"}')
        unit = store.units[0]
        assert not unit.target
        unit.target = unit.target
        assert json.loads(bytes(store)) == {"k_many": "fraction"}
        assert unit.istranslated()
        assert unit.istranslatable()
        assert not unit.isblank()
        assert store.findid(unit.getid()) is unit
        unit.update_plural_forms({"many": ""})
        assert not unit.istranslated()
        assert not unit.istranslatable()
        assert unit.isblank()
        assert unit.getid() not in store.getids()
        unit.target = multistring(["one"])
        assert store.findid(unit.getid()) is unit
        unit.target = multistring([""])
        assert store.findid(unit.getid()) is None

    def test_retarget_positional(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "ru"
        original = {"k_one": "1", "k_few": "2", "k_many": "5"}
        store.parse(json.dumps(original))
        store.settargetlanguage("cs")
        assert json.loads(bytes(store)) == original
        store.units[0].target = multistring(["jeden", "dva", "ostatní"])
        assert json.loads(bytes(store)) == {
            "k_one": "jeden",
            "k_few": "dva",
            "k_many": "5",
            "k_other": "ostatní",
        }

    @mark.parametrize(
        ("language", "original", "expected"),
        [
            (
                "ru",
                {"k_one": "1", "k_few": "2", "k_many": "5"},
                {"k_one": "1", "k_few": "2", "k_many": "5", "k_other": "5"},
            ),
            (None, {"k_one": "1", "k_other": "5"}, {"k_one": "1", "k_few": "5"}),
        ],
    )
    def test_rebind_detached_projection(self, language, original, expected) -> None:
        source = self.StoreClass()
        source.settargetlanguage(language)
        source.parse(json.dumps(original))
        unit = source.units[0]
        source.removeunit(unit)

        destination = self.StoreClass()
        destination.settargetlanguage("cs")
        destination.addunit(unit)
        assert json.loads(bytes(destination)) == original

        unit.target = unit.target
        assert json.loads(bytes(destination)) == expected

    def test_shorter_positional(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse('{"k_other": "other", "k_one": "one", "k_many": ""}')
        store.units[0].target = multistring(["new one"])
        assert json.loads(bytes(store)) == {"k_one": "new one", "k_many": ""}

    def test_oversized_positional(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "cs"
        store.parse('{"k_one": "one", "k_many": "fraction"}')
        unit = store.units[0]
        original = bytes(store)
        oversized = multistring(["a", "b", "c", "d"])
        with raises(ValueError, match="4 positional forms to one, few, other"):
            unit.target = oversized
        assert bytes(store) == original
        with raises(ValueError, match="4 positional forms"):
            store.addunit(store.UnitClass(oversized, "new"))
        assert store.units == [unit]
        unit.target.extra_strings.append("extra")
        with raises(ValueError, match="4 positional forms"):
            bytes(store)

    def test_plural_tags_resolved_once(self, monkeypatch) -> None:
        """Resolve invariant locale plural tags once for the whole catalog."""
        store = self.StoreClass()
        store.targetlanguage = "en"
        get_plural_tags = store.get_plural_tags
        get_plural_tags_calls = 0

        def counting_get_plural_tags():
            nonlocal get_plural_tags_calls
            get_plural_tags_calls += 1
            return get_plural_tags()

        monkeypatch.setattr(store, "get_plural_tags", counting_get_plural_tags)
        messages = {
            f"message_{index}_{suffix}": suffix
            for index in range(100)
            for suffix in ("one", "other")
        }

        store.parse(json.dumps(messages))

        assert len(store.units) == 100
        assert get_plural_tags_calls == 1

    def test_plural_base_processed_once(self) -> None:
        """Do not duplicate a group containing an extra CLDR plural form."""
        store = self.StoreClass()
        store.targetlanguage = "en"

        store.parse(
            '{"message_one": "one", "message_other": "other", "message_few": "few"}'
        )

        assert len(store.units) == 1

    def test_nested_object_with_plural_suffix(self) -> None:
        """Do not treat a nested object as a plural form."""
        data = """{
    "section_other": {
        "related_space_usage": "Analyze the space usage within the database",
        "related_space_usage_description": "See which items take up space."
    }
}
"""
        store = self.StoreClass()
        store.targetlanguage = "en"

        store.parse(data)

        assert [unit.getid() for unit in store.units] == [
            ".section_other.related_space_usage",
            ".section_other.related_space_usage_description",
        ]
        assert bytes(store).decode() == data

    def test_mixed_plural_values_are_regular_entries(self) -> None:
        """Do not partially group plural-like entries containing an object."""
        data = """{
    "message_one": "one",
    "message_other": "other",
    "message_few": {
        "nested": "value"
    }
}
"""
        store = self.StoreClass()
        store.targetlanguage = "en"

        store.parse(data)

        assert [unit.getid() for unit in store.units] == [
            ".message_one",
            ".message_other",
            ".message_few.nested",
        ]
        assert bytes(store).decode() == data

    def test_plurals(self) -> None:
        store = self.StoreClass()
        store.targetlanguage = "ar"
        store.parse(self.PartiallyPluralizedJson)

        # Remove plurals
        store.units[2].target = "Ahoj"
        store.units[3].target = "Nazdar"
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == self.DeepUnpluralizedJson

        # Bring back plurals
        store.settargetlanguage("ar")
        store.units[2].target = multistring(
            [
                "",
                "the singular",
                "",
                "",
                "",
                "the plural",
            ]
        )
        store.units[3].target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
                "the plural form 5",
            ]
        )
        with raises(ValueError, match="7 positional forms"):
            store.units[3].target = multistring(
                [*store.units[3].target.strings, "extra"]
            )
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == self.CorrectlyPluralizedJson

    def test_nested_array(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_I18NEXT_NESTED_ARRAY)

        assert len(store.units) == 4
        assert store.units[0].getid() == ".apps[0].title"
        assert store.units[1].getid() == ".apps[0].description"
        assert store.units[2].getid() == ".apps[1].title"
        assert store.units[3].getid() == ".apps[1].description"

        assert bytes(store).decode() == JSON_I18NEXT_NESTED_ARRAY

        newstore = self.StoreClass()
        newstore.parse(JSON_I18NEXT_NESTED_ARRAY_BEFORE)

        assert len(newstore.units) == 1

        newstore.addunit(store.units[0])
        newstore.addunit(store.units[1])
        newstore.addunit(store.units[2])
        newstore.addunit(store.units[3])

        assert bytes(newstore).decode() == JSON_I18NEXT_NESTED_ARRAY

    def test_new_plural(self) -> None:
        EXPECTED = """{
    "simple_zero": "the singular",
    "simple_one": "the plural",
    "complex_zero": "the plural form 0",
    "complex_one": "the plural form 1",
    "complex_two": "the plural form 2",
    "complex_few": "the plural form 3",
    "complex_many": "the plural form 4",
    "complex_other": "the plural form 5"
}
"""
        store = self.StoreClass()
        store.settargetlanguage("ar")

        unit = self.StoreClass.UnitClass(
            multistring(
                [
                    "the singular",
                    "the plural",
                ]
            ),
            "simple",
        )
        store.addunit(unit)

        unit = self.StoreClass.UnitClass(
            "complex",
            "complex",
        )
        store.addunit(unit)
        unit.target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
                "the plural form 5",
            ]
        )

        assert bytes(store).decode() == EXPECTED

    def test_unknown_language_single_plural_uses_other(self) -> None:
        expected = """{
    "simple_other": "the only form"
}
"""
        store = self.StoreClass()
        store.settargetlanguage("tok")

        unit = self.StoreClass.UnitClass(multistring(["the only form"]), "simple")
        store.addunit(unit)

        assert bytes(store).decode() == expected

    def test_ru(self) -> None:
        data = """{
"bet_one": "еще +{{count}} ставка",
"bet_few": "еще +{{count}} ставки",
"bet_many": "еще +{{count}} ставок"
}
"""
        store = self.StoreClass()
        store.settargetlanguage("ru")
        store.parse(data)

        assert len(store.units) == 1
        assert store.units[0].source.strings == [
            "еще +{{count}} ставка",
            "еще +{{count}} ставки",
            "еще +{{count}} ставок",
        ]


class TestFlatI18NextV4Store(TestI18NextV4Store):
    StoreClass = jsonl10n.FlatI18NextV4File
    DeepUnpluralizedJson = JSON_FLAT_I18NEXT_V4_PLURAL
    PartiallyPluralizedJson = JSON_FLAT_I18NEXT_V4
    CorrectlyPluralizedJson = JSON_FLAT_I18NEXT_V4_FIXED


class TestGoI18NJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.GoI18NJsonFile

    @mark.parametrize(("original", "added"), [("one", "other"), ("other", "one")])
    def test_extend_sparse_target(self, original, added) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        entry = {"id": "k", "translation": {original: "first"}}
        store.parse(json.dumps([entry]))
        unit = store.units[0]
        unit.target.extra_strings.append("second")
        entry["translation"][added] = "second"
        assert json.loads(bytes(store)) == [entry]
        unit.target = unit.target
        assert json.loads(bytes(store)) == [entry]
        unit.target.extra_strings.append("unrepresentable")
        with raises(ValueError, match="3 positional forms"):
            bytes(store)

    def test_build_from_foreign_named_unit(self) -> None:
        source = jsonl10n.I18NextV4File()
        source.settargetlanguage("cs")
        source.parse('{"k_other":"rest","k_many":"fraction"}')
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.addunit(store.UnitClass.buildfromunit(source.units[0]))
        assert json.loads(bytes(store)) == [
            {
                "id": source.units[0].getid(),
                "translation": {"other": "rest", "many": "fraction"},
            }
        ]

    def test_buildfromunit_preserves_named_forms(self) -> None:
        source = self.StoreClass()
        source.settargetlanguage("en")
        translation = {"other": "old", "custom": "keep"}
        catalog = [{"id": "k", "description": "note", "translation": translation}]
        source.parse(json.dumps(catalog))
        unit = source.units[0]
        unit.update_plural_forms({"many": "fraction"})
        clone = unit.buildfromunit(unit)
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(clone)
        assert clone.target.strings == ["old"]
        assert clone.plural_forms == {"other": "old", "many": "fraction"}
        translation["many"] = "fraction"
        assert json.loads(bytes(destination)) == catalog
        clone.update_plural_forms({"other": "edited"})
        assert json.loads(bytes(source)) == catalog

    @mark.parametrize("assignment", ["replace", "append"])
    @mark.parametrize("detach", ["copy", "remove"])
    def test_edit_detached_sparse_projection(self, assignment, detach) -> None:
        store = self.StoreClass(BytesIO(b'[{"id":"k","translation":{"one":"one"}}]'))
        store.settargetlanguage("cs")
        unit = store.units[0]
        if detach == "copy":
            unit = unit.buildfromunit(unit)
        else:
            store.removeunit(unit)
        if assignment == "replace":
            unit.target = multistring(["one", "few"])
        else:
            unit.target.extra_strings.append("few")
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert json.loads(bytes(destination))[0]["translation"] == {
            "one": "one",
            "few": "few",
        }

    def test_expand_after_setting_language(self) -> None:
        store = self.StoreClass(BytesIO(b'[{"id":"k","translation":{"one":"one"}}]'))
        store.settargetlanguage("cs")
        unit = store.units[0]
        unit.target.extra_strings.append("few")
        assert unit.plural_forms == {"one": "one", "few": "few"}
        unit.target.extra_strings.append("other")
        forms = {"one": "one", "few": "few", "other": "other"}
        assert json.loads(bytes(store))[0]["translation"] == forms
        store.removeunit(unit)
        assert unit.plural_forms == forms

    @mark.parametrize("read_before_detaching", [True, False])
    def test_move_expanded_target(self, read_before_detaching) -> None:
        source = self.StoreClass()
        source.settargetlanguage("cs")
        source.parse('[{"id": "k", "translation": {"one": "one"}}]')
        unit = source.units[0]
        unit.target.extra_strings.append("few")
        forms = {"one": "one", "few": "few"}
        if read_before_detaching:
            assert unit.plural_forms == forms
        source.removeunit(unit)
        assert unit.plural_forms == forms
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert json.loads(bytes(destination))[0]["translation"] == forms

    def test_merge_singleton_into_scalar(self) -> None:
        store = self.StoreClass.parsestring(b'[{"id":"k","translation":""}]')
        donor = self.StoreClass.parsestring(
            b'[{"id":"k","translation":{"one":"item"}}]'
        )
        store.units[0].merge(donor.units[0], overwrite=True)
        assert json.loads(bytes(store))[0]["translation"] == {"one": "item"}

    def test_merge_positional_donor(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse(
            '[{"id":"k","translation":{"one":"1","many":"fraction","other":"5"}}]'
        )
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = multistring(["single", "several", "rest"])
        unit.merge(donor, overwrite=True)
        saved = self.StoreClass.parsestring(bytes(store))
        assert saved.units[0].plural_forms == {
            "one": "single",
            "few": "several",
            "other": "rest",
            "many": "fraction",
        }

    @mark.parametrize("detached", [False, True])
    def test_direct_named_edit_after_retarget(self, detached) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ru")
        store.parse('[{"id":"k","translation":{"one":"1","few":"2","many":"5"}}]')
        unit = store.units[0]
        store.settargetlanguage("cs")
        if detached:
            store.removeunit(unit)
        forms = {"one": "single", "few": "several", "other": "rest"}
        unit.plural_forms = forms
        unit.rich_target = unit.rich_target
        assert unit.plural_forms == forms
        if detached:
            store.addunit(unit)
        assert json.loads(bytes(store)) == [{"id": "k", "translation": forms}]

    @mark.parametrize("detached", [False, True])
    def test_merge_foreign_plural_categories(self, detached) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ru" if detached else "cs")
        store.parse(
            '[{"id":"k","translation":{"one":"1","many":"fraction","other":"5"}}]'
        )
        unit = store.units[0]
        store.settargetlanguage("cs")
        if detached:
            store.removeunit(unit)
        donor = jsonl10n.I18NextV4File()
        donor.settargetlanguage("cs")
        donor.parse('{"k_one":"single","k_few":"several","k_other":"rest"}')
        unit.merge(donor.units[0], overwrite=True)
        if detached:
            store.addunit(unit)
        unit.rich_target = unit.rich_target
        assert unit.plural_forms == {"one": "single", "few": "several", "other": "rest"}
        assert (
            type(store).parsestring(bytes(store)).units[0].plural_forms
            == unit.plural_forms
        )

    def test_foreign_scalar_merge(self) -> None:
        store = self.StoreClass()
        store.parse('[{"id":"k","translation":{"one":"one","other":"rest"}}]')
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = "replacement"
        store.settargetlanguage("cs")
        unit.merge(donor, overwrite=True)
        assert unit.plural_forms["other"] == "replacement"
        unit.rich_target = unit.rich_target
        assert unit.plural_forms["other"] == "replacement"

    def test_named_forms(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        forms = {"many": "fraction", "other": ""}
        catalog = [{"id": "k", "description": "keep", "translation": forms}]
        store.parse(json.dumps(catalog))
        unit = store.units[0]
        assert json.loads(bytes(store)) == catalog
        assert unit.plural_forms == forms
        unit.target = unit.target
        assert unit.plural_forms == forms
        assert store.findid(unit.getid()) is unit
        with raises(ValueError, match="4 positional forms"):
            unit.target = multistring(["a", "b", "c", "d"])
        assert json.loads(bytes(store)) == catalog
        unit.update_plural_forms({"one": "one", "other": None})
        assert unit.plural_forms == {"many": "fraction", "one": "one"}
        with raises(ValueError):
            unit.plural_forms = {}
        unit.plural_forms = {"many": "fraction"}
        parsed = self.StoreClass()
        parsed.parse(bytes(store))
        assert parsed.units[0].plural_forms == {"many": "fraction"}
        assert parsed.units[0].getnotes() == "keep"

    def test_plurals(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOI18N)

        assert len(store.units) == 2
        assert store.units[0].target == multistring(
            ["{{.count}} tag", "{{.count}} tags"]
        )
        assert store.units[1].target == "Table"

        assert bytes(store).decode() == JSON_GOI18N.decode()

    def test_plurals_missing(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOI18N)

        store.units[0].target = multistring(["{{.count}} tag"])

        assert "other" not in json.loads(bytes(store))[0]["translation"]

    def test_unknown_language_single_plural_uses_other(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("tok")

        unit = self.StoreClass.UnitClass(multistring(["{{.count}} tag"]), "tag")
        store.addunit(unit)

        output = bytes(store).decode()
        assert '"other": "{{.count}} tag"' in output
        assert '"one"' not in output

    def test_invalid(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(JSON_I18NEXT_PLURAL)

    def test_invalid_entry(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('["text"]')

    def test_invalid_translation_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('[{"id": "key", "translation": []}]')

    def test_invalid_plural_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('[{"id": "key", "translation": {"one": []}}]')

    def test_dot_keys(self) -> None:
        jsontext = """[
    {
        "id": ".table",
        "translation": "message"
    }
]
"""
        store = self.StoreClass()
        store.parse(jsontext)
        # Edit target
        store.units[0].target = "message"
        assert bytes(store).decode() == jsontext


class TestGoI18NV2JsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.GoI18NV2JsonFile

    @mark.parametrize(
        ("message", "edited"),
        [
            ("old", "new"),
            (
                {"description": "note", "other": "old"},
                {"description": "note", "other": "new"},
            ),
            ({"many": "old"}, {"many": "new"}),
        ],
    )
    def test_rich_edit_single_form(self, message, edited) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(json.dumps({"k": message}))
        unit = store.units[0]
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(store)) == {"k": message}
        unit.rich_source = store.UnitClass("new").rich_source
        assert json.loads(bytes(store)) == {"k": edited}
        unit.rich_source = store.UnitClass("old").rich_source
        unit.merge(store.UnitClass("new"), overwrite=True)
        assert json.loads(bytes(store)) == {"k": edited}

    def test_buildfromunit_preserves_named_forms(self) -> None:
        source = self.StoreClass()
        source.settargetlanguage("en")
        entry = {"description": "note", "other": "old", "custom": "keep"}
        catalog = {"k": entry}
        source.parse(json.dumps(catalog))
        unit = source.units[0]
        unit.update_plural_forms({"many": "fraction"})
        clone = unit.buildfromunit(unit)
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(clone)
        assert clone.target.strings == ["old"]
        assert clone.plural_forms == {"other": "old", "many": "fraction"}
        entry["many"] = "fraction"
        assert json.loads(bytes(destination)) == catalog
        clone.update_plural_forms({"other": "edited"})
        assert json.loads(bytes(source)) == catalog

    @mark.parametrize("attribute", ["rich_source", "rich_target"])
    def test_rich_edit_after_language_change(self, attribute) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ru")
        store.parse('{"k":{"one":"1","few":"2","many":"5"}}')
        store.settargetlanguage("cs")
        unit = store.units[0]
        edited = unit.multistring_to_rich(multistring(["one", "few", "rest"]))
        setattr(unit, attribute, edited)
        assert json.loads(bytes(store))["k"] == {
            "one": "one",
            "few": "few",
            "many": "5",
            "other": "rest",
        }

    def test_merge_positional_donor(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse('{"k":{"one":"1","many":"fraction","other":"5"}}')
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = multistring(["single", "several", "rest"])
        unit.merge(donor, overwrite=True)
        saved = self.StoreClass.parsestring(bytes(store))
        assert saved.units[0].plural_forms == {
            "one": "single",
            "few": "several",
            "other": "rest",
            "many": "fraction",
        }

    def test_merge_foreign_plural_categories(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse('{"k":{"one":"1","many":"fraction","other":"5"}}')
        unit = store.units[0]
        donor = jsonl10n.I18NextV4File()
        donor.settargetlanguage("cs")
        donor.parse('{"k_one":"single","k_few":"several","k_other":"rest"}')
        unit.merge(donor.units[0], overwrite=True)
        assert unit.plural_forms == {"one": "single", "few": "several", "other": "rest"}
        assert (
            type(store).parsestring(bytes(store)).units[0].plural_forms
            == unit.plural_forms
        )

    @mark.parametrize("native", [False, True])
    @mark.parametrize("detached", [False, True])
    def test_merge_scalar_into_plural(self, native, detached) -> None:
        store = self.StoreClass()
        message = {"description": "keep", "one": "singular", "other": "plural"}
        store.parse(json.dumps({"k": message}))
        donor = (
            self.StoreClass(BytesIO(b'{"k": "new"}')).units[0]
            if native
            else jsonl10n.FlatJsonUnit("new")
        )
        store.settargetlanguage("cs")
        unit = store.units[0]
        unit.merge(donor)
        assert json.loads(bytes(store)) == {"k": message}
        if detached:
            store.removeunit(unit)
        unit.merge(donor, overwrite=True)
        if detached:
            store.addunit(unit)
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(store)) == {
            "k": {"description": "keep", "other": "new"}
        }

    def test_index_after_projection_expands(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse('{"k":{"one":""}}')
        unit = store.units[0]
        assert store.findid("k") is None
        unit.target.extra_strings.append("new")
        assert unit.plural_forms == {"one": "", "other": "new"}
        assert store.findid("k") is unit

    def test_bind_detached_append(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse('{"k":{"one":"one"}}')
        unit = store.units[0].copy()
        unit.target.extra_strings.append("few")
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert unit.plural_forms == {"one": "one", "few": "few"}

    @mark.parametrize(("original", "replacement"), [(None, "en"), ("en", "en-US")])
    def test_equivalent_locale_keeps_sparse_labels(self, original, replacement) -> None:
        store = self.StoreClass()
        store.settargetlanguage(original)
        store.parse('{"k":{"description":"keep","other":"value"}}')
        unit = store.units[0]
        store.settargetlanguage(replacement)
        unit.rich_target = unit.rich_target
        unit.target = unit.target
        assert json.loads(bytes(store)) == {
            "k": {"description": "keep", "other": "value"}
        }

    @mark.parametrize("attr", ["rich_target", "rich_source"])
    @mark.parametrize("detach", ["copy", "remove"])
    def test_detached_rich_edit_uses_saved_locale(self, attr, detach) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ru")
        store.parse('{"k":{"one":"1","few":"2","many":"5"}}')
        unit = store.units[0]
        store.settargetlanguage("cs")
        if detach == "copy":
            unit = unit.copy()
        else:
            store.removeunit(unit)
        incoming = multistring(["single", "few", "rest"])
        setattr(unit, attr, unit.multistring_to_rich(incoming))
        destination = self.StoreClass()
        destination.settargetlanguage("cs")
        destination.addunit(unit)
        assert json.loads(bytes(destination))["k"] == {
            "one": "single",
            "few": "few",
            "many": "5",
            "other": "rest",
        }

    def test_merge_scalar_before_first_attachment(self) -> None:
        unit = jsonl10n.GoI18NV2JsonUnit(multistring(["singular", "plural"]))
        unit.setid("k")
        unit.notes = "keep"
        unit.merge(jsonl10n.GoI18NV2JsonUnit("new"), overwrite=True)
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.addunit(unit)
        assert json.loads(bytes(store)) == {
            "k": {"description": "keep", "other": "new"}
        }

    def test_build_from_sparse_v1_unit(self) -> None:
        donor = jsonl10n.GoI18NJsonFile.parsestring(
            b'[{"id":"k","translation":{"other":"new"}}]'
        )
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.addunit(store.UnitClass.buildfromunit(donor.units[0]))
        assert json.loads(bytes(store)) == {"k": {"other": "new"}}

    def test_foreign_plural_into_scalar(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse('{"k":"old"}')
        donor = jsonl10n.GoI18NJsonFile.parsestring(
            b'[{"id":"k","translation":{"other":"new"}}]'
        )
        store.units[0].merge(donor.units[0], overwrite=True)
        assert json.loads(bytes(store)) == {"k": {"other": "new"}}

    def test_unbound_native_merge_uses_first_receiving_locale(self) -> None:
        source = self.StoreClass()
        source.settargetlanguage("en")
        source.parse('{"k":{"other":"new"}}')
        unit = source.UnitClass("old", item="k")
        unit.setid("k")
        unit.merge(source.units[0], overwrite=True)
        destination = self.StoreClass()
        destination.settargetlanguage("cs")
        destination.addunit(unit)
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(destination)) == {"k": {"other": "new"}}

    def test_detached_merge_keeps_receiver_locale(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse('{"k":{"one":"old","other":"old"}}')
        unit = store.units[0].copy()
        donor = self.StoreClass.parsestring(b'{"k":{"other":"new"}}')
        unit.merge(donor.units[0], overwrite=True)
        dest = self.StoreClass()
        dest.settargetlanguage("en")
        dest.addunit(unit)
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(dest)) == {"k": {"other": "new"}}

    def test_merge_named_forms(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        message = {"description": "keep", "one": "one", "other": "other"}
        store.parse(json.dumps({"k": message}))
        incoming = self.StoreClass()
        incoming.parse('{"k": {"other": "new"}}')
        donor = incoming.units[0]
        donor.update_plural_forms({"many": "fraction"})
        unit = store.units[0]
        unit.merge(donor)
        assert json.loads(bytes(store)) == {"k": message}
        unit.merge(donor, overwrite=True)
        unit.rich_target = unit.rich_target
        assert json.loads(bytes(store)) == {
            "k": {"description": "keep", "other": "new", "many": "fraction"}
        }

    def test_named_forms(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        forms = {"many": "fraction", "other": ""}
        catalog = {"k": {"description": "keep", **forms}}
        store.parse(json.dumps(catalog))
        unit = store.units[0]
        assert json.loads(bytes(store)) == catalog
        assert unit.plural_forms == forms
        unit.target = unit.target
        assert unit.plural_forms == forms
        assert store.findid(unit.getid()) is unit
        with raises(ValueError, match="4 positional forms"):
            unit.target = multistring(["a", "b", "c", "d"])
        assert json.loads(bytes(store)) == catalog
        unit.update_plural_forms({"one": "one", "other": None})
        assert unit.plural_forms == {"many": "fraction", "one": "one"}
        with raises(ValueError):
            unit.plural_forms = {}
        unit.plural_forms = {"many": "fraction"}
        parsed = self.StoreClass()
        parsed.parse(bytes(store))
        assert parsed.units[0].plural_forms == {"many": "fraction"}
        assert parsed.units[0].getnotes() == "keep"

    def test_plurals_1(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOI18N_V2_SIMPLE)

        assert len(store.units) == 6
        assert store.units[0].target == "value"
        assert store.units[1].target == "Table"
        assert store.units[2].target == multistring(
            ["{{.count}} tag", "{{.count}} tags"]
        )
        assert store.units[3].target == "world"
        assert store.units[4].target == "hello"

        assert bytes(store).decode() == JSON_GOI18N_V2_SIMPLE

    def test_plurals_2(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_GOI18N_V2)

        # Remove plurals
        store.units[1].target = "plural"

        assert bytes(store).decode() == JSON_GOI18N_V2_PLURAL

        # Bring back plurals
        store.units[1].target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
                "the plural form 5",
            ]
        )

        assert bytes(store).decode() == JSON_GOI18N_V2

    def test_plurals_blank(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_GOI18N_V2)
        # Remove one of plurals
        store.units[1].target = multistring(
            [
                "the plural form 0",
                "the plural form 1",
                "the plural form 2",
                "the plural form 3",
                "the plural form 4",
            ]
        )

        expected = json.loads(JSON_GOI18N_V2)
        del expected["plural"]["other"]
        assert json.loads(bytes(store)) == expected

    def test_plurals_missing(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOI18N_V2_SIMPLE)

        assert len(store.units) == 6

        store.units[2].target = multistring(["{{.count}} tag", "{{.count}} tags"])
        assert bytes(store).decode() == JSON_GOI18N_V2_SIMPLE

        store.units[2].target = multistring(["{{.count}} tag"])

        assert json.loads(bytes(store))["tag"]["one"] == "{{.count}} tag"

    def test_preserve_objects(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_GOI18N_V2_COMPLEX)

        assert len(store.units) == 6
        assert store.units[0].target == "value"
        assert store.units[1].target == "Table"
        assert store.units[2].target == multistring(
            ["{{.count}} tag", "{{.count}} tags"]
        )
        assert store.units[3].target == "world"
        assert store.units[4].target == "hello"

        assert bytes(store).decode() == JSON_GOI18N_V2_COMPLEX

    def test_invalid(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(JSON_I18NEXT_PLURAL)

    def test_invalid_translation_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": []}')

    def test_invalid_plural_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"one": []}}')

    def test_dot_keys(self) -> None:
        jsontext = """{
    ".table": "message"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        # Edit target
        store.units[0].target = "message"
        assert bytes(store).decode() == jsontext


class TestARBJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.ARBJsonFile

    def test_roundtrip(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_ARB)

        assert len(store.units) == 4
        assert store.units[0].isheader()
        assert store.units[1].target == "Back"
        assert store.units[2].target == "Next"
        assert store.units[3].target == "Done"

        assert bytes(store).decode() == JSON_ARB.decode()

    def test_leading_dot_keys(self) -> None:
        jsontext = """{
  ".dot": "dot",
  "@.dot": {
    "description": "description of .dot"
  },
  "nav:colon": "colon in a colon",
  "@nav:colon": {
    "description": "description of nav:colon"
  }
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 2
        store.units[1].target = "colon in a colon"
        assert bytes(store).decode() == jsontext

    def test_invalid_nesting(self) -> None:
        jsontext = """{
    "key": {
        ".dot": "dot",
        "@.dot": {}
    }
}
"""
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(jsontext)

    def test_invalid_metadata_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": "value", "@key": "metadata"}')

    def test_invalid_metadata_description_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": "value", "@key": {"description": {}}}')

    def test_empty_metadata_not_stored(self) -> None:
        """Test that empty metadata is not stored in the output."""
        jsontext = """{
  "key1": "value1",
  "@key1": {},
  "key2": "value2",
  "@key2": {
    "type": "text"
  },
  "key3": "value3"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        output = bytes(store).decode()

        assert '"@key1": {}' not in output

        # Non-empty metadata should be preserved
        assert '"@key2"' in output

        assert '"@key3"' not in output


JSON_FORMATJS = """{
    "hak27d": {
        "defaultMessage": "Control Panel",
        "description": "title of control panel section"
    },
    "haqsd": {
        "defaultMessage": "Delete user {name}",
        "description": "delete button"
    },
    "19hjs": {
        "defaultMessage": "New Password",
        "description": "placeholder text"
    },
    "explicit-id": {
        "defaultMessage": "Confirm Password",
        "description": "placeholder text"
    }
}
"""


class TestFormatJSJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.FormatJSJsonFile

    def test_roundtrip(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_FORMATJS)

        assert len(store.units) == 4
        assert store.units[3].getid() == "explicit-id"
        assert store.units[3].target == "Confirm Password"
        assert store.units[3].getnotes() == "placeholder text"

        assert bytes(store).decode() == JSON_FORMATJS

    def test_leading_dot_keys(self) -> None:
        jsontext = """{
    ".dot": {
        "defaultMessage": "Control Panel",
        "description": "title of control panel section"
    }
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert bytes(store).decode() == jsontext

    def test_object_description(self) -> None:
        jsontext = """{
    "key": {
        "defaultMessage": "Greeting",
        "description": {
            "text": "Greeting",
            "context": "home"
        }
    }
}
"""
        store = self.StoreClass()
        store.parse(jsontext)

        assert store.units[0].getnotes() == {"text": "Greeting", "context": "home"}
        assert bytes(store).decode() == jsontext

    def test_invalid(self) -> None:
        jsontext = """{
    ".dot": "text"
}
"""
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(jsontext)

    def test_invalid_default_message_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"defaultMessage": {}}}')

    def test_invalid_description_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": {"defaultMessage": "value", "description": []}}')


JSON_NEXTCLOUD_SIMPLE = b"""{
    "translations": {
        "Hello": "Hallo",
        "Goodbye": "Auf Wiedersehen"
    }
}
"""

JSON_NEXTCLOUD_WITH_NULL = b"""{
    "translations": {
        "Orangutan has %d banana.\\n": null,
        "Goodbye": "Auf Wiedersehen"
    }
}
"""

JSON_NEXTCLOUD_WITH_PLURAL_FORM = rb"""{
    "translations": {
        "Hello": "Hallo",
        "_%n tree_::_%n trees_": [
            "%n Baum",
            "%n B\u00e4ume"
        ]
    },
    "pluralForm": "nplurals=2; plural=(n != 1);"
}
"""

# spellchecker:off
JSON_NEXTCLOUD_COMPLEX = rb"""{
    "translations": {
        "Simple string": "Einfache Zeichenkette",
        "_%n comment_::_%n comments_": [
            "%n Kommentar",
            "%n Kommentare"
        ],
        "Another key": "Ein anderer Wert"
    },
    "pluralForm": "nplurals=2; plural=(n != 1);"
}
"""
# spellchecker:on


class TestNextcloudJsonUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.NextcloudJsonUnit

    def test_source_property_maps_to_id(self) -> None:
        """Test that source property maps to unit ID for NextcloudJsonUnit."""
        unit = self.UnitClass("target value")
        unit.setid("my_key")
        assert unit.source == "my_key"

        # Setting source should update the ID
        unit.source = "new_key"
        assert unit.getid() == "new_key"
        assert unit.source == "new_key"

    def test_source_roundtrip(self) -> None:
        """Test that source property persists through get/set."""
        unit = self.UnitClass("Hello World")
        unit.source = "greeting"
        assert unit.getid() == "greeting"
        assert unit.source == "greeting"


class TestNextcloudJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.NextcloudJsonFile

    def test_parse_simple(self) -> None:
        """Test parsing simple Nextcloud JSON with no plurals."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        assert len(store.units) == 2
        assert store.units[0].getid() == "Hello"
        assert store.units[0].target == "Hallo"
        assert store.units[1].getid() == "Goodbye"
        assert store.units[1].target == "Auf Wiedersehen"

    def test_parse_null_value(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_NULL)

        assert len(store.units) == 2
        assert store.units[0].getid() == "Orangutan has %d banana.\n"
        assert store.units[0].target is None
        assert store.units[1].target == "Auf Wiedersehen"

    def test_serialize_omits_null_value(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_NULL)

        assert json.loads(bytes(store)) == {
            "translations": {"Goodbye": "Auf Wiedersehen"}
        }
        assert len(store.units) == 2
        assert store.units[0].target is None

    @mark.parametrize(
        "target",
        ["", [""], ["", ""]],
    )
    def test_serialize_omits_empty_translation(self, target) -> None:
        data = {
            "translations": {"Empty": target, "Hello": "Hallo"},
            "pluralForm": "nplurals=2; plural=(n != 1);",
            "customField": "customValue",
        }
        store = self.StoreClass()
        store.parse(json.dumps(data))

        result = json.loads(bytes(store))
        assert result == {**data, "translations": {"Hello": "Hallo"}}
        assert len(store.units) == 2

    @mark.parametrize("target", [["%n Baum", ""], ["", "%n Bäume"]])
    def test_serialize_preserves_partial_plural(self, target) -> None:
        data = {"translations": {"_%n tree_::_%n trees_": target}}
        store = self.StoreClass()
        store.parse(json.dumps(data))

        assert json.loads(bytes(store)) == data

    def test_serialize_new_and_cleared_translations(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_PLURAL_FORM)
        unit = self.StoreClass.UnitClass()
        unit.source = "New key"
        unit.target = ""
        store.addunit(unit)

        assert len(json.loads(bytes(store))["translations"]) == 2
        store.units[0].target = ""
        store.units[1].target = multistring(["", ""])

        assert json.loads(bytes(store)) == {
            "translations": {},
            "pluralForm": "nplurals=2; plural=(n != 1);",
        }
        assert len(store.units) == 3

    def test_serialize_simple(self) -> None:
        """Test serializing simple translations."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue()

        assert b'"translations"' in result
        assert b'"Hello": "Hallo"' in result
        assert b'"Goodbye": "Auf Wiedersehen"' in result

    def test_parse_with_plurals(self) -> None:
        """Test parsing Nextcloud JSON with plural forms."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_PLURAL_FORM)

        assert len(store.units) == 2

        # First unit should be simple string
        assert store.units[0].getid() == "Hello"
        assert store.units[0].target == "Hallo"
        assert not isinstance(store.units[0].target, multistring)

        # Second unit should be plural
        assert store.units[1].getid() == "_%n tree_::_%n trees_"
        assert isinstance(store.units[1].target, multistring)
        assert len(store.units[1].target.strings) == 2
        assert store.units[1].target.strings[0] == "%n Baum"
        assert store.units[1].target.strings[1] == "%n Bäume"

    def test_preserve_plural_form(self) -> None:
        """Test that pluralForm metadata is preserved during round-trip."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_PLURAL_FORM)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue().decode()

        # Verify pluralForm is preserved
        assert '"pluralForm": "nplurals=2; plural=(n != 1);"' in result
        assert '"translations"' in result

    def test_roundtrip_with_plurals(self) -> None:
        """Test full round-trip with plurals and metadata."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_COMPLEX)

        assert len(store.units) == 3

        # Verify parsing
        assert store.units[0].target == "Einfache Zeichenkette"
        assert isinstance(store.units[1].target, multistring)
        assert store.units[2].target == "Ein anderer Wert"  # codespell:ignore

        # Serialize and re-parse
        out = BytesIO()
        store.serialize(out)

        store2 = self.StoreClass()
        store2.parse(out.getvalue())

        assert len(store2.units) == 3
        assert store2.units[0].target == "Einfache Zeichenkette"
        assert isinstance(store2.units[1].target, multistring)
        assert len(store2.units[1].target.strings) == 2
        assert store2.units[2].target == "Ein anderer Wert"  # codespell:ignore

    def test_ignore_non_translations_keys(self) -> None:
        """Test that only 'translations' key is parsed for units."""
        json_with_extra = b"""{
    "someOtherKey": "should be ignored",
    "translations": {
        "Hello": "Hallo"
    },
    "pluralForm": "nplurals=2; plural=(n != 1);"
}
"""
        store = self.StoreClass()
        store.parse(json_with_extra)

        # Should only have 1 unit from translations
        assert len(store.units) == 1
        assert store.units[0].getid() == "Hello"

    def test_preserve_other_metadata(self) -> None:
        """Test that arbitrary metadata outside translations is preserved."""
        json_with_metadata = b"""{
    "translations": {
        "Hello": "Hallo"
    },
    "pluralForm": "nplurals=2; plural=(n != 1);",
    "customField": "customValue"
}
"""
        store = self.StoreClass()
        store.parse(json_with_metadata)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue().decode()

        # Verify all metadata is preserved
        assert '"pluralForm": "nplurals=2; plural=(n != 1);"' in result
        assert '"customField": "customValue"' in result
        assert '"translations"' in result

    def test_add_unit(self) -> None:
        """Test adding a new unit to Nextcloud JSON."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        # Add a new simple unit
        unit = self.StoreClass.UnitClass("Neuer Wert")
        unit.setid("New Key")
        store.addunit(unit)

        assert len(store.units) == 3
        assert store.units[2].getid() == "New Key"
        assert store.units[2].target == "Neuer Wert"

    def test_add_plural_unit(self) -> None:
        """Test adding a plural unit to Nextcloud JSON."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        # Add a plural unit
        unit = self.StoreClass.UnitClass(multistring(["%n Datei", "%n Dateien"]))
        unit.setid("_%n file_::_%n files_")
        store.addunit(unit)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue().decode()

        # Verify plural is serialized as array
        assert (
            '"_%n file_::_%n files_": [\n            "%n Datei",\n            "%n Dateien"\n        ]'
            in result
        )

    def test_empty_translations(self) -> None:
        """Test handling of empty translations object."""
        json_empty = b"""{
    "translations": {},
    "pluralForm": "nplurals=2; plural=(n != 1);"
}
"""
        store = self.StoreClass()
        store.parse(json_empty)

        assert len(store.units) == 0

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue().decode()

        assert '"translations": {}' in result
        assert '"pluralForm"' in result

    def test_invalid_translations_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"translations": []}')

    def test_invalid_translation_value(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"translations": {"key": {}}}')


JSON_RESJSON = b"""{
    "greeting": "Hello",
    "_greeting.comment": "A welcome greeting.",
    "_greeting.source": "Hello",
    "farewell": "Goodbye",
    "_farewell.comment": "A parting message.",
    "_farewell.source": "Goodbye"
}
"""


class TestRESJSONFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.RESJSONFile

    def test_roundtrip(self) -> None:
        store = self.StoreClass()
        store.parse(JSON_RESJSON)

        assert len(store.units) == 2
        assert store.units[0].target == "Hello"
        assert store.units[0].getnotes() == "A welcome greeting."
        assert store.units[0].metadata.get("source") == "Hello"
        assert store.units[1].target == "Goodbye"
        assert store.units[1].getnotes() == "A parting message."
        assert store.units[1].metadata.get("source") == "Goodbye"

        assert bytes(store).decode() == JSON_RESJSON.decode()

    def test_basic_parsing(self) -> None:
        jsontext = """{
    "key": "value",
    "_key.comment": "A comment"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].target == "value"
        assert store.units[0].getnotes() == "A comment"
        assert bytes(store).decode() == jsontext

    def test_multiple_metadata(self) -> None:
        jsontext = """{
    "message": "text",
    "_message.comment": "comment text",
    "_message.source": "source text",
    "_message.custom": "custom data"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].target == "text"
        assert store.units[0].getnotes() == "comment text"
        assert store.units[0].metadata.get("source") == "source text"
        assert store.units[0].metadata.get("custom") == "custom data"
        assert bytes(store).decode() == jsontext

    def test_no_metadata(self) -> None:
        jsontext = """{
    "simple": "value"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].target == "value"
        assert store.units[0].getnotes() == ""
        assert bytes(store).decode() == jsontext

    def test_edit_target(self) -> None:
        jsontext = """{
    "key": "value",
    "_key.comment": "comment"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        store.units[0].target = "new value"
        result = bytes(store).decode()
        assert '"key": "new value"' in result
        assert '"_key.comment": "comment"' in result

    def test_edit_notes(self) -> None:
        jsontext = """{
    "key": "value",
    "_key.comment": "original comment",
    "_key.source": "source text"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        store.units[0].notes = "modified comment"
        result = bytes(store).decode()
        assert '"key": "value"' in result
        assert '"_key.comment": "modified comment"' in result
        assert '"_key.source": "source text"' in result

    def test_keys_with_dots(self) -> None:
        jsontext = """{
    "foo.bar": "value",
    "_foo.bar.comment": "comment for foo.bar"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo.bar"
        assert store.units[0].target == "value"
        assert store.units[0].getnotes() == "comment for foo.bar"
        assert bytes(store).decode() == jsontext

    def test_leading_dot_keys(self) -> None:
        jsontext = """{
    ".dot": "dot value",
    "_.dot.comment": "comment"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].target == "dot value"
        assert bytes(store).decode() == jsontext

    def test_invalid_nesting(self) -> None:
        jsontext = """{
    "key": {
        "nested": "value"
    }
}
"""
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(jsontext)

    def test_invalid_top_level_type(self) -> None:
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse("[]")

    def test_source_property_get_set(self) -> None:
        """Test that source property can be read and written correctly."""
        jsontext = """{
    "key": "value",
    "_key.source": "original source"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].source == "original source"
        assert store.units[0].target == "value"

        # Modify source
        store.units[0].source = "modified source"
        result = bytes(store).decode()
        assert '"_key.source": "modified source"' in result

    def test_source_property_persists(self) -> None:
        """Test that source property persists through serialization."""
        store = self.StoreClass()
        unit = store.UnitClass("")
        unit.setid("mykey")
        unit.target = "target value"
        unit.source = "source value"
        store.addunit(unit)

        result = bytes(store).decode()
        assert '"mykey": "target value"' in result
        assert '"_mykey.source": "source value"' in result

        # Parse again to verify persistence
        store2 = self.StoreClass()
        store2.parse(result)
        assert len(store2.units) == 1
        assert store2.units[0].source == "source value"
        assert store2.units[0].target == "target value"

    def test_getcontext_returns_id(self) -> None:
        """Test that getcontext() returns the unit ID."""
        jsontext = """{
    "greeting": "Hello",
    "_greeting.comment": "A greeting"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].getcontext() == "greeting"

    def test_parsing_preserves_order(self) -> None:
        """Test that parsing preserves the order of keys."""
        jsontext = """{
    "first": "1",
    "_first.source": "one",
    "second": "2",
    "_second.source": "two",
    "third": "3",
    "_third.source": "three"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 3
        assert store.units[0].getid() == "first"
        assert store.units[1].getid() == "second"
        assert store.units[2].getid() == "third"

    def test_metadata_without_translation(self) -> None:
        """Test handling when metadata exists but no corresponding translation value."""
        jsontext = """{
    "key": "value",
    "_key.source": "source text",
    "_orphan.comment": "orphan metadata"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        # Should handle orphan metadata gracefully
        # The parsing code extracts "orphan" as the base key from "_orphan.comment"
        assert len(store.units) == 2
        # First unit should be the normal key with metadata
        assert store.units[0].getid() == "key"
        assert store.units[0].source == "source text"
        # Second unit should extract the base key from the orphan metadata
        assert store.units[1].getid() == "orphan"
        assert store.units[1].metadata.get("comment") == "orphan metadata"

    def test_complex_keys_with_multiple_dots(self) -> None:
        """Test handling of keys with multiple dots."""
        jsontext = """{
    "app.section.key": "value",
    "_app.section.key.source": "source",
    "_app.section.key.comment": "comment"
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].getid() == "app.section.key"
        assert store.units[0].target == "value"
        assert store.units[0].source == "source"
        assert store.units[0].getnotes() == "comment"

    def test_source_empty_string(self) -> None:
        """Test that empty source strings are handled correctly."""
        jsontext = """{
    "key": "value",
    "_key.source": ""
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 1
        assert store.units[0].source == ""
        assert store.units[0].target == "value"
