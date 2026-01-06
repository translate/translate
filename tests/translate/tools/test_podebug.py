import os

from translate.storage import base, po, xliff
from translate.tools import podebug

PO_DOC = """
msgid "This is a %s test, hooray."
msgstr ""
"""

XLIFF_DOC = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="NoName" source-language="en" datatype="plaintext">
    <body>
      <trans-unit id="office:document-content[0]/office:body[0]/office:text[0]/text:p[0]">
        <source>This <g id="0">is a</g> test <x id="1" xid="office:document-content[0]/office:body[0]/office:text[0]/text:p[0]/text:note[0]"/>, hooray.</source>
      </trans-unit>
    </body>
  </file>
</xliff>
"""


class TestPODebug:
    debug = podebug.podebug()

    def setup_method(self, method) -> None:
        self.postore = po.pofile(PO_DOC.encode("utf-8"))
        self.xliffstore = xliff.xlifffile(XLIFF_DOC.encode("utf-8"))

    def test_ignore_gtk(self) -> None:
        """Test operation of GTK message ignoring."""
        unit = base.TranslationUnit("default:LTR")
        assert self.debug.ignore_gtk(unit)

    def test_keep_target(self) -> None:
        """Test that we use the target for rewriting if it exists."""
        unit = base.TranslationUnit("blie")

        unit.target = "bla"
        debugger = podebug.podebug(rewritestyle="xxx")
        unit = debugger.convertunit(unit, "")
        assert unit.target == "xxxblaxxx"

        unit.target = "d%d"
        debugger = podebug.podebug(rewritestyle="flipped")
        unit = debugger.convertunit(unit, "")
        assert unit.target == "\u202ep%d"

    def test_rewrite_blank(self) -> None:
        """Test the blank rewrite function."""
        assert str(self.debug.rewrite_blank("Test")) == ""

    def test_rewrite_blank_clears_fuzzy(self) -> None:
        """Test that blank rewrite clears fuzzy flags."""
        # Create a PO file with a fuzzy unit
        po_content = b"""
#: test.c:20
#, fuzzy
msgid "Test message"
msgstr "Translated message"
"""
        store = po.pofile(po_content)
        unit = store.units[0]

        # Verify it's fuzzy before processing
        assert unit.isfuzzy()
        assert unit.target == "Translated message"

        # Apply blank rewrite
        debugger = podebug.podebug(rewritestyle="blank")
        unit = debugger.convertunit(unit, "")

        # Verify fuzzy flag is cleared and target is blank
        assert not unit.isfuzzy()
        assert unit.target == ""

    def test_rewrite_blank_with_plurals(self) -> None:
        """Test that blank rewrite works with plural forms."""
        po_content = b"""
#: test.c:30
msgid "One item"
msgid_plural "%d items"
msgstr[0] "Un article"
msgstr[1] "%d articles"
"""
        store = po.pofile(po_content)
        debugger = podebug.podebug(rewritestyle="blank")
        converted = debugger.convertstore(store)

        unit = converted.units[0]
        # Check that all plural forms are blanked
        assert unit.target == ["", ""]

    def test_rewrite_en(self) -> None:
        """Test the en rewrite function."""
        assert str(self.debug.rewrite_en("Test")) == "Test"

    def test_rewrite_xxx(self) -> None:
        """Test the xxx rewrite function."""
        assert str(self.debug.rewrite_xxx("Test")) == "xxxTestxxx"
        assert str(self.debug.rewrite_xxx("Newline\n")) == "xxxNewlinexxx\n"

    def test_rewrite_bracket(self) -> None:
        """Test the bracket rewrite function."""
        assert str(self.debug.rewrite_bracket("Test")) == "[Test]"
        assert str(self.debug.rewrite_bracket("Newline\n")) == "[Newline]\n"

    def test_rewrite_unicode(self) -> None:
        """Test the unicode rewrite function."""
        assert str(self.debug.rewrite_unicode("Test")) == "Ŧḗşŧ"

    def test_rewrite_unicode_preserves_at_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_unicode("@@ph@@Test @@ph@@")) == "@@ph@@Ŧḗşŧ @@ph@@"

    def test_rewrite_unicode_preserves_single_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_unicode("{ph}Test {ph}")) == "{ph}Ŧḗşŧ {ph}"

    def test_rewrite_unicode_preserves_double_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_unicode("{{ph}}Test {{ph}}")) == "{{ph}}Ŧḗşŧ {{ph}}"

    def test_rewrite_unicode_preserves_html(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_unicode("<style0>Test</style0>"))
            == "<style0>Ŧḗşŧ</style0>"
        )

    def test_rewrite_unicode_preserves_multiple_styles_of_placeholder(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_unicode("<b>{{ph}}Test{ph}@@ph@@Test</b>"))
            == "<b>{{ph}}Ŧḗşŧ{ph}@@ph@@Ŧḗşŧ</b>"
        )

    def test_rewrite_flipped(self) -> None:
        """Test the unicode rewrite function."""
        assert str(self.debug.rewrite_flipped("Test")) == "\u202e⊥ǝsʇ"
        # alternative with reversed string and no RTL override:
        # assert unicode(self.debug.rewrite_flipped("Test")) == "ʇsǝ⊥"
        # Chars < ! and > z are returned as is
        assert str(self.debug.rewrite_flipped(" ")) == "\u202e "
        assert str(self.debug.rewrite_flipped("©")) == "\u202e©"

    def test_rewrite_flipped_preserves_at_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_flipped("@@ph@@Test @@ph@@")) == "\u202e@@ph@@⊥ǝsʇ @@ph@@"
        )

    def test_rewrite_flipped_preserves_single_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_flipped("{ph}Test {ph}")) == "\u202e{ph}⊥ǝsʇ {ph}"

    def test_rewrite_flipped_preserves_double_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_flipped("{{ph}}Test {{ph}}")) == "\u202e{{ph}}⊥ǝsʇ {{ph}}"
        )

    def test_rewrite_flipped_preserves_html(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_flipped("<style0>Test </style0>"))
            == "\u202e<style0>⊥ǝsʇ </style0>"
        )

    def test_rewrite_flipped_multiple_styles_of_placeholder(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_flipped("<b>{{ph}}Test{ph}@@ph@@Test</b>"))
            == "\u202e<b>{{ph}}⊥ǝsʇ{ph}@@ph@@⊥ǝsʇ</b>"
        )

    def test_rewrite_classified(self) -> None:
        """Test the unicode rewrite function."""
        assert str(self.debug.rewrite_classified("Test")) == "▮▮▮▮"
        # alternative with reversed string and no RTL override:
        # assert unicode(self.debug.rewrite_classified("Test")) == "ʇsǝ⊥"
        # Chars < ! and > z are returned as is
        assert str(self.debug.rewrite_classified(" ")) == " "
        assert str(self.debug.rewrite_classified("©")) == "©"

    def test_rewrite_classified_preserves_at_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_classified("@@ph@@Test @@ph@@")) == "@@ph@@▮▮▮▮ @@ph@@"

    def test_rewrite_classified_preserves_single_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_classified("{ph}Test {ph}")) == "{ph}▮▮▮▮ {ph}"

    def test_rewrite_classified_preserves_double_brace_placeholders(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert str(debug.rewrite_classified("{{ph}}Test {{ph}}")) == "{{ph}}▮▮▮▮ {{ph}}"

    def test_rewrite_classified_preserves_html(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_classified("<style0>Test </style0>"))
            == "<style0>▮▮▮▮ </style0>"
        )

    def test_rewrite_classified_multiple_styles_of_placeholder(self) -> None:
        """Test the unicode rewrite function."""
        debug = podebug.podebug(preserveplaceholders=True)
        assert (
            str(debug.rewrite_classified("<b>{{ph}}Test{ph}@@ph@@Test</b>"))
            == "<b>{{ph}}▮▮▮▮{ph}@@ph@@▮▮▮▮</b>"
        )

    def test_rewrite_chef(self) -> None:
        """
        Test the chef rewrite function.

        This is not really critical to test but a simple tests ensures
        that it stays working.
        """
        assert (
            str(self.debug.rewrite_chef("Mock Swedish test you muppet"))
            == "Mock Swedish test yooo mooppet"
        )

    def test_po_variables(self) -> None:
        debug = podebug.podebug(rewritestyle="unicode")
        po_out = debug.convertstore(self.postore)

        in_unit = self.postore.units[0]
        out_unit = po_out.units[0]

        assert in_unit.source == out_unit.source
        print(out_unit.target)
        print(bytes(po_out))
        rewrite_func = self.debug.rewrite_unicode
        assert (
            out_unit.target
            == f"{rewrite_func('This is a ')}%s{rewrite_func(' test, hooray.')}"
        )

    def test_xliff_rewrite(self) -> None:
        debug = podebug.podebug(rewritestyle="xxx")
        xliff_out = debug.convertstore(self.xliffstore)

        in_unit = self.xliffstore.units[0]
        out_unit = xliff_out.units[0]

        assert in_unit.source == out_unit.source
        print(out_unit.target)
        print(bytes(xliff_out))
        assert out_unit.target == f"xxx{in_unit.source}xxx"

    def test_hash(self) -> None:
        po_docs = (
            """
msgid "Test msgid 1"
msgstr "Test msgstr 1"
""",
            """
msgctxt "test context"
msgid "Test msgid 2"
msgstr "Test msgstr 2"
""",
            """
# Test comment 3
msgctxt "test context 3"
msgid "Test msgid 3"
msgstr "Test msgstr 3"
""",
        )
        debugs = (
            podebug.podebug(format="%h "),
            podebug.podebug(format="%6h."),
            podebug.podebug(format="zzz%7h.zzz"),
            podebug.podebug(format="%f %F %b %B %d %s "),
            podebug.podebug(format="%3f %4F %5b %6B %7d %8s "),
            podebug.podebug(format="%cf %cF %cb %cB %cd %cs "),
            podebug.podebug(format="%3cf %4cF %5cb %6cB %7cd %8cs "),
        )
        results = [
            # spellchecker:off
            "85a9 Test msgstr 1",
            "a15d Test msgstr 2",
            "6398 Test msgstr 3",
            "85a917.Test msgstr 1",
            "a15d71.Test msgstr 2",
            "639898.Test msgstr 3",
            "zzz85a9170.zzzTest msgstr 1",
            "zzza15d718.zzzTest msgstr 2",
            "zzz639898c.zzzTest msgstr 3",
            "fullpath/to/fakefile fullpath/to/fakefile.po fakefile fakefile.po fullpath/to full-t-fake Test msgstr 1",
            "fullpath/to/fakefile fullpath/to/fakefile.po fakefile fakefile.po fullpath/to full-t-fake Test msgstr 2",
            "fullpath/to/fakefile fullpath/to/fakefile.po fakefile fakefile.po fullpath/to full-t-fake Test msgstr 3",
            "ful full fakef fakefi fullpat full-t-f Test msgstr 1",
            "ful full fakef fakefi fullpat full-t-f Test msgstr 2",
            "ful full fakef fakefi fullpat full-t-f Test msgstr 3",
            "fllpth/t/fkfl fllpth/t/fkfl.p fkfl fkfl.p fllpth/t fll-t-fk Test msgstr 1",
            "fllpth/t/fkfl fllpth/t/fkfl.p fkfl fkfl.p fllpth/t fll-t-fk Test msgstr 2",
            "fllpth/t/fkfl fllpth/t/fkfl.p fkfl fkfl.p fllpth/t fll-t-fk Test msgstr 3",
            "fll fllp fkfl fkfl.p fllpth/ fll-t-fk Test msgstr 1",
            "fll fllp fkfl fkfl.p fllpth/ fll-t-fk Test msgstr 2",
            "fll fllp fkfl fkfl.p fllpth/ fll-t-fk Test msgstr 3",
            # spellchecker:on
        ]

        for debug in debugs:
            for po_doc in po_docs:
                postore = po.pofile(po_doc.encode("utf-8"))
                postore.filename = os.path.join("fullpath", "to", "fakefile.po")
                po_out = debug.convertstore(postore)
                in_unit = postore.units[0]
                out_unit = po_out.units[0]
                assert in_unit.source == out_unit.source
                assert out_unit.target == results.pop(0).replace("/", os.sep)
