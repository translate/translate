from codecs import BOM_UTF16_LE
from io import BytesIO

from translate.convert import po2wordfast
from translate.storage import wordfast

from . import test_convert

MINIPO = """msgid "Curve"
msgstr "Kurwe"
"""

NON_LATIN1_PO = """msgid "Cross"
msgstr "Крест"
"""


class TestPO2Wordfast:
    @staticmethod
    def po2wordfast(
        posource: str, sourcelanguage="en", targetlanguage="af"
    ) -> wordfast.WordfastTMFile:
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        outputfile.wffile = wordfast.WordfastTMFile()  # ty:ignore[unresolved-attribute]
        po2wordfast.convertpo(
            inputfile,
            outputfile,
            templatefile=None,
            sourcelanguage=sourcelanguage,
            targetlanguage=targetlanguage,
        )
        return outputfile.wffile  # ty:ignore[unresolved-attribute]

    def test_languages(self) -> None:
        store = self.po2wordfast(MINIPO, sourcelanguage="en", targetlanguage="af_ZA")
        assert store.sourcelanguage == "en"
        assert store.targetlanguage == "af-za"
        assert store.header.header["src-lang"] == "%EN-01"
        assert store.header.header["target-lang"] == "%AF-ZA"
        assert store.units[0].metadata["src-lang"] == "EN-01"
        assert store.units[0].metadata["target-lang"] == "AF-ZA"

    def test_non_latin1_output(self) -> None:
        store = self.po2wordfast(NON_LATIN1_PO)
        output = BytesIO()
        store.serialize(output)
        assert output.getvalue().startswith(BOM_UTF16_LE)


class TestPO2WordfastCommand(test_convert.TestConvertCommand, TestPO2Wordfast):
    """Tests running actual po2wordfast commands on files."""

    convertmodule = po2wordfast
    expected_options = [
        "-l LANG, --language=LANG",
        "--source-language=LANG",
    ]

    def test_command_languages(self) -> None:
        self.create_testfile("test.po", MINIPO)
        self.run_command(
            "test.po",
            "test.txt",
            language="af_ZA",
            source_language="xh",
        )
        content = self.read_testfile("test.txt")
        store = wordfast.WordfastTMFile(BytesIO(content))
        assert store.sourcelanguage == "xh"
        assert store.targetlanguage == "af-za"
        assert store.header.header["src-lang"] == "%XH-01"
        assert store.header.header["target-lang"] == "%AF-ZA"
        assert store.units[0].metadata["src-lang"] == "XH-01"
        assert store.units[0].metadata["target-lang"] == "AF-ZA"

    def test_command_default_source_language(self) -> None:
        self.create_testfile("test.po", MINIPO)
        self.run_command("test.po", "test.txt", language="af")
        store = wordfast.WordfastTMFile(BytesIO(self.read_testfile("test.txt")))
        assert store.header.header["src-lang"] == "%EN-01"
        assert store.header.header["target-lang"] == "%AF-01"

    def test_command_utf16_fallback(self) -> None:
        self.create_testfile("test.po", NON_LATIN1_PO)
        self.run_command("test.po", "test.txt", language="ru")
        content = self.read_testfile("test.txt")
        assert content.startswith(BOM_UTF16_LE)
        store = wordfast.WordfastTMFile(BytesIO(content))
        assert store.units[0].target == "Крест"
