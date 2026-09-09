"""Independent terminology alternatives and lossless TBX editing."""

from io import StringIO
from unittest.mock import patch

import pytest
from lxml import etree

from translate.storage.tbx import match_term_indices, tbxfile


def parse_terms(namespace=""):
    data = f"""<martif {namespace} type="TBX"><text><body>
      <termEntry id="concept">
        <descrip type="definition">Shared definition</descrip>
        <langSet xml:lang="en">
          <tig id="old"><term>legacy dashboard</term><termNote type="administrativeStatus">obsolete</termNote><note from="developer">Old name</note></tig>
          <tig id="current"><term>dashboard</term><termNote type="administrativeStatus">preferred</termNote></tig>
        </langSet>
        <langSet xml:lang="ko-KR">
          <note from="translator">Korean explanation</note>
          <tig id="one"><term>하나</term><descrip type="Usage note">First usage</descrip></tig>
          <tig><term>둘</term><termNote type="administrativeStatus">forbidden</termNote></tig>
          <tig id="three"><term>셋</term></tig>
        </langSet>
        <langSet xml:lang="de"><tig><term>Deutsch</term><note from="translator">German only</note></tig></langSet>
      </termEntry>
    </body></text></martif>"""
    return tbxfile.parsestring(data, sourcelanguage="en", targetlanguage="ko_KR")


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_alternatives(namespace):
    store = parse_terms(namespace)
    before = etree.tostring(store.document)
    unit = store.units[0]
    assert len(store.units) == 1
    assert [term.text for term in unit.get_source_terms()] == [
        "legacy dashboard",
        "dashboard",
    ]
    targets = unit.get_target_terms()
    assert [term.id for term in targets] == ["one", None, "three"]
    assert targets[1].administrative_status == "forbidden"
    assert {note.text for note in targets[0].notes} == {
        "Shared definition",
        "Korean explanation",
        "First usage",
    }
    assert "Old name" not in {note.text for note in unit.get_source_terms()[1].notes}
    assert unit.source == "legacy dashboard"
    assert unit.target == "하나"
    assert not unit.isobsolete()
    assert unit.get_target_terms("fr") == []
    unit.set_target_terms([term.text for term in targets])
    assert etree.tostring(store.document) == before


def test_edit_terms_preserves_metadata():
    store = parse_terms()
    unit = store.units[0]
    german = etree.tostring(unit.get_target_dom("de"))
    unit.set_target_terms(["셋", "하나 renamed", "둘", "new"])
    terms = unit.get_target_terms()
    assert [term.id for term in terms] == ["three", "one", None, None]
    assert "First usage" in {note.text for note in terms[1].notes}
    assert terms[2].administrative_status == "forbidden"
    assert terms[3].administrative_status is None
    assert etree.tostring(unit.get_target_dom("de")) == german
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    )
    assert restored.units[0].get_target_terms() == terms
    unit.set_target_terms(["둘"])
    assert unit.get_target_terms()[0].administrative_status == "forbidden"
    unit.set_target_terms([])
    assert [term.text for term in unit.get_target_terms()] == [""]
    assert unit.get_common_notes()[-1].text == "Korean explanation"


def test_duplicates_and_ambiguous_edits():
    assert match_term_indices(["a", "b", "a"], ["a", "a", "b"]) == [0, 2, 1]
    assert match_term_indices(["a", "b", "c"], ["c", "renamed"]) == [2, 0]
    assert match_term_indices([], ["new"]) == [None]


def test_scalar_source_preserves_siblings_and_ids():
    unit = parse_terms().units[0]
    unit.source = "Old renamed"
    assert [term.id for term in unit.get_source_terms()] == ["old", "current"]
    assert unit.get_source_terms()[1].text == "dashboard"
    unit.target = "First renamed"
    assert len(unit.get_target_terms()) == 3
    assert unit.get_target_terms()[0].id == "one"


def test_common_explanation_preserves_term_notes():
    unit = parse_terms().units[0]
    unit.set_common_note("New definition", source=True)
    unit.set_common_note("New Korean note")
    terms = unit.get_target_terms()
    assert {note.text for note in terms[0].notes} == {
        "New definition",
        "New Korean note",
        "First usage",
    }
    assert unit.get_target_terms("de")[0].notes[-1].text == "German only"


def test_note_scopes_and_missing_language_explanation():
    store = parse_terms()
    unit = store.units[0]
    assert [(note.text, note.scope) for note in unit.get_target_terms()[0].notes] == [
        ("Shared definition", "concept"),
        ("Korean explanation", "language"),
        ("First usage", "term"),
    ]
    korean = etree.tostring(unit.target_dom)
    store.settargetlanguage("fr")
    unit.set_common_note("French explanation")
    assert [term.text for term in unit.get_target_terms()] == [""]
    assert unit.get_common_notes()[-1].scope == "language"
    assert etree.tostring(unit.get_target_dom("ko-KR")) == korean
    assert "French explanation" not in {
        note.text for note in unit.get_common_notes(source=True)
    }


def test_whitespace_noop():
    unit = tbxfile.parsestring(
        '<martif><text><body><termEntry xml:space="default">'
        '<langSet xml:lang="en"><tig><term>  one   two  </term></tig></langSet>'
        "</termEntry></body></text></martif>",
        sourcelanguage="en",
    ).units[0]
    before = etree.tostring(unit.xmlelement)
    terms = unit.get_source_terms()
    assert terms[0].text == "one two"
    unit.set_source_terms([terms[0].text])
    assert etree.tostring(unit.xmlelement) == before


def test_missing_target_and_language_setters():
    store = parse_terms()
    unit = store.units[0]
    etree.SubElement(unit.xmlelement, "descrip", type="Translation needed").text = "No"
    store.settargetlanguage("fr")
    before = etree.tostring(store.document)
    assert unit.get_target_terms() == []
    assert not unit.istranslated()
    assert not unit.istranslatable()
    unit.set_target_terms([])
    assert etree.tostring(store.document) == before
    store.setsourcelanguage("de")
    assert unit.get_source_terms()[0].text == "Deutsch"
    unit.set_target_terms(["French"])
    assert unit.get_target_terms()[0].text == "French"


def test_deprecated_siblings():
    unit = parse_terms().units[0]
    for node in unit.xmlelement.findall(".//termNote[@type='administrativeStatus']"):
        node.text = "deprecated"
    assert not unit.isobsolete()
    for tig in unit.xmlelement.findall(".//tig"):
        node = tig.find("termNote[@type='administrativeStatus']")
        if node is None:
            node = etree.SubElement(tig, "termNote", type="administrativeStatus")
        node.text = "deprecated"
    assert unit.isobsolete()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_active_unselected_language_prevents_obsolescence(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    for language in (unit.source_dom, unit.target_dom):
        for tig in language.findall(unit.namespaced("tig")):
            status = tig.find(
                f"{unit.namespaced('termNote')}[@type='administrativeStatus']"
            )
            if status is None:
                status = etree.SubElement(
                    tig, unit.namespaced("termNote"), type="administrativeStatus"
                )
            status.text = "deprecated"
    assert all(term.deprecated for term in unit.get_source_terms())
    assert all(term.deprecated for term in unit.get_target_terms())
    assert not unit.isobsolete()
    german = unit.get_target_dom("de")
    etree.SubElement(
        german.find(unit.namespaced("tig")),
        unit.namespaced("termNote"),
        type="administrativeStatus",
    ).text = "deprecated"
    assert unit.isobsolete()
    store.settargetlanguage("fr")
    assert unit.isobsolete()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_term_ids_and_tig_precedence(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    tigs = unit.target_dom.findall(unit.namespaced("tig"))
    tigs[0].find(unit.namespaced("term")).set("id", "nested-first")
    tigs[1].find(unit.namespaced("term")).set("id", "nested-second")
    before = etree.tostring(unit.xmlelement)
    assert [term.id for term in unit.get_target_terms()] == [
        "one",
        "nested-second",
        "three",
    ]
    assert etree.tostring(unit.xmlelement) == before
    unit.set_target_terms(["둘", "renamed", "셋"])
    assert [term.id for term in unit.get_target_terms()] == [
        "nested-second",
        "one",
        "three",
    ]
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    assert restored.get_target_terms() == unit.get_target_terms()
    assert (
        restored.target_dom.find(
            f"{unit.namespaced('tig')}/{unit.namespaced('term')}"
        ).get("id")
        == "nested-second"
    )


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("empty_tig", [False, True])
def test_scalar_target_populates_empty_language(namespace, empty_tig):
    store = parse_terms(namespace)
    unit = store.units[0]
    korean = etree.tostring(unit.target_dom)
    store.settargetlanguage("fr")
    unit.set_common_note("French explanation")
    for node in unit.target_dom.findall(unit.namespaced("tig")):
        unit.target_dom.remove(node)
    if empty_tig:
        etree.SubElement(unit.target_dom, unit.namespaced("tig"), id="empty")
    unit.target = "French term"
    assert unit.target == "French term"
    assert (
        unit.target_dom.find(f"{unit.namespaced('tig')}/{unit.namespaced('term')}").text
        == "French term"
    )
    assert unit.get_common_notes()[-1].text == "French explanation"
    assert etree.tostring(unit.get_target_dom("ko-KR")) == korean
    if empty_tig:
        assert unit.get_target_terms()[0].id == "empty"
    unit.set_target_terms([])
    store.settargetlanguage("ko-KR")
    unit.settarget("Replacement", lang="fr")
    assert unit.gettarget("fr") == "Replacement"
    assert unit.target == "하나"
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="fr"
    ).units[0]
    assert restored.target == "Replacement"
    assert restored.get_common_notes()[-1].text == "French explanation"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("with_note", [False, True])
def test_missing_target_inserted_after_source(namespace, with_note):
    store = parse_terms(namespace)
    unit = store.units[0]
    korean = etree.tostring(unit.target_dom)
    german = etree.tostring(unit.get_target_dom("de"))
    store.settargetlanguage("fr")
    if with_note:
        unit.set_common_note("French explanation")
    unit.set_target_terms(["French term", "French alternative"])
    assert unit.source_dom.getnext() is unit.target_dom
    assert etree.tostring(unit.get_target_dom("ko-KR")) == korean
    assert etree.tostring(unit.get_target_dom("de")) == german
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "legacy dashboard"
    assert restored.target == "French term"
    assert [term.text for term in restored.get_target_terms()] == [
        "French term",
        "French alternative",
    ]
    if with_note:
        assert restored.get_common_notes()[-1].text == "French explanation"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("empty_tig", [False, True])
def test_scalar_source_populates_empty_language(namespace, empty_tig):
    store = parse_terms(namespace)
    unit = store.units[0]
    korean = etree.tostring(unit.target_dom)
    language = unit.source_dom
    note = etree.Element(unit.namespaced("note"), {"from": "developer"})
    note.text = "Source language note"
    language.insert(0, note)
    for node in language.findall(unit.namespaced("tig")):
        language.remove(node)
    if empty_tig:
        etree.SubElement(language, unit.namespaced("tig"), id="empty")
    unit.source = "New source"
    assert unit.source_dom is language
    assert unit.source == "New source"
    assert unit.get_common_notes(source=True)[-1].text == "Source language note"
    assert etree.tostring(unit.target_dom) == korean
    if empty_tig:
        assert unit.get_source_terms()[0].id == "empty"
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "New source"
    assert restored.get_common_notes(source=True)[-1].text == "Source language note"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_missing_source_inserted_before_languages(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    languages = [etree.tostring(node) for node in unit.getlanguageNodes()]
    store.setsourcelanguage("fr")
    assert unit.get_source_terms() == []
    unit.set_source_terms(["French source", "French alternative"])
    assert unit.getlanguageNodes()[0] is unit.source_dom
    assert [etree.tostring(node) for node in unit.getlanguageNodes()[1:]] == languages
    assert unit.xmlelement[0].tag == unit.namespaced("descrip")
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "French source"
    assert restored.target == "legacy dashboard"
    assert [term.text for term in restored.get_source_terms()] == [
        "French source",
        "French alternative",
    ]


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("language", [None, "en", "ko-KR", "de"])
@pytest.mark.parametrize("term_scope", [False, True])
def test_nested_translation_needed(namespace, language, term_scope):
    store = parse_terms(namespace)
    unit = store.units[0]
    parent = unit.xmlelement if language is None else unit.getlanguageNode(language)
    if term_scope:
        # Also cover grouped metadata inside each scope.
        if language is not None:
            parent = parent.find(unit.namespaced("tig"))
        parent = etree.SubElement(parent, unit.namespaced("descripGrp"))
    flag = etree.SubElement(
        parent, unit.namespaced("descrip"), type="Translation needed"
    )
    flag.text = "No"
    assert not unit.istranslatable()
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    assert not restored.istranslatable()
    flag.text = "Yes"
    assert unit.istranslatable()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("selected_target", ["ko-KR", "es", None])
def test_explicit_unrelated_language_preserves_fallback_target(
    namespace, selected_target
):
    store = parse_terms(namespace)
    unit = store.units[0]
    store.settargetlanguage(selected_target)
    languages = [etree.tostring(node) for node in unit.getlanguageNodes()]
    unit.set_target_terms(["French term"], lang="fr")
    assert [etree.tostring(node) for node in unit.getlanguageNodes()[:-1]] == languages
    assert unit.gettarget("fr") == "French term"
    assert unit.target == (None if selected_target == "es" else "하나")
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "legacy dashboard"
    assert restored.target == "하나"
    assert restored.gettarget("fr") == "French term"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_explicit_selected_target_preserves_fallback_order(namespace):
    store = parse_terms(namespace)
    store.settargetlanguage("fr-FR")
    unit = store.units[0]
    unit.set_target_terms(["French term"], lang="FR_fr")
    assert unit.source_dom.getnext() is unit.target_dom
    assert unit.target == "French term"
    assert tbxfile.parsestring(bytes(store)).units[0].target == "French term"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("selected_source", ["en", "es", None])
def test_explicit_unrelated_language_preserves_fallback_source(
    namespace, selected_source
):
    store = parse_terms(namespace)
    unit = store.units[0]
    store.setsourcelanguage(selected_source)
    languages = [etree.tostring(node) for node in unit.getlanguageNodes()]
    unit.set_source_terms(["French term"], lang="fr")
    assert [etree.tostring(node) for node in unit.getlanguageNodes()[:-1]] == languages
    assert unit.gettarget("fr") == "French term"
    assert unit.source == (None if selected_source == "es" else "legacy dashboard")
    assert unit.target == "하나"
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "legacy dashboard"
    assert restored.target == "하나"
    assert restored.gettarget("fr") == "French term"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_explicit_selected_source_preserves_fallback_order(namespace):
    store = parse_terms(namespace)
    store.setsourcelanguage("fr-FR")
    unit = store.units[0]
    unit.set_source_terms(["French term"], lang="FR_fr")
    assert unit.getlanguageNodes()[0] is unit.source_dom
    assert unit.source == "French term"
    assert tbxfile.parsestring(bytes(store)).units[0].source == "French term"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("with_note", [False, True])
@pytest.mark.parametrize("explicit", [False, True])
def test_missing_target_keeps_nonleading_source_in_fallback_pair(
    namespace, with_note, explicit
):
    store = parse_terms(namespace)
    unit = store.units[0]
    source = unit.source_dom
    german = unit.get_target_dom("de")
    source.addprevious(german)
    previous = {
        code: etree.tostring(unit.getlanguageNode(code), with_tail=False)
        for code in ("en", "ko-KR", "de")
    }
    store.settargetlanguage("fr")
    if with_note:
        unit.set_common_note("French explanation")
    unit.set_target_terms(["French term"], lang="fr" if explicit else None)
    assert unit.getlanguageNodes()[:2] == [source, unit.target_dom]
    assert unit.xmlelement[0].tag == unit.namespaced("descrip")
    for code, content in previous.items():
        assert etree.tostring(unit.getlanguageNode(code), with_tail=False) == content
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "legacy dashboard"
    assert restored.target == "French term"
    if with_note:
        assert restored.get_common_notes()[-1].text == "French explanation"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_unrelated_target_does_not_move_nonleading_source(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    unit.source_dom.addprevious(unit.get_target_dom("de"))
    languages = [etree.tostring(node) for node in unit.getlanguageNodes()]
    unit.set_target_terms(["French term"], lang="fr")
    assert [etree.tostring(node) for node in unit.getlanguageNodes()[:-1]] == languages
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert restored.source == "Deutsch"
    assert restored.target == "legacy dashboard"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("source", [False, True])
@pytest.mark.parametrize(
    ("configured", "requested", "selected"),
    [
        ("fr", "FR_fr", True),
        ("fr-FR", "fr", False),
        ("fr-CA", "fr-FR", False),
        ("fr", "fr-CA", False),
    ],
)
def test_new_language_uses_reader_matching(
    namespace, source, configured, requested, selected
):
    store = parse_terms(namespace)
    unit = store.units[0]
    if source:
        store.setsourcelanguage(configured)
        setter = unit.set_source_terms
    else:
        store.settargetlanguage(configured)
        setter = unit.set_target_terms
    languages = [
        etree.tostring(node, with_tail=False) for node in unit.getlanguageNodes()
    ]
    setter(["New term"], lang=requested)
    assert (unit.source if source else unit.target) == (
        "New term" if selected else None
    )
    restored = tbxfile.parsestring(bytes(store)).units[0]
    if selected:
        assert (restored.source if source else restored.target) == "New term"
    else:
        assert [
            etree.tostring(node, with_tail=False)
            for node in unit.getlanguageNodes()[:-1]
        ] == languages
        assert restored.source == "legacy dashboard"
        assert restored.target == "하나"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("source", [False, True])
def test_new_default_variant_preserves_existing_exact_match(namespace, source):
    store = parse_terms(namespace)
    unit = store.units[0]
    if source:
        store.setsourcelanguage("fr")
        setter = unit.set_source_terms
    else:
        store.settargetlanguage("fr")
        setter = unit.set_target_terms
    setter(["Exact term"])
    languages = [etree.tostring(node) for node in unit.getlanguageNodes()]
    setter(["Regional term"], lang="fr-FR")
    assert [etree.tostring(node) for node in unit.getlanguageNodes()[:-1]] == languages
    assert (unit.source if source else unit.target) == "Exact term"
    restored = tbxfile.parsestring(bytes(store)).units[0]
    assert (restored.source if source else restored.target) == "Exact term"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_empty_scalar_source_edit_refreshes_lookup(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    unit.set_source_terms([])
    store.makeindex()
    unit.setsource("")
    assert store.findunit("") is None
    assert store.findid("concept") is unit
    assert None not in store.sourceindex


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_source_language_edit_preserves_alternatives_and_metadata(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    source = unit.source_dom
    terms = unit.get_source_terms()
    targets = unit.get_target_terms()
    assert store.findunit("legacy dashboard") is unit
    unit.setsource("French source", sourcelang="fr")
    store.setsourcelanguage("fr")
    assert unit.source_dom is source
    assert store.findunit("legacy dashboard") is None
    assert store.findunit("French source") is unit
    assert unit.get_source_terms()[0].id == terms[0].id
    assert unit.get_source_terms()[0].notes == terms[0].notes
    assert (
        unit.get_source_terms()[0].administrative_status
        == terms[0].administrative_status
    )
    assert unit.get_source_terms()[1] == terms[1]
    assert unit.get_target_terms() == targets
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="fr", targetlanguage="ko-KR"
    ).units[0]
    assert restored.get_source_terms() == unit.get_source_terms()
    assert restored.get_target_terms() == targets


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("explicit_id", [False, True])
def test_source_alternatives_refresh_identity_indexes(namespace, explicit_id):
    store = parse_terms(namespace)
    unit = store.units[0]
    if not explicit_id:
        unit.xmlelement.attrib.pop("id")
    old_id = unit.getid()
    assert store.findid(old_id) is unit
    assert store.findunit("legacy dashboard") is unit
    unit.set_source_terms(["dashboard", "Renamed source"])
    assert store.findunit("legacy dashboard") is None
    assert store.findunit("dashboard") is unit
    assert store.findid(unit.getid()) is unit
    assert unit.getid() == (old_id if explicit_id else "dashboard")
    if not explicit_id:
        assert store.findid(old_id) is None
    assert [term.id for term in unit.get_source_terms()] == ["current", "old"]
    unit.setid("renamed-concept")
    assert store.findid("renamed-concept") is unit
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    )
    assert (
        restored.findid("renamed-concept").get_source_terms() == unit.get_source_terms()
    )


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("targets", [["", "French"], ["French", ""], ["", ""], []])
def test_translation_status_uses_all_selected_target_terms(
    namespace, targets, monkeypatch
):
    store = parse_terms(namespace)
    store.settargetlanguage("fr")
    unit = store.units[0]
    unit.set_target_terms(targets)
    assert unit.istranslated() == any(targets)
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="fr"
    ).units[0]
    assert restored.istranslated() == any(targets)
    # Other populated languages must not count towards the selected target.
    store.settargetlanguage("es")
    assert not unit.istranslated()
    store.settargetlanguage("fr")
    monkeypatch.setattr(unit, "isfuzzy", lambda: True)
    assert not unit.istranslated()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_unselected_language_keeps_concept_nonblank_and_indexed(namespace):
    store = tbxfile.parsestring(
        f'<martif {namespace}><text><body><termEntry id="german-only">'
        '<langSet xml:lang="de"><tig><term></term></tig>'
        "<tig><term>Deutsch</term></tig></langSet>"
        "</termEntry></body></text></martif>",
        sourcelanguage="en",
        targetlanguage="fr",
    )
    unit = store.units[0]
    assert unit.source is None
    assert unit.target is None
    assert not unit.isblank()
    assert not unit.istranslated()
    assert store.findid("german-only") is unit
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="fr"
    )
    assert restored.findid("german-only") is not None
    unit.set_target_terms(["", ""], lang="de")
    assert unit.isblank()
    assert store.findid("german-only") is None


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_absent_source_is_not_indexed(namespace):
    store = parse_terms(namespace)
    store.setsourcelanguage("fr")
    unit = store.units[0]
    assert unit.source is None
    assert store.findid("concept") is unit
    assert None not in store.sourceindex
    unit.set_source_terms(["French source"])
    assert store.findunit("French source") is unit
    unit.set_source_terms([])
    assert store.findunit("French source") is None
    assert store.findid("concept") is unit
    assert None not in store.sourceindex


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("explicit", [False, True])
def test_scalar_target_clear_preserves_terms_and_metadata(namespace, explicit):
    store = parse_terms(namespace)
    unit = store.units[0]
    records = unit.get_target_terms()
    language = unit.target_dom
    term = language.find(f"{unit.namespaced('tig')}/{unit.namespaced('term')}")
    etree.SubElement(term, unit.namespaced("hi")).text = "Inline content"
    if explicit:
        store.settargetlanguage("de")
        unit.settarget(None, lang="ko-KR")
        assert unit.target == "Deutsch"
        store.settargetlanguage("ko-KR")
    else:
        unit.target = None
    assert unit.target_dom is language
    assert unit.target == ""
    assert len(term) == 0
    assert unit.istranslated()
    cleared = unit.get_target_terms()
    assert cleared[0].id == records[0].id
    assert cleared[0].notes == records[0].notes
    assert cleared[1:] == records[1:]
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    assert restored.get_target_terms() == cleared
    unit.target = "Replacement"
    assert unit.get_target_terms()[0].id == records[0].id
    assert unit.get_target_terms()[1:] == records[1:]


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_clear_target_preserves_note_only_language(namespace):
    store = parse_terms(namespace)
    store.settargetlanguage("fr")
    unit = store.units[0]
    unit.set_common_note("French note")
    before = unit.get_target_terms()
    unit.target = None
    assert unit.get_target_terms() == before


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_empty_alternatives_do_not_prevent_obsolescence(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    for language in unit.getlanguageNodes():
        for tig in language.findall(unit.namespaced("tig")):
            etree.SubElement(
                tig, unit.namespaced("termNote"), type="administrativeStatus"
            ).text = "deprecated"
            for status in tig.findall(
                f"{unit.namespaced('termNote')}[@type='administrativeStatus']"
            ):
                status.text = "deprecated"
    assert unit.isobsolete()
    unit.set_target_terms([""], lang="fr")
    assert unit.isobsolete()
    unit.set_target_terms(["Active"], lang="fr")
    assert not unit.isobsolete()
    unit.set_target_terms([""], lang="fr")
    assert unit.isobsolete()
    for term in unit.xmlelement.iter(unit.namespaced("term")):
        term.text = ""
    assert not unit.isobsolete()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("source", [False, True])
def test_common_note_edits_preserve_tbx_content_order(namespace, source):
    store = parse_terms(namespace)
    unit = store.units[0]
    # Validate the structural content models relevant to common notes, including
    # metadata before language sets and metadata before term containers.
    schema = etree.DTD(
        StringIO("""
<!ELEMENT termEntry ((descrip|note)*,langSet+)>
<!ATTLIST termEntry id CDATA #IMPLIED xmlns CDATA #IMPLIED xmlns:xml CDATA #IMPLIED>
<!ELEMENT langSet ((descrip|note)*,tig+)>
<!ATTLIST langSet xml:lang CDATA #REQUIRED>
<!ELEMENT tig (term,(termNote|descrip|note)*)>
<!ATTLIST tig id CDATA #IMPLIED>
<!ELEMENT term (#PCDATA)>
<!ELEMENT termNote (#PCDATA)>
<!ATTLIST termNote type CDATA #IMPLIED>
<!ELEMENT descrip (#PCDATA)>
<!ATTLIST descrip type CDATA #REQUIRED>
<!ELEMENT note (#PCDATA)>
<!ATTLIST note from CDATA #IMPLIED>
""")
    )
    for text in ("First explanation", "Replacement explanation"):
        unit.set_common_note(text, source=source)
        restored = tbxfile.parsestring(
            bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
        ).units[0]
        assert schema.validate(restored.xmlelement), str(schema.error_log)
        notes = restored.get_common_notes(source=source)
        assert text in {note.text for note in notes}
        if text == "Replacement explanation":
            assert "First explanation" not in {note.text for note in notes}


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_new_common_source_note_has_definition_category(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    unit.set_common_note("", source=True)
    unit.set_common_note("New definition", source=True)
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    note = next(
        note
        for note in restored.get_common_notes(source=True)
        if note.text == "New definition"
    )
    assert note.origin == "definition"
    assert note.category == "definition"


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("language_scope", [False, True])
@pytest.mark.parametrize("replacement", ["New definition", ""])
def test_grouped_source_definition_edit(namespace, language_scope, replacement):
    store = parse_terms(namespace)
    unit = store.units[0]
    definition = unit.xmlelement.find(unit.namespaced("descrip"))
    unit.xmlelement.remove(definition)
    parent = unit.source_dom if language_scope else unit.xmlelement
    group = etree.Element(unit.namespaced("descripGrp"))
    parent.insert(0, group)
    group.append(definition)
    etree.SubElement(group, unit.namespaced("note")).text = "Definition reference"
    target_before = etree.tostring(unit.target_dom)
    unit.set_common_note(replacement, source=True)
    assert etree.tostring(unit.target_dom) == target_before
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    groups = restored.xmlelement.findall(f".//{unit.namespaced('descripGrp')}")
    if replacement:
        assert len(groups) == 1
        schema = etree.DTD(
            StringIO("""
<!ELEMENT descripGrp (descrip,note*)>
<!ATTLIST descripGrp xmlns CDATA #IMPLIED xmlns:xml CDATA #IMPLIED>
<!ELEMENT descrip (#PCDATA)>
<!ATTLIST descrip type CDATA #REQUIRED>
<!ELEMENT note (#PCDATA)>
""")
        )
        assert schema.validate(groups[0]), str(schema.error_log)
        notes = restored.get_common_notes(source=True)
        assert any(
            note.text == replacement and note.category == "definition" for note in notes
        )
        assert any(note.text == "Definition reference" for note in notes)
    else:
        assert groups == []
        assert all(
            note.origin != "definition"
            for note in restored.get_common_notes(source=True)
        )


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_unselected_idless_concepts_are_not_indexed_under_none(namespace):
    store = tbxfile.parsestring(
        f"<martif {namespace}><text><body>"
        '<termEntry><langSet xml:lang="de"><tig><term>Eins</term></tig></langSet></termEntry>'
        '<termEntry><langSet xml:lang="de"><tig><term>Zwei</term></tig></langSet></termEntry>'
        "</body></text></martif>",
        sourcelanguage="en",
        targetlanguage="fr",
    )
    assert len(store.units) == 2
    assert all(not unit.isblank() for unit in store.units)
    assert list(store.getids()) == []
    assert store.findid(None) is None
    assert None not in store.sourceindex
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="fr"
    )
    assert len(restored.units) == 2
    assert list(restored.getids()) == []
    first = store.units[0]
    second = store.units[1]
    first.setid("explicit")
    assert store.findid("explicit") is first
    assert list(store.getids()) == ["explicit"]
    store.setsourcelanguage("de")
    assert store.findid("Zwei") is second
    assert set(store.getids()) == {"explicit", "Zwei"}
    store.setsourcelanguage("en")
    assert store.findid("Zwei") is None
    store.removeunit(second)
    assert list(store.getids()) == ["explicit"]


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("source", [False, True])
@pytest.mark.parametrize("scalar", [False, True])
def test_repaired_term_precedes_metadata(namespace, source, scalar):
    unit = parse_terms(namespace).units[0]
    language = unit.source_dom if source else unit.target_dom
    tig = language.find(unit.namespaced("tig"))
    tig.remove(tig.find(unit.namespaced("term")))
    metadata = [etree.tostring(node) for node in tig]
    if scalar:
        for sibling in language.findall(unit.namespaced("tig"))[1:]:
            language.remove(sibling)
        if source:
            unit.source = "Repaired"
        else:
            unit.target = "Repaired"
    else:
        setter = unit.set_source_terms if source else unit.set_target_terms
        records = unit.get_source_terms() if source else unit.get_target_terms()
        setter(["Repaired", *[term.text for term in records[1:]]])
    assert tig[0].tag == unit.namespaced("term")
    assert tig[0].text == "Repaired"
    assert [etree.tostring(node) for node in tig[1:]] == metadata


@pytest.mark.parametrize("empty", [False, True])
def test_empty_id_index_is_built_once_until_mutation(empty):
    store = tbxfile() if empty else parse_terms()
    if not empty:
        store.units[0].xmlelement.attrib.pop("id")
        store.setsourcelanguage("fr")
    with patch.object(store, "makeindex", wraps=store.makeindex) as makeindex:
        for _ in range(3):
            assert list(store.getids()) == []
            assert store.findid("missing") is None
            assert store.findunit("missing") is None
        assert makeindex.call_count == 1
        if empty:
            unit = store.addsourceunit("New source")
        else:
            unit = store.units[0]
            unit.set_source_terms(["New source"])
        assert store.findunit("New source") is unit
        assert makeindex.call_count == 2
        unit.setid("new-id")
        assert store.findid("new-id") is unit
        assert makeindex.call_count == 3


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_source_definition_replacement_keeps_language_scope(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    definition = unit.xmlelement.find(unit.namespaced("descrip"))
    unit.xmlelement.remove(definition)
    unit.source_dom.insert(0, definition)
    targets = unit.get_target_terms()
    unit.set_common_note("English definition", source=True)
    assert definition.getparent() is unit.source_dom
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    note = next(
        note
        for note in restored.get_common_notes(source=True)
        if note.text == "English definition"
    )
    assert note.scope == "language"
    assert restored.get_target_terms() == targets


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_source_language_change_preserves_empty_language_metadata(namespace):
    store = parse_terms(namespace)
    unit = store.units[0]
    language = unit.source_dom
    unit.set_source_terms([])
    etree.SubElement(
        language, unit.namespaced("note"), {"from": "developer"}
    ).text = "Source metadata"
    target = etree.tostring(unit.target_dom)
    unit.setsource("French source", sourcelang="fr")
    store.setsourcelanguage("fr")
    assert unit.source_dom is language
    assert unit.source == "French source"
    assert etree.tostring(unit.target_dom) == target
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="fr", targetlanguage="ko-KR"
    ).units[0]
    assert any(
        note.text == "Source metadata"
        for note in restored.get_common_notes(source=True)
    )


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("explicit", [False, True])
def test_scalar_target_clear_skips_tig_without_term(namespace, explicit):
    store = parse_terms(namespace)
    unit = store.units[0]
    language = unit.target_dom
    leading = etree.Element(unit.namespaced("tig"), id="metadata-only")
    etree.SubElement(leading, unit.namespaced("note")).text = "Retained note"
    language.insert(0, leading)
    leading_before = etree.tostring(leading)
    records = unit.get_target_terms()
    assert unit.target == "하나"
    if explicit:
        store.settargetlanguage("de")
        unit.settarget(None, lang="ko-KR")
        assert unit.target == "Deutsch"
        store.settargetlanguage("ko-KR")
    else:
        unit.target = None
    assert unit.target == ""
    assert etree.tostring(leading) == leading_before
    assert unit.get_target_terms()[2:] == records[2:]
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    assert restored.target == ""
    assert restored.get_target_terms() == unit.get_target_terms()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("source", [False, True])
def test_clear_alternatives_preserves_valid_language(namespace, source):
    store = parse_terms(namespace)
    unit = store.units[0]
    setter = unit.set_source_terms if source else unit.set_target_terms
    language = unit.source_dom if source else unit.target_dom
    notes = unit.get_common_notes(source=source)
    schema = etree.DTD(
        StringIO("""
<!ELEMENT langSet (note*,tig+)>
<!ATTLIST langSet xml:lang CDATA #REQUIRED xmlns CDATA #IMPLIED xmlns:xml CDATA #IMPLIED>
<!ELEMENT note (#PCDATA)>
<!ATTLIST note from CDATA #IMPLIED>
<!ELEMENT tig (term)>
<!ELEMENT term (#PCDATA)>
""")
    )
    for _ in range(2):
        setter([])
        assert schema.validate(language), str(schema.error_log)
        restored = tbxfile.parsestring(
            bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
        ).units[0]
        terms = restored.get_source_terms() if source else restored.get_target_terms()
        assert [term.text for term in terms] == [""]
        assert terms[0].id is None
        assert terms[0].administrative_status is None
        assert restored.get_common_notes(source=source) == notes


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("mode", ["source", "target", "explicit_target"])
def test_scalar_edit_skips_tig_without_term(namespace, mode):
    store = parse_terms(namespace)
    unit = store.units[0]
    source = mode == "source"
    language = unit.source_dom if source else unit.target_dom
    leading = etree.Element(unit.namespaced("tig"), id="metadata-only")
    etree.SubElement(leading, unit.namespaced("note")).text = "Retained note"
    language.insert(0, leading)
    leading_before = etree.tostring(leading)
    records = unit.get_source_terms() if source else unit.get_target_terms()
    if source:
        unit.source = "Updated term"
    elif mode == "explicit_target":
        store.settargetlanguage("de")
        unit.settarget("Updated term", lang="ko-KR")
        assert unit.target == "Deutsch"
    else:
        unit.target = "Updated term"
    assert etree.tostring(leading) == leading_before
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="ko-KR"
    ).units[0]
    assert (restored.source if source else restored.target) == "Updated term"
    terms = restored.get_source_terms() if source else restored.get_target_terms()
    assert len(terms) == len(records)
    assert terms[0] == records[0]
    assert terms[1].id == records[1].id
    assert terms[1].notes == records[1].notes
    assert terms[1].administrative_status == records[1].administrative_status
    assert terms[2:] == records[2:]


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
def test_new_note_language_has_valid_term_container(namespace):
    store = parse_terms(namespace)
    store.settargetlanguage("fr")
    unit = store.units[0]
    unit.set_common_note("French explanation")
    restored = tbxfile.parsestring(
        bytes(store), sourcelanguage="en", targetlanguage="fr"
    ).units[0]
    schema = etree.DTD(
        StringIO("""
<!ELEMENT langSet (note,tig+)>
<!ATTLIST langSet xml:lang CDATA #REQUIRED xmlns CDATA #IMPLIED xmlns:xml CDATA #IMPLIED>
<!ELEMENT note (#PCDATA)>
<!ATTLIST note from CDATA #IMPLIED>
<!ELEMENT tig (term)>
<!ELEMENT term (#PCDATA)>
""")
    )
    assert schema.validate(restored.target_dom), str(schema.error_log)
    assert restored.get_common_notes()[-1].text == "French explanation"
    assert [term.text for term in restored.get_target_terms()] == [""]
    assert not restored.istranslated()


@pytest.mark.parametrize("namespace", ["", 'xmlns="urn:iso:std:iso:30042:ed-2"'])
@pytest.mark.parametrize("clear", [False, True])
def test_empty_source_identities_are_not_indexed(namespace, clear):
    store = parse_terms(namespace)
    unit = store.units[0]
    del unit.xmlelement.attrib["id"]
    assert store.findid("legacy dashboard") is unit
    if clear:
        unit.set_source_terms([])
    else:
        unit.source = ""
    for current in (
        store,
        tbxfile.parsestring(bytes(store), sourcelanguage="en", targetlanguage="ko-KR"),
    ):
        assert len(current.units) == 1
        assert not current.units[0].isblank()
        assert list(current.getids()) == []
        assert current.findid("") is None
        assert current.findunit("") is None
        assert current.findid("legacy dashboard") is None
        assert current.findunit("legacy dashboard") is None
        current.units[0].setid("explicit")
        assert current.findid("explicit") is current.units[0]
        current.units[0].source = "New source"
        assert current.findunit("New source") is current.units[0]
