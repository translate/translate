from io import BytesIO

from translate.convert import po2tmx, test_convert
from translate.misc.xml_helpers import XML_NS
from translate.storage import tmx


class TestPO2TMX:
    @staticmethod
    def po2tmx(posource, sourcelanguage="en", targetlanguage="af", comment=None):
        """helper that converts po source to tmx source without requiring files"""
        inputfile = BytesIO(posource.encode("utf-8"))
        outputfile = BytesIO()
        outputfile.tmxfile = tmx.tmxfile(inputfile=None, sourcelanguage=sourcelanguage)
        po2tmx.convertpo(
            inputfile,
            outputfile,
            templatefile=None,
            sourcelanguage=sourcelanguage,
            targetlanguage=targetlanguage,
            comment=comment,
        )
        return outputfile.tmxfile

    def test_basic(self):
        minipo = r"""# Afrikaans translation of program ABC
#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"Last-Translator: Zuza Software Foundation <xxx@translate.org.za>\n"
"Language-Team: Afrikaans <translate-discuss-xxx@lists.sourceforge.net>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgid "Applications"
msgstr "Toepassings"
"""
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert tmx.translate("Applications") == "Toepassings"
        assert tmx.translate("bla") is None
        xmltext = bytes(tmx).decode("utf-8")
        assert xmltext.index('creationtool="Translate Toolkit"')
        assert xmltext.index("adminlang")
        assert xmltext.index("creationtoolversion")
        assert xmltext.index("datatype")
        assert xmltext.index("o-tmf")
        assert xmltext.index("segtype")
        assert xmltext.index("srclang")

    def test_sourcelanguage(self):
        minipo = 'msgid "String"\nmsgstr "String"\n'
        tmx = self.po2tmx(minipo, sourcelanguage="xh")
        print("The generated xml:")
        print(bytes(tmx))
        header = tmx.document.find("header")
        assert header.get("srclang") == "xh"

    def test_targetlanguage(self):
        minipo = 'msgid "String"\nmsgstr "String"\n'
        tmx = self.po2tmx(minipo, targetlanguage="xh")
        print("The generated xml:")
        print(bytes(tmx))
        tuv = tmx.document.findall(".//%s" % tmx.namespaced("tuv"))[1]
        # tag[0] will be the source, we want the target tuv
        assert tuv.get("{%s}lang" % XML_NS) == "xh"

    def test_multiline(self):
        """Test multiline po entry"""
        minipo = r'''msgid "First part "
"and extra"
msgstr "Eerste deel "
"en ekstra"'''
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert tmx.translate("First part and extra") == "Eerste deel en ekstra"

    def test_escapednewlines(self):
        """Test the escaping of newlines"""
        minipo = r"""msgid "First line\nSecond line"
msgstr "Eerste lyn\nTweede lyn"
"""
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert tmx.translate("First line\nSecond line") == "Eerste lyn\nTweede lyn"

    def test_escapedtabs(self):
        """Test the escaping of tabs"""
        minipo = r"""msgid "First column\tSecond column"
msgstr "Eerste kolom\tTweede kolom"
"""
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert (
            tmx.translate("First column\tSecond column") == "Eerste kolom\tTweede kolom"
        )

    def test_escapedquotes(self):
        """Test the escaping of quotes (and slash)"""
        minipo = r"""msgid "Hello \"Everyone\""
msgstr "Good day \"All\""

msgid "Use \\\"."
msgstr "Gebruik \\\"."
"""
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert tmx.translate('Hello "Everyone"') == 'Good day "All"'
        assert tmx.translate(r"Use \".") == r"Gebruik \"."

    def test_exclusions(self):
        """Test that empty and fuzzy messages are excluded"""
        minipo = r"""#, fuzzy
msgid "One"
msgstr "Een"

msgid "Two"
msgstr ""

msgid ""
msgstr "Drie"
"""
        tmx = self.po2tmx(minipo)
        print("The generated xml:")
        print(bytes(tmx))
        assert b"<tu" not in bytes(tmx)
        assert len(tmx.units) == 0

    def test_nonascii(self):
        """Tests that non-ascii conversion works."""
        minipo = """msgid "Bézier curve"
msgstr "Bézier-kurwe"
"""
        tmx = self.po2tmx(minipo)
        print(bytes(tmx))
        assert tmx.translate("Bézier curve") == "Bézier-kurwe"

    def test_nonecomments(self):
        """Tests that none comments are imported."""
        minipo = """#My comment rules
msgid "Bézier curve"
msgstr "Bézier-kurwe"
"""
        tmx = self.po2tmx(minipo)
        print(bytes(tmx))
        unit = tmx.findunits("Bézier curve")
        assert len(unit[0].getnotes()) == 0

    def test_otherscomments(self):
        """Tests that others comments are imported."""
        minipo = """#My comment rules
msgid "Bézier curve"
msgstr "Bézier-kurwe"
"""
        tmx = self.po2tmx(minipo, comment="others")
        print(bytes(tmx))
        unit = tmx.findunits("Bézier curve")
        assert unit[0].getnotes() == "My comment rules"

    def test_sourcecomments(self):
        """Tests that source comments are imported."""
        minipo = """#: ../PuzzleFourSided.h:45
msgid "Bézier curve"
msgstr "Bézier-kurwe"
"""
        tmx = self.po2tmx(minipo, comment="source")
        print(bytes(tmx))
        unit = tmx.findunits("Bézier curve")
        assert unit[0].getnotes() == "../PuzzleFourSided.h:45"

    def test_typecomments(self):
        """Tests that others comments are imported."""
        minipo = """#, csharp-format
msgid "Bézier curve"
msgstr "Bézier-kurwe"
"""
        tmx = self.po2tmx(minipo, comment="type")
        print(bytes(tmx))
        unit = tmx.findunits("Bézier curve")
        assert unit[0].getnotes() == "csharp-format"


class TestPO2TMXCommand(test_convert.TestConvertCommand, TestPO2TMX):
    """Tests running actual po2tmx commands on files"""

    convertmodule = po2tmx

    expected_options = [
        "-l LANG, --language=LANG",
        "--source-language=LANG",
        "--comments",
    ]
