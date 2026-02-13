import time

from pytest import importorskip

trados = importorskip("translate.storage.trados", exc_type=ImportError)


def test_unescape() -> None:
    # NBSP
    assert trados.unescape("Ordre du jour\\~:") == "Ordre du jour\u00a0:"
    assert (
        trados.unescape("Association for Road Safety \\endash  Conference")
        == "Association for Road Safety –  Conference"
    )


def test_escape() -> None:
    # NBSP
    assert trados.escape("Ordre du jour\u00a0:") == "Ordre du jour\\~:"
    assert (
        trados.escape("Association for Road Safety –  Conference")
        == "Association for Road Safety \\endash  Conference"
    )


class TestTradosTxtDate:
    """Test TradosTxtDate class."""

    def test_timestring(self) -> None:
        """Setting and getting times set using a timestring."""
        tradostime = trados.TradosTxtDate()
        assert tradostime.timestring is None
        tradostime.timestring = "18012000, 13:18:35"
        assert tradostime.time[:6] == (2000, 1, 18, 13, 18, 35)

    def test_time(self) -> None:
        """Setting and getting times set using time tuple."""
        tradostime = trados.TradosTxtDate()
        assert tradostime.time is None
        tradostime.time = time.strptime("20012000, 14:20:45", trados.TRADOS_TIMEFORMAT)
        assert tradostime.timestring == "20012000, 14:20:45"

    def test_str(self) -> None:
        """Test string representation."""
        tradostime = trados.TradosTxtDate()
        assert str(tradostime) == ""
        tradostime.timestring = "18012000, 13:18:35"
        assert str(tradostime) == "18012000, 13:18:35"

    def test_init_with_timestring(self) -> None:
        """Test initialization with timestring."""
        tradostime = trados.TradosTxtDate("18012000, 13:18:35")
        assert tradostime.timestring == "18012000, 13:18:35"

    def test_init_with_time(self) -> None:
        """Test initialization with time struct."""
        time_struct = time.strptime("20012000, 14:20:45", trados.TRADOS_TIMEFORMAT)
        tradostime = trados.TradosTxtDate(time_struct)
        assert tradostime.timestring == "20012000, 14:20:45"


class TestTradosUnit:
    """Test TradosUnit class - note that this is a read-only format."""

    def test_source_target(self) -> None:
        """Test source and target properties."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>TEST-USER
<UsC>0
<Seg L=EN_GB>Hello World
<Seg L=DE_DE>Hallo Welt
</TrU>"""
        store = trados.TradosTxtTmFile()
        store.parse(trados_content.encode("iso-8859-1"))
        unit = store.units[0]
        assert unit.source == "Hello World"
        assert unit.target == "Hallo Welt"

    def test_escaping_in_content(self) -> None:
        """Test that RTF escapes are properly unescaped."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>TEST-USER
<UsC>0
<Seg L=EN_GB>Association for Road Safety \\endash  Conference
<Seg L=DE_DE>Tagung der Gesellschaft
</TrU>"""
        store = trados.TradosTxtTmFile()
        store.parse(trados_content.encode("iso-8859-1"))
        unit = store.units[0]
        assert unit.source == "Association for Road Safety –  Conference"

    def test_multiple_escapes(self) -> None:
        """Test multiple RTF escape sequences."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>TEST-USER
<UsC>0
<Seg L=EN_GB>\\lquote Test\\rquote \\endash  with\\~NBSP
<Seg L=DE_DE>Translation
</TrU>"""
        store = trados.TradosTxtTmFile()
        store.parse(trados_content.encode("iso-8859-1"))
        unit = store.units[0]
        # \u2018 is left single quotation mark, \u2019 is right single quotation mark
        assert unit.source == "\u2018 Test\u2019 –  with\u00a0NBSP"


class TestTradosTxtTmFile:
    """Test TradosTxtTmFile class - note that this is a read-only format."""

    StoreClass = trados.TradosTxtTmFile

    def test_create_blank(self) -> None:
        """Test creating a blank store."""
        store = self.StoreClass()
        assert len(store.units) == 0

    def test_parse_simple(self) -> None:
        """Test parsing a simple Trados file."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>Hello World
<Seg L=DE_DE>Hallo Welt
</TrU>"""
        store = self.StoreClass()
        store.parse(trados_content.encode("iso-8859-1"))
        assert len(store.units) == 1
        assert store.units[0].source == "Hello World"
        assert store.units[0].target == "Hallo Welt"

    def test_parse_multiple_units(self) -> None:
        """Test parsing multiple translation units."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>First entry
<Seg L=DE_DE>Erster Eintrag
</TrU>
<TrU>
<CrD>18012000, 13:19:14
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>Second entry
<Seg L=DE_DE>Zweiter Eintrag
</TrU>"""
        store = self.StoreClass()
        store.parse(trados_content.encode("iso-8859-1"))
        assert len(store.units) == 2
        assert store.units[0].source == "First entry"
        assert store.units[0].target == "Erster Eintrag"
        assert store.units[1].source == "Second entry"
        assert store.units[1].target == "Zweiter Eintrag"

    def test_parse_with_escapes(self) -> None:
        """Test parsing with RTF escape sequences."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>Use NBSP\\~here
<Seg L=DE_DE>Verwende NBSP\\~hier
</TrU>"""
        store = self.StoreClass()
        store.parse(trados_content.encode("iso-8859-1"))
        assert len(store.units) == 1
        assert store.units[0].source == "Use NBSP\u00a0here"
        assert store.units[0].target == "Verwende NBSP\u00a0hier"

    def test_findunit(self) -> None:
        """Test finding a unit by source text."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>First entry
<Seg L=DE_DE>Erster Eintrag
</TrU>
<TrU>
<CrD>18012000, 13:19:14
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>Second entry
<Seg L=DE_DE>Zweiter Eintrag
</TrU>"""
        store = self.StoreClass()
        store.parse(trados_content.encode("iso-8859-1"))
        unit = store.findunit("First entry")
        assert unit is not None
        assert unit.source == "First entry"
        assert unit.target == "Erster Eintrag"

    def test_translate(self) -> None:
        """Test the translate method."""
        trados_content = """<TrU>
<CrD>18012000, 13:18:35
<CrU>CAROL-ANN
<UsC>0
<Seg L=EN_GB>Hello
<Seg L=DE_DE>Hallo
</TrU>"""
        store = self.StoreClass()
        store.parse(trados_content.encode("iso-8859-1"))
        assert store.translate("Hello") == "Hallo"
        assert store.translate("NotFound") is None

    def test_encoding(self) -> None:
        """Test that the default encoding is iso-8859-1."""
        store = self.StoreClass()
        assert store.default_encoding == "iso-8859-1"

    def test_extensions(self) -> None:
        """Test that extensions are correctly defined."""
        store = self.StoreClass()
        assert "txt" in store.Extensions

    def test_name(self) -> None:
        """Test that the store name is correct."""
        store = self.StoreClass()
        assert store.Name == "Trados Translation Memory"
