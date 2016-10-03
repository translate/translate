# -*- coding: utf-8 -*-

import sys
from io import BytesIO
from translate.storage import jsonl10n, test_monolingual


class TestJSONResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.JsonUnit


class TestJSONResourceStore(test_monolingual.TestMonolingualUnit):
    StoreClass = jsonl10n.JsonFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('{"key": "value"}')
        out = BytesIO()
        src = store.serialize(out)

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
