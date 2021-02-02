from io import BytesIO

from pytest import raises

from translate.misc.multistring import multistring
from translate.storage import base, jsonl10n, test_monolingual


JSON_I18NEXT = b"""{
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
JSON_I18NEXT_PLURAL = b"""{
    "key": "value",
    "keyDeep": {
        "inner": "value"
    },
    "keyPluralSimple": "Ahoj",
    "keyPluralMultipleEgArabic": "Nazdar"
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

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == data

    def test_array(self):
        store = self.StoreClass()
        store.parse(JSON_ARRAY)

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


class TestI18NextStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.I18NextFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse(JSON_I18NEXT)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_I18NEXT

    def test_units(self):
        store = self.StoreClass()
        store.parse(JSON_I18NEXT)
        assert len(store.units) == 4

    def test_plurals(self):
        store = self.StoreClass()
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

        assert out.getvalue() == JSON_I18NEXT

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
        EXPECTED = b"""{
    "simple": "the singular",
    "simple_plural": "the plural",
    "complex_0": "the plural form 0",
    "complex_1": "the plural form 1",
    "complex_2": "the plural form 2",
    "complex_3": "the plural form 3",
    "complex_4": "the plural form 4",
    "complex_5": "the plural form 5"
}
"""
        store = self.StoreClass()

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
                    "the plural form 0",
                    "the plural form 1",
                    "the plural form 2",
                    "the plural form 3",
                    "the plural form 4",
                    "the plural form 5",
                ]
            ),
            "complex",
        )
        store.addunit(unit)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == EXPECTED


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
