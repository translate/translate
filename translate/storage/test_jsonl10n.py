# -*- coding: utf-8 -*-

from io import BytesIO
from translate.storage import jsonl10n, test_monolingual


class TestJSONResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = jsonl10n.JsonUnit


class TestJSONResourceStore(test_monolingual.TestMonolingualUnit):
    StoreClass = jsonl10n.JsonFile

    def test_serialize(self):
        store = jsonl10n.JsonFile()
        store.parse('{"key": "value"}')
        out = BytesIO()
        src = store.serialize(out)

        assert out.getvalue() == b'{\n    "key": "value"\n}\n'
