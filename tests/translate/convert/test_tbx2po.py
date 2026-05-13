from translate.convert import tbx2po
from translate.storage import po

from . import test_convert


class TestTBX2POCommand(test_convert.TestConvertCommand):
    """Tests running actual tbx2po commands on files."""

    convertmodule = tbx2po

    expected_options = [
        "-l LANG, --language=LANG",
        "--source-language=LANG",
    ]

    @staticmethod
    def multilingual_tbx() -> str:
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX" xml:lang="en">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Translate Toolkit</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="testid">
                <langSet xml:lang="de"><tig><term>Farbe</term></tig></langSet>
                <langSet xml:lang="en"><tig><term>color</term></tig></langSet>
                <langSet xml:lang="es"><tig><term>color espanol</term></tig></langSet>
            </termEntry>
        </body>
    </text>
</martif>
"""

    def test_language_options_select_terms(self) -> None:
        self.create_testfile("terms.tbx", self.multilingual_tbx())
        self.run_command("terms.tbx", "terms.po", source_language="en", language="es")

        with self.open_testfile("terms.po") as handle:
            store = po.pofile(handle)
        unit = store.findunit("color")

        assert unit is not None
        assert unit.target == "color espanol"

    def test_without_language_options_uses_langset_order(self) -> None:
        self.create_testfile("terms.tbx", self.multilingual_tbx())
        self.run_command("terms.tbx", "terms.po")

        with self.open_testfile("terms.po") as handle:
            store = po.pofile(handle)
        unit = store.findunit("Farbe")

        assert unit is not None
        assert unit.target == "color"
