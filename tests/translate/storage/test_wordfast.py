import time
from codecs import BOM_UTF16_LE
from io import BytesIO

from translate.storage import wordfast as wf

from . import test_base


class TestWFTime:
    def test_timestring(self) -> None:
        """Setting and getting times set using a timestring."""
        wftime = wf.WordfastTime()
        assert wftime.timestring is None
        wftime.timestring = "19710820~050000"
        assert wftime.time[:6] == (1971, 8, 20, 5, 0, 0)

    def test_time(self) -> None:
        """Setting and getting times set using time tuple."""
        wftime = wf.WordfastTime()
        assert wftime.time is None
        wftime.time = time.strptime("19990327~000000", wf.WF_TIMEFORMAT)
        wftime.timestring = "19990327~000000"


class TestWFHeader:
    def test_language_setting(self) -> None:
        """Wordfast language codes use uppercase and -01 for no variant."""
        header = wf.WordfastHeader()
        header.sourcelang = "en"
        header.targetlang = "af_ZA"
        assert header.header["src-lang"] == "%EN-01"
        assert header.header["target-lang"] == "%AF-ZA"
        assert header.sourcelang == "en"
        assert header.targetlang == "af-za"

    def test_unknown_language_setting(self) -> None:
        """Do not truncate language codes outside the legacy five-character form."""
        header = wf.WordfastHeader()
        header.sourcelang = "sr_Latn"
        header.targetlang = "ast"
        assert header.header["src-lang"] == "%SR-LATN"
        assert header.header["target-lang"] == "%AST"


class TestWFUnit(test_base.TestTranslationUnit):
    UnitClass = wf.WordfastUnit

    def normalize_unit_metadata(self, *units) -> None:
        """Normalize timestamps to avoid flaky test failures on slow systems."""
        # Wordfast units have timestamps in metadata that are updated on source/target
        # assignment. On slow systems, units created milliseconds apart have different
        # timestamps, causing equality comparisons to fail.
        FIXED_DATE = "20200101~120000"
        for unit in units:
            unit.metadata["date"] = FIXED_DATE

    def test_difficult_escapes(self) -> None:
        r"""
        Wordfast files need to perform magic with escapes.

        Wordfast does not accept line breaks in its TM (even though they would
        be valid in CSV) thus we turn \\n into \n and reimplement the base
        class test but eliminate a few of the actual tests.
        """
        unit = self.unit
        specials = ['\\"', "\\ ", "\\\n", "\\\t", "\\\\r", '\\\\"']
        for special in specials:
            unit.source = special
            print("unit.source:", f"{unit.source!r}|")
            print("special:", f"{special!r}|")
            assert unit.source == special

    def test_wordfast_escaping(self) -> None:
        """Check handling of &'NN; style escaping."""

        def compare(real, escaped) -> None:
            unit = self.UnitClass(real)
            print(real.encode("utf-8"), unit.source.encode("utf-8"))
            assert unit.source == real
            assert unit.metadata["source"] == escaped
            unit.target = real
            assert unit.target == real
            assert unit.metadata["target"] == escaped

        for escaped, real in wf.WF_ESCAPE_MAP[
            :16
        ]:  # Only common and Windows, not testing Mac
            compare(real, escaped)
        # Real world cases
        unit = self.UnitClass("Open &File. ’n Probleem.")  # codespell:ignore
        assert (
            unit.metadata["source"]
            == "Open &'26;File. &'92;n Probleem."  # codespell:ignore
        )

    def test_newlines(self) -> None:
        """Wordfast does not like real newlines."""
        unit = self.UnitClass("One\nTwo")
        assert unit.metadata["source"] == "One\\nTwo"

    def test_language_setting(self) -> None:
        """Check that we can set source and target languages."""
        unit = self.UnitClass("Test")
        unit.sourcelang = "en"
        unit.targetlang = "af_ZA"
        assert unit.metadata["src-lang"] == "EN-01"
        assert unit.metadata["target-lang"] == "AF-ZA"
        assert unit.sourcelang == "en"
        assert unit.targetlang == "af-za"

    def test_istranslated(self) -> None:
        unit = self.UnitClass()
        assert not unit.istranslated()
        unit.source = "Test"
        assert not unit.istranslated()
        unit.target = "Rest"
        assert unit.istranslated()


class TestWFFile(test_base.TestTranslationStore):
    StoreClass = wf.WordfastTMFile

    @staticmethod
    def serialize(source="Bézier curve", target="Bézier-kurwe") -> bytes:
        store = wf.WordfastTMFile()
        unit = store.addsourceunit(source)
        unit.target = target
        output = BytesIO()
        store.serialize(output)
        return output.getvalue()

    def test_language_detection(self) -> None:
        store = wf.WordfastTMFile()
        store.header.header["src-lang"] = "%EN-01"
        store.header.header["target-lang"] = "%AF-ZA"
        unit = store.addsourceunit("Test")
        unit.sourcelang = "de"
        unit.targetlang = "fr"
        assert store.getsourcelanguage() == "en"
        assert store.gettargetlanguage() == "af-za"
        assert store.sourcelanguage == "en"
        assert store.targetlanguage == "af-za"

        store.sourcelanguage = "de"
        store.targetlanguage = "fr_CA"
        assert store.getsourcelanguage() == "de"
        assert store.gettargetlanguage() == "fr-ca"
        assert store.header.header["src-lang"] == "%DE-01"
        assert store.header.header["target-lang"] == "%FR-CA"

        store.header.header["src-lang"] = ""
        store.header.header["target-lang"] = ""
        assert store.getsourcelanguage() is None
        assert store.gettargetlanguage() is None

    def test_latin1_serialization(self) -> None:
        content = self.serialize()
        assert not content.startswith(BOM_UTF16_LE)
        assert content.count(b"\r\n") == 2
        assert b"\r\r\n" not in content

        reparsed = wf.WordfastTMFile(BytesIO(content))
        assert reparsed.encoding == "iso-8859-1"
        assert reparsed.units[0].source == "Bézier curve"
        assert reparsed.units[0].target == "Bézier-kurwe"

    def test_utf16_fallback(self) -> None:
        store = wf.WordfastTMFile()
        unit = store.addsourceunit("Bézier †")
        unit.target = "Kromme †"
        output = BytesIO()
        store.serialize(output)
        content = output.getvalue()
        assert content.startswith(BOM_UTF16_LE)
        assert store.encoding == "utf-16"
        assert "Bézier †" in content.decode(store.encoding)
        assert content.count("\r\n".encode("utf-16-le")) == 2
        assert b"\r\x00\r\n\x00" not in content

        reparsed = wf.WordfastTMFile(BytesIO(content))
        assert reparsed.encoding == "utf-16"
        assert reparsed.units[0].source == "Bézier †"
        assert reparsed.units[0].target == "Kromme †"

    def test_bomless_utf16le_detection(self) -> None:
        content = self.serialize("Bézier †", "Kromme †").removeprefix(BOM_UTF16_LE)
        reparsed = wf.WordfastTMFile(BytesIO(content))
        assert reparsed.encoding == "utf-16-le"
        assert reparsed.units[0].source == "Bézier †"

    def test_bomless_utf16be_detection(self) -> None:
        content = self.serialize().decode("iso-8859-1").encode("utf-16-be")
        reparsed = wf.WordfastTMFile(BytesIO(content))
        assert reparsed.encoding == "utf-16-be"
        assert reparsed.units[0].source == "Bézier curve"
