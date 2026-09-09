"""Editing identities must preserve file content and refresh store lookups."""

from __future__ import annotations

import json

import pytest
from lxml import etree

from translate.misc.multistring import multistring
from translate.storage import (
    aresource,
    base,
    csvl10n,
    dtd,
    fluent,
    jsonl10n,
    php,
    po,
    properties,
    resx,
    tbx,
    tmx,
    toml,
    xliff,
    xliff2,
    yaml,
)


@pytest.mark.parametrize(
    ("store_class", "content", "old_key", "new_key"),
    [
        (jsonl10n.JsonFile, '{"old": "Value", "keep": "Other"}', ".old", ".new"),
        (
            jsonl10n.JsonNestedFile,
            '{"group": {"old": "Value"}, "keep": "Other"}',
            ".group.old",
            ".moved.new",
        ),
        (
            jsonl10n.ARBJsonFile,
            '{"old": "Value", "@old": {"description": "Note"}}',
            "old",
            "new",
        ),
        (
            jsonl10n.WebExtensionJsonFile,
            '{"old": {"message": "Value", "description": "Note"}}',
            "old",
            "new",
        ),
        (yaml.YAMLFile, "old: Value\nkeep: Other\n", "old", "new"),
        (
            yaml.RubyYAMLFile,
            "en:\n  old:\n    one: Value\n    other: Values\n",
            "old",
            "new",
        ),
        (toml.TOMLFile, 'old = "Value"\nkeep = "Other"\n', "old", "new"),
        (
            toml.GoI18nTOMLFile,
            '[old]\none = "Value"\nother = "Values"\n',
            "old",
            "new",
        ),
        (properties.propfile, "# Note\nold=Value\nkeep=Other\n", "old", "new"),
        (
            properties.gwtfile,
            "# Note\nold=Values\nold[one]=Value\nkeep=Other\n",
            "old",
            "new",
        ),
        (
            php.phpfile,
            '<?php\n// Note\n$old = "Value";\n$keep = "Other";\n',
            "$old",
            "$new",
        ),
        (dtd.dtdfile, '<!-- Note -->\n<!ENTITY old "Value">\n', "old", "new"),
        (fluent.FluentFile, "# Note\nold = Value\nkeep = Other\n", "old", "new"),
        (
            aresource.AndroidResourceFile,
            '<resources><string name="old">Value</string><string name="keep">Other</string></resources>',
            "old",
            "new",
        ),
        (
            resx.RESXFile,
            '<root><data name="old"><value>Value</value><comment>Note</comment></data></root>',
            "old",
            "new",
        ),
    ],
)
def test_rename_key_roundtrip(store_class, content, old_key, new_key) -> None:
    store = store_class.parsestring(content)
    unit = store.findid(old_key)
    assert unit is not None
    previous_target = unit.target
    previous_notes = unit.getnotes()
    original_units = list(store.units)
    unit.setid(new_key)
    assert store.findid(old_key) is None
    assert store.findid(new_key) is unit
    assert all(
        left is right for left, right in zip(store.units, original_units, strict=True)
    )
    assert unit.target == previous_target
    assert unit.getnotes() == previous_notes

    reloaded = store_class.parsestring(bytes(store))
    assert reloaded.findid(old_key) is None
    renamed = reloaded.findid(new_key)
    assert renamed is not None
    assert renamed.target == previous_target
    assert renamed.getnotes() == previous_notes
    assert len(reloaded.units) == len(original_units)


@pytest.mark.parametrize("store_class", [jsonl10n.I18NextFile, jsonl10n.I18NextV4File])
def test_rename_json_plurals(store_class) -> None:
    content = (
        '{"old": "Value", "old_plural": "Values"}'
        if store_class is jsonl10n.I18NextFile
        else '{"old_one": "Value", "old_other": "Values"}'
    )
    store = store_class.parsestring(content)
    store.settargetlanguage("en")
    unit = store.units[0]
    old_key = unit.getid()
    assert store.findid(old_key) is unit
    unit.setid(".new")
    assert store.findid(old_key) is None
    assert store.findid(".new") is unit
    result = json.loads(bytes(store))
    assert all(key.startswith("new") for key in result)
    assert set(result.values()) == {"Value", "Values"}


@pytest.mark.parametrize("store_class", [po.pofile, csvl10n.csvfile])
def test_edit_bilingual_source_and_context(store_class) -> None:
    store = store_class()
    unit = store.addsourceunit("Old source")
    unit.target = "Translation"
    unit.addnote("Keep this note")
    unit.setcontext("old context")
    old_id = unit.getid()
    assert store.findid(old_id) is unit
    unit.source = "New source"
    unit.setcontext("new context")
    assert store.findunit("Old source") is None
    assert store.findunit("New source") is unit
    assert store.findid(old_id) is None
    assert store.findid(unit.getid()) is unit
    reloaded = store_class.parsestring(bytes(store))
    renamed = reloaded.findunit("New source")
    assert renamed.target == "Translation"
    assert renamed.getcontext() == "new context"
    assert "Keep this note" in renamed.getnotes()


def test_edit_po_plural_source() -> None:
    store = po.pofile.parsestring(
        'msgid "Old"\nmsgid_plural "Old plural"\nmsgstr[0] "One"\nmsgstr[1] "Many"\n'
    )
    unit = store.findunit("Old")
    unit.source = multistring(["New", "New plural"])
    assert store.findunit("Old") is None
    assert store.findunit("Old plural") is None
    assert store.findunit("New") is unit
    assert store.findunit("New plural") is unit
    reloaded = po.pofile.parsestring(bytes(store))
    assert reloaded.findunit("New").target.strings == ["One", "Many"]


@pytest.mark.parametrize(
    "unit_class", [xliff.xliffunit, xliff2.Xliff2Unit, tmx.tmxunit, tbx.tbxunit]
)
def test_xml_source_preserves_metadata(unit_class) -> None:
    unit = unit_class("Old source")
    unit.target = "Translation"
    source_node = unit.source_dom
    source_node.set("custom", "language metadata")
    text_node = (
        source_node.find(f".//{unit.namespaced(unit.textNode)}")
        if unit.textNode
        else source_node
    )
    text_node.set("custom", "text metadata")
    note = etree.SubElement(unit.xmlelement, unit.namespaced("note"))
    note.text = "Keep note"
    original_target = etree.tostring(unit.target_dom)
    store = base.TranslationStore()
    store.addunit(unit)
    assert store.findunit("Old source") is unit
    unit.source = "New source"
    assert unit.source_dom is source_node
    assert text_node.get("custom") == "text metadata"
    assert note.text == "Keep note"
    assert etree.tostring(unit.target_dom) == original_target
    assert store.findunit("Old source") is None
    assert store.findunit("New source") is unit


@pytest.mark.parametrize(
    "unit_class", [xliff.xliffunit, xliff2.Xliff2Unit, tmx.tmxunit, tbx.tbxunit]
)
def test_xml_noop_source_preserves_inline_content(unit_class) -> None:
    unit = unit_class("Before  ")
    source_node = unit.source_dom
    text_node = (
        source_node.find(f".//{unit.namespaced(unit.textNode)}")
        if unit.textNode
        else source_node
    )
    child = etree.SubElement(text_node, unit.namespaced("hi"))
    child.text = "inline  text"
    child.tail = "  after"
    original = etree.tostring(source_node)
    unit.source = unit.source
    assert etree.tostring(unit.source_dom) == original


def test_remove_renamed_unit_from_index() -> None:
    store = jsonl10n.JsonFile.parsestring('{"old": "Value", "keep": "Other"}')
    unit = store.findid(".old")
    unit.setid(".new")
    assert store.findid(".new") is unit
    store.removeunit(unit)
    assert store.findid(".new") is None
    assert store.findunit("Value") is None
    assert store.findid(".keep") is not None


@pytest.mark.parametrize(
    ("store_class", "content"),
    [
        (yaml.YAMLFile, "old: Value\nkeep: Other\n"),
        (toml.TOMLFile, 'old = "Value"\nkeep = "Other"\n'),
    ],
)
@pytest.mark.parametrize("reuse_key", [False, True])
def test_removed_unit_rename_preserves_former_store(
    store_class, content, reuse_key
) -> None:
    store = store_class.parsestring(content)
    unit = store.findid("old")
    store.removeunit(unit)
    if reuse_key:
        replacement = store.addsourceunit("Replacement")
        replacement.setid("old")
    original = bytes(store)
    unit.setid("new" if reuse_key else "keep")
    assert bytes(store) == original
    assert store.findid("new") is None
    assert store.findid("keep").target == "Other"
    reloaded = store_class.parsestring(bytes(store))
    assert reloaded.findid("new") is None
    if reuse_key:
        assert store.findid("old") is replacement
        assert reloaded.findid("old").target == "Replacement"
    else:
        assert reloaded.findid("old") is None


@pytest.mark.parametrize("store_class", [base.TranslationStore, tmx.tmxfile])
@pytest.mark.parametrize("removed_index", [0, 1])
def test_remove_duplicate_id_preserves_surviving_lookup(
    store_class, removed_index
) -> None:
    store = store_class()
    duplicates = [store.addsourceunit("Duplicate") for _ in range(2)]
    duplicates[0].target = "First translation"
    duplicates[1].target = "Second translation"
    other = store.addsourceunit("Other")
    assert store.findid("Duplicate") is duplicates[1]
    store.removeunit(duplicates[removed_index])
    survivor = duplicates[1 - removed_index]
    assert store.findid("Other") is other
    assert store.findid("Duplicate") is survivor
    assert store.findunits("Duplicate") == [survivor]


@pytest.mark.parametrize("store_class", [xliff.xlifffile, xliff2.Xliff2File])
def test_rich_source_edit_refreshes_lookup(store_class) -> None:
    store = store_class()
    unit = store.addsourceunit("Old source")
    unit.target = "Translation"
    unit.setid("source-id")
    unit_id = unit.getid()
    assert store.findunit("Old source") is unit
    replacement = store_class.UnitClass("New source")
    inline = etree.SubElement(replacement.source_dom, replacement.namespaced("ph"))
    inline.set("id", "placeholder")
    unit.rich_source = replacement.rich_source
    assert store.findunit("Old source") is None
    assert store.findunit(unit.source) is unit
    assert store.findid(unit_id) is unit
    reloaded = store_class.parsestring(bytes(store))
    edited = reloaded.findunit(unit.source)
    assert edited.target == "Translation"
    assert edited.source_dom.find(edited.namespaced("ph")).get("id") == "placeholder"


@pytest.mark.parametrize(
    ("store_class", "content", "old_key", "new_key"),
    [
        (
            yaml.YAMLFile,
            'group:\n  # Before\n  old: "Value" # Inline\n  keep: Other\n',
            "group->old",
            "group->new",
        ),
        (
            toml.TOMLFile,
            '[group]\n# Before\nold = "Value" # Inline\nkeep = "Other"\n',
            "group.old",
            "group.new",
        ),
    ],
)
def test_retained_document_rename_preserves_formatting(
    store_class, content, old_key, new_key
) -> None:
    store = store_class.parsestring(content)
    unit = store.findid(old_key)
    assert unit is not None
    unit.setid(new_key)
    assert bytes(store).decode() == content.replace("old", "new")
    unit.setid(old_key)
    assert bytes(store).decode() == content
    unit.setid(old_key)
    assert bytes(store).decode() == content


@pytest.mark.parametrize(
    ("store_class", "content", "new_key"),
    [
        (yaml.YAMLFile, "old: Value\nkeep: Other\n", "keep"),
        (toml.TOMLFile, 'old = "Value"\nkeep = "Other"\n', "keep"),
        (yaml.YAMLFile, "old: Value\nkeep: Other\n", "group->new"),
        (toml.TOMLFile, 'old = "Value"\nkeep = "Other"\n', ".group.new"),
    ],
)
def test_retained_document_rejects_unsafe_rename(store_class, content, new_key) -> None:
    store = store_class.parsestring(content)
    unit = store.findid("old")
    original = bytes(store)
    with pytest.raises(ValueError):
        unit.setid(new_key)
    assert unit.getid() == "old"
    assert store.findid("old") is unit
    assert bytes(store) == original


@pytest.mark.parametrize("store_class", [yaml.YAMLFile, toml.TOMLFile])
def test_new_cached_document_unit_can_get_key(store_class) -> None:
    store = store_class()
    unit = store.addsourceunit("Value")
    unit.setid("new")
    assert store.findid("new") is unit
    assert store_class.parsestring(bytes(store)).findid("new").target == "Value"


@pytest.mark.parametrize(
    ("store_class", "content", "key"),
    [
        (yaml.YAMLFile, "existing: Original\n", "existing"),
        (yaml.YAMLFile, "group:\n  existing: Original\n", "group->existing"),
        (toml.TOMLFile, 'existing = "Original"\n', "existing"),
        (toml.TOMLFile, '[group]\nexisting = "Original"\n', "group.existing"),
    ],
)
@pytest.mark.parametrize("serialized", [False, True])
def test_new_retained_document_unit_rejects_collision(
    store_class, content, key, serialized
) -> None:
    if serialized:
        store = store_class.parsestring(content)
        existing = store.findid(key)
    else:
        store = store_class()
        existing = store.addsourceunit("Original")
        existing.setid(key)
    unit = store.addsourceunit("Replacement")
    original_id = unit.getid()
    with pytest.raises(ValueError, match="Key already exists"):
        unit.setid(key)
    assert unit.getid() == original_id
    assert store.findid(key) is existing
    assert existing.target == "Original"
    unit.setid("different")
    reloaded = store_class.parsestring(bytes(store))
    assert reloaded.findid(key).target == "Original"
    assert reloaded.findid("different").target == "Replacement"


@pytest.mark.parametrize(
    ("store_class", "content"),
    [
        (yaml.YAMLFile, "existing: {}\n"),
        (toml.TOMLFile, "[existing]\n"),
    ],
)
def test_new_retained_document_unit_rejects_nonunit_collision(
    store_class, content
) -> None:
    store = store_class.parsestring(content)
    assert store.findid("existing") is None
    unit = store.addsourceunit("Replacement")
    original_id = unit.getid()
    with pytest.raises(ValueError, match="Key already exists"):
        unit.setid("existing")
    assert unit.getid() == original_id


@pytest.mark.parametrize(
    ("store_class", "content"),
    [
        (yaml.YAMLFile, "values: [Value, Other]\n"),
        (toml.TOMLFile, 'values = ["Value", "Other"]\n'),
    ],
)
def test_retained_document_rejects_array_item_rename(store_class, content) -> None:
    store = store_class.parsestring(content)
    unit = store.findunit("Value")
    old_key = unit.getid()
    original = bytes(store)
    with pytest.raises(ValueError, match="same mapping"):
        unit.setid("new")
    assert store.findid(old_key) is unit
    assert bytes(store) == original


@pytest.mark.parametrize(
    "store_class", [xliff.xlifffile, xliff2.Xliff2File, tbx.tbxfile]
)
def test_xml_key_and_source_roundtrip(store_class) -> None:
    store = store_class()
    unit = store.addsourceunit("Old source")
    unit.target = "Translation"
    unit.setid("old")
    unit.addnote("Keep note")
    store = store_class.parsestring(bytes(store))
    unit = store.findunit("Old source")
    old_key = unit.getid()
    unit.setid("new")
    unit.source = "New source"
    assert store.findid(old_key) is None
    assert store.findunit("Old source") is None
    assert store.findunit("New source") is unit
    reloaded = store_class.parsestring(bytes(store))
    unit = reloaded.findunit("New source")
    assert unit.target == "Translation"
    assert "Keep note" in unit.getnotes()
    assert reloaded.findid(old_key) is None


@pytest.mark.parametrize("keep_other", [False, True])
def test_removing_unit_invalidates_tmx_language_index(keep_other):
    store = tmx.tmxfile(sourcelanguage="en", targetlanguage="fr")
    unit = store.addsourceunit("Source")
    unit.target = "Translation"
    if keep_other:
        other = store.addsourceunit("Other")
        other.target = "Other translation"
    assert store.translate("Source", sourcelang="en", targetlang="fr") == "Translation"
    store.removeunit(unit)
    assert store.translate("Source", sourcelang="en", targetlang="fr") is None
    assert store.translate("Translation", sourcelang="fr", targetlang="en") is None
    if keep_other:
        assert (
            store.translate("Other", sourcelang="en", targetlang="fr")
            == "Other translation"
        )
