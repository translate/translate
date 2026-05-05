from io import BytesIO, StringIO

from pytest import importorskip, raises

from translate.misc.multistring import multistring
from translate.storage import base, pypo

fpo = importorskip("translate.storage.fpo", exc_type=ImportError)


class TestFPOFile:
    StoreClass = fpo.pofile

    def poparse(self, posource):
        """Helper that parses po source without requiring files."""
        dummyfile = BytesIO(
            posource.encode() if isinstance(posource, str) else posource
        )
        return self.StoreClass(dummyfile, noheader=True)

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

    def test_buildfromunit_preserves_previous_metadata(self) -> None:
        """FPO units should retain previous metadata copied from another PO unit."""
        source_unit = pypo.pounit("new file")
        source_unit.target = "fichier"
        source_unit.setcontext("new context")
        source_unit.prev_source = "old file"
        source_unit.prev_context = "old context"
        source_unit.markfuzzy()

        unit = fpo.pounit.buildfromunit(source_unit)

        assert unit.prev_source == "old file"
        assert unit.prev_context == "old context"
        assert str(unit) == (
            "#, fuzzy\n"
            '#| msgctxt "old context"\n'
            '#| msgid "old file"\n'
            'msgctxt "new context"\n'
            'msgid "new file"\n'
            'msgstr "fichier"\n'
        )

    def test_previous_plural_metadata(self) -> None:
        """Checks FPO parsing, API access and serialization of previous entries."""
        posource = r"""#, fuzzy
#| msgctxt "old context"
#| msgid "old file"
#| msgid_plural "old files"
msgctxt "new context"
msgid "new file"
msgid_plural "new files"
msgstr[0] "fichier"
msgstr[1] "fichiers"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.prev_context == "old context"
        assert isinstance(unit.prev_source, multistring)
        assert [str(string) for string in unit.prev_source.strings] == [
            "old file",
            "old files",
        ]
        alternatives = unit.getalttrans()
        assert len(alternatives) == 1
        assert unit.getalttrans(origin="tm") == []
        assert [str(string) for string in alternatives[0].source.strings] == [
            "old file",
            "old files",
        ]
        assert [str(string) for string in alternatives[0].target.strings] == [
            "fichier",
            "fichiers",
        ]
        assert bytes(pofile).decode("utf-8") == posource

    def test_merge_sets_previous_metadata(self) -> None:
        """Checks FPO merging records the reused message as previous."""
        current = self.poparse('msgid "new file"\nmsgstr ""\n').units[0]
        previous = self.poparse('msgid "old file"\nmsgstr "fichier"\n').units[0]

        current.merge(previous, authoritative=True)

        assert current.prev_source == "old file"
        assert current.prev_context == ""
        assert str(current) == (
            '#, fuzzy\n#| msgid "old file"\nmsgid "new file"\nmsgstr "fichier"\n'
        )

    def test_msgidcomment_not_used_as_previous_context(self) -> None:
        """KDE-style msgid comments should not become previous msgctxt."""
        current = self.poparse('msgid "new file"\nmsgstr ""\n').units[0]
        previous = self.poparse('msgid "old file"\nmsgstr "fichier"\n').units[0]
        previous.msgidcomment = "certs.label"

        current.merge(previous, authoritative=True)

        assert current.prev_source == "old file"
        assert current.prev_context == ""
        assert "#| msgctxt" not in str(current)
