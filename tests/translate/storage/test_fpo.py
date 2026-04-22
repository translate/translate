from io import BytesIO, StringIO

from pytest import importorskip, raises

from translate.storage import base

fpo = importorskip("translate.storage.fpo", exc_type=ImportError)


class TestFPOFile:
    StoreClass = fpo.pofile

    def test_bytesio_path_content_is_not_reopened(self, tmp_path) -> None:
        po_path = tmp_path / "payload.po"
        po_path.write_text(
            'msgid "secret"\nmsgstr "classified"\n',
            encoding="utf-8",
        )

        with raises(base.ParseError):
            self.StoreClass(BytesIO(str(po_path).encode("utf-8")))

    def test_text_stream_is_treated_as_content(self) -> None:
        with raises(base.ParseError):
            self.StoreClass(StringIO('msgid "secret"\nmsgstr "classified"\n'))

    def test_text_stream_uses_declared_header_charset(self) -> None:
        with raises(base.ParseError):
            self.StoreClass(
                StringIO(
                    'msgid ""\n'
                    'msgstr ""\n'
                    '"Content-Type: text/plain; charset=ISO-8859-1\\n"\n'
                    "\n"
                    'msgid "drink"\n'
                    'msgstr "café"\n'
                )
            )
