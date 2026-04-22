from io import BytesIO, StringIO
from pathlib import Path

from translate.storage import ini

from . import test_monolingual


class TestINIUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = ini.iniunit


class TestINIStore(test_monolingual.TestMonolingualStore):
    StoreClass = ini.inifile

    def test_serialize(self) -> None:
        content = b"[default]\nkey=None"
        store = self.StoreClass()
        store.parse(content)
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == content

    def test_rem(self) -> None:
        content = b"[default]\nremaining=None"
        store = self.StoreClass()
        store.parse(content)
        assert len(store.units) == 1
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == content

    def test_modified_entry_preserves_crlf_from_bytes(self) -> None:
        content = b"[default]\r\n; comment\r\nkey=value\r\nother=keep\r\n"
        store = self.StoreClass()
        store.parse(content)
        store.units[0].target = "changed"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == (
            b"[default]\r\n; comment\r\nkey=changed\r\nother=keep\r\n"
        )

    def test_modified_entry_preserves_crlf_from_file(self, tmp_path: Path) -> None:
        content = b"[default]\r\n; comment\r\nkey=value\r\nother=keep\r\n"
        input_file = tmp_path / "crlf.ini"
        input_file.write_bytes(content)

        store = self.StoreClass(str(input_file))
        store.units[0].target = "changed"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == (
            b"[default]\r\n; comment\r\nkey=changed\r\nother=keep\r\n"
        )

    def test_text_stream_input_is_parsed_as_content(self) -> None:
        store = self.StoreClass()
        store.parse(StringIO("[default]\nkey=value\n"))

        assert len(store.units) == 1
        assert store.units[0].source == "value"

    def test_new_entry_preserves_crlf(self) -> None:
        content = b"[default]\r\n; comment\r\nkey=value\r\n"
        store = self.StoreClass()
        store.parse(content)
        unit = ini.iniunit("new")
        unit.addlocation("[default]newkey")
        store.addunit(unit)

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == (
            b"[default]\r\n; comment\r\nkey=value\r\nnewkey = new\r\n"
        )

    def test_modified_entry_preserves_lf(self) -> None:
        content = b"[default]\n; comment\nkey=value\nother=keep\n"
        store = self.StoreClass()
        store.parse(content)
        store.units[0].target = "changed"

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b"[default]\n; comment\nkey=changed\nother=keep\n"
