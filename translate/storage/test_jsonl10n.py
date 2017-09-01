# -*- coding: utf-8 -*-

from io import BytesIO
from translate.misc.multistring import multistring
from translate.storage import jsonl10n, test_monolingual


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


class TestJSONResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.JsonUnit


class TestJSONResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.JsonFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": "value"}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": "value"\n}\n'

    def test_ordering(self):
        store = self.StoreClass()
        store.parse('''{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz"
}''')

        assert store.units[0].source == 'foo'
        assert store.units[2].source == 'baz'


class TestJSONNestedResourceStore(test_monolingual.TestMonolingualUnit):
    StoreClass = jsonl10n.JsonNestedFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": {"second": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": {\n        "second": "value"\n    }\n}\n'

    def test_ordering(self):
        store = self.StoreClass()
        store.parse('''{
    "foo": "foo",
    "bar": {
        "baz": "baz"
}}''')

        assert store.units[0].source == 'foo'
        assert store.units[1].getid() == '.bar.baz'


class TestWebExtensionUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.WebExtensionJsonUnit


class TestWebExtensionStore(test_monolingual.TestMonolingualStore):
    StoreClass = jsonl10n.WebExtensionJsonFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": {\n        "message": "value",\n        "description": "note"\n    }\n}\n'

    def test_serialize_no_description(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value"}}')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": {\n        "message": "value"\n    }\n}\n'

    def test_set_target(self):
        store = self.StoreClass()
        store.parse('{"key": {"message": "value", "description": "note"}}')
        store.units[0].settarget('another')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'{\n    "key": {\n        "message": "another",\n        "description": "note"\n    }\n}\n'


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
        store.units[2].target = 'Ahoj'
        store.units[3].target = 'Nazdar'
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_I18NEXT_PLURAL

        # Bring back plurals
        store.units[2].target = multistring([
            "the singular",
            "the plural",
        ])
        store.units[3].target = multistring([
            "the plural form 0",
            "the plural form 1",
            "the plural form 2",
            "the plural form 3",
            "the plural form 4",
            "the plural form 5"
        ])
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == JSON_I18NEXT
