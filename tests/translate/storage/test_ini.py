from io import BytesIO

from translate.storage import ini, test_monolingual


class TestINIUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = ini.iniunit


class TestINIStore(test_monolingual.TestMonolingualStore):
    StoreClass = ini.inifile

    def test_serialize(self):
        content = b"[default]\nkey=None"
        store = self.StoreClass()
        store.parse(content)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == content
