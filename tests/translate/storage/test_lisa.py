"""Shared language selection behavior for multilingual LISA formats."""

import pytest

from translate.misc.xml_helpers import getXMLlang
from translate.storage import tbx, tmx


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
