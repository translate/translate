"""Shared XML serialization and language selection behavior for LISA formats."""

from codecs import BOM_UTF8
from io import BytesIO

import pytest

from translate.misc.xml_helpers import getXMLlang
from translate.storage import (
    aresource,
    base,
    lisa,
    poxliff,
    resx,
    tbx,
    tmx,
    ts2,
    xliff,
    xliff2,
)


@pytest.fixture(
    params=[
        xliff.Xliff1File,
        xliff2.Xliff2File,
        ts2.tsfile,
        resx.RESXFile,
        aresource.AndroidResourceFile,
    ]
)
def encoded_xml_document(request):
    store_class = request.param
    store = store_class()
    unit = store.addsourceunit("café")
    unit.target = "café"
    return store_class, bytes(store)


@pytest.mark.parametrize("file_like", [False, True])
def test_unsupported_xml_encoding(encoded_xml_document, file_like, monkeypatch) -> None:
    store_class, document = encoded_xml_document
    store = store_class()
    error = LookupError("Codec unavailable")

    def reject_encoding(encoding):
        assert encoding.upper() == "UTF-8"
        raise error

    monkeypatch.setattr(lisa, "lookup", reject_encoding)
    with pytest.raises(
        base.ParseError, match=r"(?i)Unsupported XML encoding: UTF-8"
    ) as exc:
        store.parse(BytesIO(document) if file_like else document)
    assert exc.value.__cause__ is error
    assert store.units == []


@pytest.mark.parametrize("encoding", ["UTF-8", "ISO-8859-1"])
@pytest.mark.parametrize("file_like", [False, True])
def test_supported_xml_encoding(encoded_xml_document, encoding, file_like) -> None:
    store_class, document = encoded_xml_document
    text = document.decode("utf-8")
    declaration, body = text.split("?>", 1)
    declaration = declaration.replace("utf-8", encoding).replace("UTF-8", encoding)
    data = (declaration + "?>" + body).encode(encoding)
    store = store_class(BytesIO(data) if file_like else data)
    assert store.encoding.upper() == encoding
    assert store.units[0].target == "café"
    output = bytes(store)
    assert f'encoding="{encoding}"'.lower() in output.decode(encoding).lower()
    assert "café".encode(encoding) in output
    assert store_class.parsestring(output).units[0].target == "café"


@pytest.fixture(params=["1.2", "2.0"])
def xliff_document(request):
    if request.param == "1.2":
        store_class = xliff.Xliff1File
        document = """<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
<file original="test" source-language="en" target-language="cs" datatype="plaintext">
<body><trans-unit id="1"><source>Hello</source><target>Příliš žluťoučký</target></trans-unit></body>
</file></xliff>"""
    else:
        store_class = xliff2.Xliff2File
        document = """<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="cs">
<file id="f1"><unit id="1"><segment><source>Hello</source><target>Příliš žluťoučký</target></segment></unit></file>
</xliff>"""
    return store_class, ('<?xml version="1.0" encoding="UTF-8"?>\n' + document).encode()


@pytest.mark.parametrize("input_bom", [False, True])
@pytest.mark.parametrize("option", [None, False, True])
@pytest.mark.parametrize("uppercase", [False, True])
@pytest.mark.parametrize("file_like", [False, True])
def test_utf8_bom(xliff_document, input_bom, option, uppercase, file_like) -> None:
    store_class, document = xliff_document
    data = (BOM_UTF8 if input_bom else b"") + document
    store = store_class(BytesIO(data)) if file_like else store_class.parsestring(data)
    assert store.XMLutf8BOM is None
    store.XMLutf8BOM = option
    store.XMLuppercaseEncoding = uppercase
    encoding = store.encoding
    expected_bom = input_bom if option is None else option
    declaration_encoding = "UTF-8" if uppercase else "utf-8"
    declaration = f'<?xml version="1.0" encoding="{declaration_encoding}"?>\n'.encode()

    outputs = []
    for _ in range(2):
        out = BytesIO()
        store.serialize(out)
        outputs.extend([out.getvalue(), bytes(store)])
    assert all(output == outputs[0] for output in outputs)
    for output in outputs:
        assert output.count(BOM_UTF8) == int(expected_bom)
        assert output.startswith((BOM_UTF8 if expected_bom else b"") + declaration)
        assert BOM_UTF8 not in output.split(b"?>", 1)[1]
        assert "Příliš žluťoučký".encode() in output
        restored = store_class.parsestring(output)
        assert restored.units[0].target == "Příliš žluťoučký"
    assert store.encoding == encoding


@pytest.mark.parametrize("input_bom", [False, True])
def test_utf8_bom_option_changes(xliff_document, input_bom) -> None:
    store_class, document = xliff_document
    store = store_class.parsestring((BOM_UTF8 if input_bom else b"") + document)
    other = store_class.parsestring(document)
    assert store_class().XMLutf8BOM is None
    assert not bytes(store_class()).startswith(BOM_UTF8)
    for option in (True, False, None, True, None):
        store.XMLutf8BOM = option
        expected_bom = input_bom if option is None else option
        assert bytes(store).startswith(BOM_UTF8) == expected_bom
        assert other.XMLutf8BOM is None
        assert not bytes(other).startswith(BOM_UTF8)
    store.parse(document if input_bom else BOM_UTF8 + document)
    assert store.XMLutf8BOM is None
    assert bytes(store).startswith(BOM_UTF8) != input_bom


@pytest.mark.parametrize("encoding", ["UTF-8", "utf8", "utf_8"])
@pytest.mark.parametrize("uppercase", [False, True])
def test_utf8_bom_encoding_alias(xliff_document, encoding, uppercase) -> None:
    store_class, document = xliff_document
    store = store_class.parsestring(document)
    store.encoding = encoding
    store.XMLutf8BOM = True
    store.XMLuppercaseEncoding = uppercase
    output = bytes(store)
    declaration_encoding = "UTF-8" if uppercase else "utf-8"
    assert output.startswith(
        BOM_UTF8 + f'<?xml version="1.0" encoding="{declaration_encoding}"?>'.encode()
    )
    assert output.count(BOM_UTF8) == 1
    assert store_class.parsestring(output).units[0].target == "Příliš žluťoučký"
    assert store.encoding == encoding


def test_utf8_bom_non_utf8_encoding(xliff_document) -> None:
    store_class, document = xliff_document
    store = store_class.parsestring(BOM_UTF8 + document)
    store.units[0].target = "café"
    store.encoding = "ISO-8859-1"
    store.XMLutf8BOM = False
    expected = bytes(store)
    for option in (True, None):
        store.XMLutf8BOM = option
        assert bytes(store) == expected
    assert BOM_UTF8 not in expected
    assert b'encoding="ISO-8859-1"' in expected
    assert "café".encode("ISO-8859-1") in expected
    assert store_class.parsestring(expected).units[0].target == "café"


@pytest.mark.parametrize(
    "store_class", [aresource.AndroidResourceFile, poxliff.PoXliffFile]
)
@pytest.mark.parametrize("input_bom", [False, True])
def test_utf8_bom_custom_parser(store_class, input_bom) -> None:
    document = bytes(store_class())
    store = store_class.parsestring((BOM_UTF8 if input_bom else b"") + document)
    assert store.XMLutf8BOM is None
    assert bytes(store).startswith(BOM_UTF8) == input_bom
    for option in (True, False, None):
        store.XMLutf8BOM = option
        output = bytes(store)
        expected_bom = input_bom if option is None else option
        assert output.startswith(BOM_UTF8) == expected_bom
        assert output.count(BOM_UTF8) == int(expected_bom)
        store_class.parsestring(output)


@pytest.fixture(params=[tbx.tbxfile, tmx.tmxfile])
def multilingual_store(request):
    """Create stores with ordered language nodes for either format."""
    store_class = request.param

    def create(languages, source="en", target="ko"):
        store = store_class(sourcelanguage=source, targetlanguage=target)
        unit = store.UnitClass(None)
        for language, text in languages:
            unit.xmlelement.append(unit.createlanguageNode(language, text, "source"))
        store.addunit(unit)
        return store_class.parsestring(
            bytes(store), sourcelanguage=source, targetlanguage=target
        )

    return create


def test_default_country_lookup(multilingual_store) -> None:
    store = multilingual_store([("EN_us", "source"), ("KO-kr", "target")])
    unit = store.units[0]
    assert unit.source == "source"
    assert unit.target == "target"
    assert unit.gettarget("KO") == "target"
    assert unit.gettarget("en_US") == "source"


@pytest.mark.parametrize("exact_first", [True, False])
def test_exact_language_wins(multilingual_store, exact_first) -> None:
    languages = [
        ("EN", "exact source"),
        ("ko", "exact target"),
        ("en-US", "regional source"),
        ("ko-KR", "regional target"),
    ]
    if not exact_first:
        languages.reverse()
    unit = multilingual_store(languages).units[0]
    assert unit.source == "exact source"
    assert unit.target == "exact target"
    assert unit.gettarget("ko") == "exact target"


@pytest.mark.parametrize(
    ("requested", "available"),
    [
        ("en", "en-GB"),
        ("en-GB", "en-US"),
        ("en-US", "en"),
        ("en-Latn", "en-US"),
        ("zh", "zh-CN"),
        ("unknown", "unknown-US"),
    ],
)
def test_unmatched_language_stays_empty(
    multilingual_store, requested, available
) -> None:
    unit = multilingual_store(
        [(available, "unmatched")], source=requested, target=requested
    ).units[0]
    assert unit.source is None
    assert unit.target is None
    assert unit.gettarget(requested) is None


def test_weblate_default_country(multilingual_store) -> None:
    unit = multilingual_store(
        [("pt-BR", "Brazil"), ("pt-PT", "Portugal")], source="pt"
    ).units[0]
    assert unit.source == "Portugal"


@pytest.mark.parametrize("explicit", [True, False])
def test_fallback_edits_preserve_languages(multilingual_store, explicit) -> None:
    store = multilingual_store(
        [("en-US", "source"), ("ko-KR", "target"), ("de", "untouched")]
    )
    unit = store.units[0]
    assert store.findunit("source") is unit
    if explicit:
        unit.setsource("updated source", "en")
        unit.settarget("updated target", "ko")
    else:
        unit.source = "updated source"
        unit.target = "updated target"
    assert store.findunit("source") is None
    assert store.findunit("updated source") is unit
    restored = (
        type(store)
        .parsestring(bytes(store), sourcelanguage="en", targetlanguage="ko")
        .units[0]
    )
    assert restored.source == "updated source"
    assert restored.target == "updated target"
    assert restored.gettarget("de") == "untouched"
    assert [getXMLlang(node) for node in restored.getlanguageNodes()] == [
        "en-US",
        "ko-KR",
        "de",
    ]


def test_fallback_language_changes_invalidate_indexes(multilingual_store) -> None:
    store = multilingual_store([("en-US", "English"), ("ko-KR", "Korean")])
    assert store.findunit("English") is store.units[0]
    store.setsourcelanguage("ko")
    store.settargetlanguage("en")
    assert store.findunit("English") is None
    assert store.findunit("Korean") is store.units[0]
    assert store.units[0].target == "English"


def test_missing_target_with_fallback_source(multilingual_store) -> None:
    unit = multilingual_store([("en-US", "source")]).units[0]
    assert unit.source == "source"
    assert unit.target is None
    assert not unit.istranslated()
    assert not unit.isblank()


def test_tbx_dnt_missing_target() -> None:
    store = tbx.tbxfile.parsestring(
        '<martif type="TBX"><text><body><termEntry id="c218">'
        '<descrip type="Translation needed">No</descrip>'
        '<langSet xml:lang="en-us"><tig id="c218-4">'
        "<term>SUSE Multi-Linux Manager</term></tig></langSet>"
        "</termEntry></body></text></martif>",
        sourcelanguage="en",
        targetlanguage="de",
    )
    assert len(store.units) == 1
    unit = store.units[0]
    assert unit.source == "SUSE Multi-Linux Manager"
    assert unit.target is None
    assert not unit.isblank()
    assert not unit.isobsolete()
    assert not unit.istranslated()
    assert not unit.istranslatable()


@pytest.mark.parametrize("multilingual_store", [tmx.tmxfile], indirect=True)
def test_tmx_translate_default_country(multilingual_store) -> None:
    store = multilingual_store([("en-US", "source"), ("ko-KR", "target")])
    assert store.translate("source", sourcelang="en", targetlang="ko") == "target"
    store.units[0].source = "updated"
    assert store.translate("source", sourcelang="en", targetlang="ko") is None
    assert store.translate("updated", sourcelang="en", targetlang="ko") == "target"


@pytest.mark.parametrize("multilingual_store", [tmx.tmxfile], indirect=True)
def test_tmx_translate_exact_language_wins(multilingual_store) -> None:
    store = multilingual_store(
        [("en-US", "regional"), ("en", "exact"), ("ko-KR", "target")]
    )
    assert store.translate("regional", sourcelang="en", targetlang="ko") is None
    assert store.translate("exact", sourcelang="en", targetlang="ko") == "target"


@pytest.mark.parametrize("multilingual_store", [tmx.tmxfile], indirect=True)
@pytest.mark.parametrize("exact_first", [False, True])
def test_tmx_translate_prefers_exact_across_units(
    multilingual_store, exact_first
) -> None:
    regional = multilingual_store([("en-US", "source"), ("ko-KR", "regional")])
    exact = multilingual_store([("en", "source"), ("ko-KR", "exact")])
    store, other = (exact, regional) if exact_first else (regional, exact)
    store.addunit(other.units[0])
    assert store.translate("source", sourcelang="en", targetlang="ko") == "exact"
    assert store.translate("source", sourcelang="en-US", targetlang="ko") == "regional"


def test_source_language_change_preserves_sibling(multilingual_store) -> None:
    store = multilingual_store([("de", "source"), ("fr-FR", "sibling")], source="de")
    unit = store.units[0]
    unit.setsource("updated", "fr")
    restored = type(store).parsestring(
        bytes(store), sourcelanguage="fr", targetlanguage="fr-FR"
    )
    assert restored.units[0].source == "updated"
    assert restored.units[0].target == "sibling"
    assert [getXMLlang(node) for node in restored.units[0].getlanguageNodes()] == [
        "fr",
        "fr-FR",
    ]


@pytest.mark.parametrize("explicit", [False, True])
def test_target_fallback_does_not_use_source(multilingual_store, explicit) -> None:
    store = multilingual_store([("en-US", "source")], source="en-US", target="en")
    unit = store.units[0]
    assert unit.target is None
    assert unit.gettarget("en") is None
    assert not unit.istranslated()
    unit.settarget(None, lang="en" if explicit else None)
    assert unit.source == "source"
    unit.settarget("target", lang="en" if explicit else None)
    restored = type(store).parsestring(
        bytes(store), sourcelanguage="en-US", targetlanguage="en"
    )
    assert restored.units[0].source == "source"
    assert restored.units[0].target == "target"
    assert [getXMLlang(node) for node in restored.units[0].getlanguageNodes()] == [
        "en-US",
        "en",
    ]


def test_explicit_source_language_remains_selectable(multilingual_store) -> None:
    unit = multilingual_store([("en-US", "source")], source="en", target="en").units[0]
    assert unit.target == "source"
    assert unit.gettarget("en-US") == "source"
