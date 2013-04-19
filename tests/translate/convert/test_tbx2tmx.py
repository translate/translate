from io import BytesIO

import pytest

from translate.convert import tbx2tmx
from translate.misc.xml_helpers import getXMLlang
from translate.storage import tmx

from . import test_convert


def glossary(entries):
    return f'<martif type="TBX"><text><body>{entries}</body></text></martif>'


def language(code, *terms):
    return (
        f'<langSet xml:lang="{code}">'
        + "".join(f"<tig><term>{term}</term></tig>" for term in terms)
        + "</langSet>"
    )


def concept(*languages):
    return "<termEntry>" + "".join(languages) + "</termEntry>"


def convert(entries, source="en", target="cs"):
    output = tmx.tmxfile(sourcelanguage=source, targetlanguage=target)
    tbx2tmx.tbx2tmx().convertfiles(
        BytesIO(glossary(entries).encode()), output, source, target
    )
    return tmx.tmxfile(BytesIO(bytes(output)), targetlanguage=target)


def test_language_selection_and_unicode() -> None:
    output = convert(
        concept(
            language("de", "Farbe"), language("cs", "barva"), language("en", "color")
        )
        + concept(
            language("en", "Bézier &amp; curve"), language("cs", "Bézierova křivka")
        )
    )
    assert [(unit.source, unit.target) for unit in output.units] == [
        ("color", "barva"),
        ("Bézier & curve", "Bézierova křivka"),
    ]
    header = output.document.find("header")
    assert header is not None
    assert header.get("srclang") == "en"
    assert [getXMLlang(node) for node in output.units[0].getlanguageNodes()] == [
        "en",
        "cs",
    ]


def test_alternative_terms() -> None:
    output = convert(
        concept(language("en", "color", "colour"), language("cs", "barva", "zbarvení"))
    )
    assert [(unit.source, unit.target) for unit in output.units] == [
        ("color", "barva"),
        ("color", "zbarvení"),
        ("colour", "barva"),
        ("colour", "zbarvení"),
    ]


def test_missing_languages_and_empty_terms() -> None:
    output = convert(
        concept(language("de", "Farbe"), language("cs", "barva"))
        + concept(language("en", "color"), language("de", "Farbe"))
        + concept(language("en", ""), language("cs", "barva"))
        + concept(language("en", "color"), language("cs", ""))
        + concept(language("en", "", "colour"), language("cs", "", "barva"))
    )
    assert [(unit.source, unit.target) for unit in output.units] == [
        ("colour", "barva")
    ]


def test_deprecated_terms_and_scoped_notes() -> None:
    output = convert("""<termEntry>
        <descrip type="definition">A shared definition</descrip>
        <langSet xml:lang="en">
            <tig><term>old source</term><termNote type="administrativeStatus">deprecated</termNote></tig>
            <tig><term>new source</term><note>Source note</note></tig>
        </langSet>
        <langSet xml:lang="cs">
            <tig><term>old target</term><termNote type="administrativeStatus">deprecated</termNote></tig>
            <tig><term>new target</term><note>Target note</note></tig>
        </langSet>
    </termEntry>""")
    assert len(output.units) == 1
    unit = output.units[0]
    assert (unit.source, unit.target) == ("new source", "new target")
    assert unit.getnotes() == "A shared definition\nSource note\nTarget note"


def test_inline_text() -> None:
    output = convert(
        concept(
            language("en", "a <hi>colored</hi> term"), language("cs", "barevný termín")
        )
    )
    assert output.units[0].source == "a colored term"


class TestTBX2TMXCommand(test_convert.TestConvertCommand):
    convertmodule = tbx2tmx
    expected_options = ["-l LANG, --language=LANG", "--source-language=LANG"]

    def test_file(self) -> None:
        self.create_testfile(
            "terms.tbx",
            glossary(concept(language("de", "Farbe"), language("cs", "barva"))),
        )
        self.run_command("terms.tbx", "terms.tmx", source_language="de", language="cs")
        output = tmx.tmxfile(
            BytesIO(self.read_testfile("terms.tmx")), targetlanguage="cs"
        )
        assert output.units[0].source == "Farbe"
        assert output.units[0].target == "barva"
        header = output.document.find("header")
        assert header is not None
        assert header.get("srclang") == "de"

    def test_directory(self) -> None:
        self.create_testfile(
            "terms/one.tbx",
            glossary(concept(language("en", "one"), language("cs", "jedna"))),
        )
        self.create_testfile(
            "terms/nested/two.tbx",
            glossary(concept(language("en", "two"), language("cs", "dvě"))),
        )
        self.run_command("terms", "combined.tmx", language="cs")
        output = tmx.tmxfile(
            BytesIO(self.read_testfile("combined.tmx")), targetlanguage="cs"
        )
        assert {(unit.source, unit.target) for unit in output.units} == {
            ("one", "jedna"),
            ("two", "dvě"),
        }

    def test_requires_target_language(self) -> None:
        self.create_testfile("terms.tbx", glossary(""))
        with pytest.raises(ValueError, match="You must specify the target language"):
            self.run_command("terms.tbx", "terms.tmx")

    def test_empty_output(self) -> None:
        self.create_testfile("terms.tbx", glossary(""))
        self.run_command("terms.tbx", "terms.tmx", language="cs")
        output = tmx.tmxfile(BytesIO(self.read_testfile("terms.tmx")))
        assert output.units == []
