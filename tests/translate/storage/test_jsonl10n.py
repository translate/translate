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

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": "value"}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": "value"\n}\n'

    def test_can_not_detect(self):
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(
                b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00b\xee\x9dh^\x01\x00\x00\x90\x04\x00\x00\x13\x00\x08\x02"
            )

    def test_error(self):
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse('{"key": "value"')

    def test_filter(self):
        store = self.StoreClass(filter=["key"])
        store.parse('{"key": "value", "other": "second"}')
        assert len(store.units) == 1
        assert store.units[0].source == "value"

    def test_ordering(self):
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

    def test_args(self):
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

    def test_bom(self):
        content = "{}\n".encode("utf-8-sig")
        store = self.StoreClass()
        store.parse(content)
        assert len(store.units) == 0
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == content

    def test_complex(self):
        store = self.StoreClass()
        store.parse(JSON_COMPLEX)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_COMPLEX

    def test_complex_array(self):
        store = self.StoreClass()
        store.parse(JSON_COMPLEX_ARRAY)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_COMPLEX_ARRAY

    def test_add(self):
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

    def test_add_list_like(self):
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

    def test_add_blank(self):
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

    def test_types(self):
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

    def test_null(self):
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

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": {"second": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue() == b'{\n    "key": {\n        "second": "value"\n    }\n}\n'
        )

    def test_ordering(self):
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

    def test_array(self):
        store = self.StoreClass()
        store.parse(JSON_ARRAY)

        assert store.units[0].source == "One"
        assert store.units[0].getid() == ".key[0]"
        assert store.units[1].getid() == ".key[1]"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_ARRAY

    def test_add(self):
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

    def test_add_index(self):
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

    def test_add_index_nested(self):
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

    def test_nested_list_mixed(self):
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

    def test_list_to_dict(self):
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

    def test_complex_keys(self):
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

    def test_add_other(self):
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
    def test_from_string(self, id_string, expected):
        id_class = self.StoreClass.UnitClass.IdClass
        from_string = id_class.from_string
        assert from_string(id_string) == id_class(expected)

    def test_dot_keys(self):
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

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key": {\n        "message": "value",\n        "description": "note"\n    }\n}\n'
        )

    def test_dot_keys(self):
        store = self.StoreClass()
        store.parse('{"key.dot": {"message": "value", "description": "note"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key.dot": {\n        "message": "value",\n        "description": "note"\n    }\n}\n'
        )

    def test_leading_dot_keys(self):
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

    def test_serialize_no_description(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue() == b'{\n    "key": {\n        "message": "value"\n    }\n}\n'
        )

    def test_set_target(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        store.units[0].target = "another"
        out = BytesIO()
        store.serialize(out)

        assert (
            out.getvalue()
            == b'{\n    "key": {\n        "message": "another",\n        "description": "note"\n    }\n}\n'
        )

    def test_placeholders(self):
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

    def test_comments(self):
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


class TestI18NextStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.I18NextFile

    def test_serialize(self):
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_I18NEXT)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == JSON_I18NEXT

    def test_units(self):
        store = self.StoreClass()
        store.settargetlanguage("ar")
        store.parse(JSON_I18NEXT)
        assert len(store.units) == 4

    def test_plurals(self):
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

    def test_nested_array(self):
        store = self.StoreClass()
        store.parse(JSON_I18NEXT_NESTED_ARRAY)

        assert len(store.units) == 4
        assert store.units[0].getid() == ".apps[0].title"
        assert store.units[1].getid() == ".apps[0].description"
        assert store.units[2].getid() == ".apps[1].title"
        assert store.units[3].getid() == ".apps[1].description"

        assert bytes(store).decode() == JSON_I18NEXT_NESTED_ARRAY

    def test_new_plural(self):
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

    def test_new_plural_id(self):
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

    def test_plurals(self):
        store = self.StoreClass()
        store.parse(JSON_GOTEXT)

        assert len(store.units) == 2
        assert store.units[0].target == multistring(["{N} tag", "{N} tags"])
        assert store.units[1].target == "Table"

        assert bytes(store).decode() == JSON_GOTEXT.decode()

    def test_plurals_missing(self):
        store = self.StoreClass()
        store.parse(JSON_GOTEXT)

        store.units[0].target = multistring(["{N} tag"])

        assert (
            '"other": {\n                            "msg": ""' in bytes(store).decode()
        )

    def test_case_no_msg(self):
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
                        "one": {
                            "msg": "One file remaining!"
                        },
                        "other": {
                            "msg": "There are {N} more files remaining!"
                        }
                    }
                }
            }
        }
    ]
}
"""
        )

    def test_complex_id(self):
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


class TestI18NextV4Store(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.I18NextV4File
    DeepUnpluralizedJson = JSON_I18NEXT_PLURAL
    PartiallyPluralizedJson = JSON_I18NEXT_V4
    CorrectlyPluralizedJson = JSON_I18NEXT_V4_FIXED

    def test_serialize(self):
        store = self.StoreClass()
        store.targetlanguage = "ar"
        store.parse(JSON_I18NEXT_V4)
        out = BytesIO()
        store.serialize(out)

        # This will add missing plurals
        assert out.getvalue().decode() == JSON_I18NEXT_V4_FIXED

    def test_units(self):
        store = self.StoreClass()
        store.targetlanguage = "ar"
        store.parse(self.PartiallyPluralizedJson)
        assert len(store.units) == 4

    def test_plurals(self):
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
                "the plural form 6",
            ]
        )
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue().decode() == self.CorrectlyPluralizedJson

    def test_nested_array(self):
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

    def test_new_plural(self):
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

    def test_ru(self):
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

    def test_plurals(self):
        store = self.StoreClass()
        store.parse(JSON_GOI18N)

        assert len(store.units) == 2
        assert store.units[0].target == multistring(
            ["{{.count}} tag", "{{.count}} tags"]
        )
        assert store.units[1].target == "Table"

        assert bytes(store).decode() == JSON_GOI18N.decode()

    def test_plurals_missing(self):
        store = self.StoreClass()
        store.parse(JSON_GOI18N)

        store.units[0].target = multistring(["{{.count}} tag"])

        assert '"other": ""' in bytes(store).decode()

    def test_invalid(self):
        store = self.StoreClass()
        with raises(ValueError):
            store.parse(JSON_I18NEXT_PLURAL)

    def test_dot_keys(self):
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

    def test_plurals_1(self):
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

    def test_plurals_2(self):
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

    def test_plurals_blank(self):
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

        assert bytes(store).decode() == JSON_GOI18N_V2.replace("the plural form 5", "")

    def test_plurals_missing(self):
        store = self.StoreClass()
        store.parse(JSON_GOI18N_V2_SIMPLE)

        assert len(store.units) == 6

        store.units[2].target = multistring(["{{.count}} tag", "{{.count}} tags"])
        assert bytes(store).decode() == JSON_GOI18N_V2_SIMPLE

        store.units[2].target = multistring(["{{.count}} tag"])

        assert '"other": "{{.count}} tag"' in bytes(store).decode()

    def test_simplification(self):
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

        assert bytes(store).decode() == JSON_GOI18N_V2_SIMPLE

    def test_invalid(self):
        store = self.StoreClass()
        with raises(ValueError):
            store.parse(JSON_I18NEXT_PLURAL)

    def test_dot_keys(self):
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

    def test_roundtrip(self):
        store = self.StoreClass()
        store.parse(JSON_ARB)

        assert len(store.units) == 4
        assert store.units[0].isheader()
        assert store.units[1].target == "Back"
        assert store.units[2].target == "Next"
        assert store.units[3].target == "Done"

        assert bytes(store).decode() == JSON_ARB.decode()

    def test_leading_dot_keys(self):
        jsontext = """{
  ".dot": "dot",
  "@.dot": {},
  "nav:colon": "colon in a colon",
  "@nav:colon": {}
}
"""
        store = self.StoreClass()
        store.parse(jsontext)
        assert len(store.units) == 2
        store.units[1].target = "colon in a colon"
        assert bytes(store).decode() == jsontext

    def test_invalid_nesting(self):
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

    def test_roundtrip(self):
        store = self.StoreClass()
        store.parse(JSON_FORMATJS)

        assert len(store.units) == 4
        assert store.units[3].getid() == "explicit-id"
        assert store.units[3].target == "Confirm Password"
        assert store.units[3].getnotes() == "placeholder text"

        assert bytes(store).decode() == JSON_FORMATJS

    def test_leading_dot_keys(self):
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

    def test_invalid(self):
        jsontext = """{
    ".dot": "text"
}
"""
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(jsontext)


JSON_NEXTCLOUD_SIMPLE = b"""{
    "translations": {
        "Hello": "Hallo",
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

    def test_source_property_maps_to_id(self):
        """Test that source property maps to unit ID for NextcloudJsonUnit."""
        unit = self.UnitClass("target value")
        unit.setid("my_key")
        assert unit.source == "my_key"

        # Setting source should update the ID
        unit.source = "new_key"
        assert unit.getid() == "new_key"
        assert unit.source == "new_key"

    def test_source_roundtrip(self):
        """Test that source property persists through get/set."""
        unit = self.UnitClass("Hello World")
        unit.source = "greeting"
        assert unit.getid() == "greeting"
        assert unit.source == "greeting"


class TestNextcloudJsonFile(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.NextcloudJsonFile

    def test_parse_simple(self):
        """Test parsing simple Nextcloud JSON with no plurals."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        assert len(store.units) == 2
        assert store.units[0].getid() == "Hello"
        assert store.units[0].target == "Hallo"
        assert store.units[1].getid() == "Goodbye"
        assert store.units[1].target == "Auf Wiedersehen"

    def test_serialize_simple(self):
        """Test serializing simple translations."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_SIMPLE)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue()

        assert b'"translations"' in result
        assert b'"Hello": "Hallo"' in result
        assert b'"Goodbye": "Auf Wiedersehen"' in result

    def test_parse_with_plurals(self):
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

    def test_preserve_plural_form(self):
        """Test that pluralForm metadata is preserved during round-trip."""
        store = self.StoreClass()
        store.parse(JSON_NEXTCLOUD_WITH_PLURAL_FORM)

        out = BytesIO()
        store.serialize(out)
        result = out.getvalue().decode()

        # Verify pluralForm is preserved
        assert '"pluralForm": "nplurals=2; plural=(n != 1);"' in result
        assert '"translations"' in result

    def test_roundtrip_with_plurals(self):
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

    def test_ignore_non_translations_keys(self):
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

    def test_preserve_other_metadata(self):
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

    def test_add_unit(self):
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

    def test_add_plural_unit(self):
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

    def test_empty_translations(self):
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

    def test_roundtrip(self):
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

    def test_basic_parsing(self):
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

    def test_multiple_metadata(self):
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

    def test_no_metadata(self):
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

    def test_edit_target(self):
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

    def test_edit_notes(self):
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

    def test_keys_with_dots(self):
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

    def test_leading_dot_keys(self):
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

    def test_invalid_nesting(self):
        jsontext = """{
    "key": {
        "nested": "value"
    }
}
"""
        store = self.StoreClass()
        with raises(base.ParseError):
            store.parse(jsontext)

    def test_source_property_get_set(self):
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

    def test_source_property_persists(self):
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

    def test_getcontext_returns_id(self):
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

    def test_parsing_preserves_order(self):
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

    def test_metadata_without_translation(self):
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

    def test_complex_keys_with_multiple_dots(self):
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

    def test_source_empty_string(self):
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
