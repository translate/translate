"""Tests for Apple XLIFF format with plural support."""

from __future__ import annotations

from translate.misc.multistring import multistring
from translate.storage import applestrings_xliff

from . import test_xliff

# ---------------------------------------------------------------------------
# Shared XLIFF snippets used across several tests
# ---------------------------------------------------------------------------

_SINGULAR_XLIFF = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="greeting" xml:space="preserve">
        <source>Hello</source>
        <target>Hello</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

# Based on Apple's documented XLIFF editing example:
# https://developer.apple.com/documentation/xcode/editing-xliff-and-string-catalog-files
_APPLE_WORKFLOW_XLIFF = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="de" datatype="plaintext">
    <body>
      <trans-unit id="greeting" xml:space="preserve">
        <source>Hello, world!</source>
        <target>Hallo, Welt!</target>
        <note>A friendly greeting.</note>
      </trans-unit>
      <trans-unit id="missing-target" xml:space="preserve">
        <source>Missing target</source>
      </trans-unit>
      <trans-unit id="empty-target" xml:space="preserve">
        <source>Empty target</source>
        <target></target>
      </trans-unit>
      <trans-unit id="explicit-state" xml:space="preserve">
        <source>Explicit state</source>
        <target state="needs-review-translation" state-qualifier="leveraged-mt">Expliziter Status</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

_BASIC_PLURAL_XLIFF = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="items:count:dict" xml:space="preserve">
        <source>NSStringPluralRuleType</source>
        <target>NSStringPluralRuleType</target>
      </trans-unit>
      <trans-unit id="items:count:dict/:string" xml:space="preserve">
        <source>d</source>
        <target>d</target>
      </trans-unit>
      <trans-unit id="items:count:dict/one:dict/:string" xml:space="preserve">
        <source>One item</source>
        <target>One item</target>
      </trans-unit>
      <trans-unit id="items:count:dict/other:dict/:string" xml:space="preserve">
        <source>%d items</source>
        <target>%d items</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""


def _add_plural(
    store: applestrings_xliff.AppleStringsXliffFile,
    base_key: str,
    target_strings: list,
    format_value_type: str = "d",
    source_strings: list | None = None,
) -> applestrings_xliff.AppleStringsXliffUnit:
    """
    Add a plural unit using the standard store API.

    :param store:              An AppleStringsXliffFile instance.
    :param base_key:           Logical key (e.g. ``"items:count"``).
    :param target_strings:     List/multistring of target plural forms.
    :param format_value_type:  NSStringFormatValueTypeKey value (e.g. ``"d"``).
    :param source_strings:     Optional source forms; defaults to *target_strings*.
    :returns:                  The created :class:`AppleStringsXliffUnit`.
    """
    if source_strings is None:
        source_strings = target_strings
    filenames = store.getfilenames()
    filename = filenames[0] if filenames else "NoName"
    unit = store.addsourceunit(
        multistring(list(source_strings)), filename=filename, createifmissing=True
    )
    unit.target = multistring(list(target_strings))
    unit.setid(base_key)
    unit.format_value_type = format_value_type
    return unit


# ---------------------------------------------------------------------------
# Unit-level tests
# ---------------------------------------------------------------------------


class TestAppleStringsXliffUnit(test_xliff.TestXLIFFUnit):
    """Tests for AppleStringsXliffUnit."""

    UnitClass = applestrings_xliff.AppleStringsXliffUnit
    StoreClass = applestrings_xliff.AppleStringsXliffFile


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------


class TestAppleStringsXliffFile(test_xliff.TestXLIFFfile):
    """Tests for AppleStringsXliffFile."""

    StoreClass = applestrings_xliff.AppleStringsXliffFile
    translated_unit_attributes = ""
    translated_target_attributes = ""
    fuzzy_without_target_attribute = ""

    # ------------------------------------------------------------------
    # Basic parsing
    # ------------------------------------------------------------------

    def test_parse_basic_string(self):
        """A basic non-plural string is parsed as a single regular unit."""
        store = self.StoreClass()
        store.parse(_SINGULAR_XLIFF)

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "Hello"
        assert unit.target == "Hello"
        assert not unit.hasplural()

    def test_parse_apple_workflow(self):
        """Apple targets and bare developer notes have implicit semantics."""
        store = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF)
        greeting, missing_target, empty_target, explicit_state = store.units

        assert greeting.get_state_n() == greeting.S_TRANSLATED
        assert greeting.isapproved()
        assert not greeting.isfuzzy()
        assert greeting.getnotes() == "A friendly greeting."
        assert greeting.getnotes(origin="developer") == "A friendly greeting."

        assert missing_target.get_state_n() == missing_target.S_UNTRANSLATED
        assert not missing_target.isapproved()
        assert not missing_target.isfuzzy()

        assert empty_target.get_state_n() == empty_target.S_UNTRANSLATED
        assert not empty_target.isapproved()
        assert not empty_target.isfuzzy()

        assert explicit_state.get_state_n() == explicit_state.S_NEEDS_REVIEW
        assert not explicit_state.isapproved()
        assert explicit_state.isfuzzy()

    def test_whitespace_target_inherits_unit_xml_space(self):
        """Whitespace-only targets respect xml:space on the trans-unit."""
        content = _APPLE_WORKFLOW_XLIFF.replace(
            b"<target>Hallo, Welt!</target>",
            b"<target>   </target>",
        )
        greeting = self.StoreClass.parsestring(content).units[0]

        assert greeting.target == "   "
        assert greeting.get_state_n() == greeting.S_TRANSLATED
        assert greeting.isapproved()
        assert greeting.istranslated()
        assert not greeting.isfuzzy()

    def test_apple_workflow_serialization(self):
        """Apple metadata round-trips without synthesized XLIFF attributes."""
        store = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF)
        greeting = store.units[0]

        greeting.target = "Guten Tag!"
        greeting.addnote("Shown to translators.", origin="developer")
        greeting.addnote("Internal note.", origin="translator")

        serialized = bytes(store)
        reparsed = self.StoreClass.parsestring(serialized)
        greeting = reparsed.units[0]
        explicit_state = reparsed.units[3]

        assert "approved" not in greeting.xmlelement.attrib
        assert "state" not in greeting.get_target_dom().attrib
        assert greeting.getnotes(origin="developer") == (
            "A friendly greeting.\nShown to translators."
        )
        assert greeting.getnotes(origin="translator") == "Internal note."

        note_nodes = list(
            greeting.xmlelement.iterdescendants(greeting.namespaced("note"))
        )
        assert [note.get("from") for note in note_nodes] == [
            None,
            None,
            "translator",
        ]

        explicit_target = explicit_state.get_target_dom()
        assert explicit_target.get("state") == "needs-review-translation"
        assert explicit_target.get("state-qualifier") == "leveraged-mt"

    def test_apple_state_transitions(self):
        """Explicit workflow transitions remain observable without approval tags."""
        store = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF)
        greeting = store.units[0]
        target = greeting.get_target_dom()

        greeting.set_state_n(greeting.S_UNTRANSLATED)
        assert target.get("state") == "new"
        assert greeting.get_state_n() == greeting.S_UNTRANSLATED
        assert not greeting.isapproved()

        greeting.markapproved()
        assert target.get("state") == "translated"
        assert greeting.isapproved()

        greeting.markapproved(False)
        assert target.get("state") == "needs-review-translation"
        assert not greeting.isapproved()
        assert greeting.isfuzzy()
        assert "approved" not in greeting.xmlelement.attrib

    def test_state_transition_creates_missing_singular_target(self):
        """A singular state transition persists without an existing target."""
        store = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF)
        missing_target = store.units[1]
        assert missing_target.get_target_dom() is None

        missing_target.markapproved()

        target = missing_target.get_target_dom()
        assert target is not None
        assert target.get("state") == "translated"
        assert missing_target.get_state_n() == missing_target.S_TRANSLATED
        assert missing_target.isapproved()

        reparsed = self.StoreClass.parsestring(bytes(store)).units[1]
        assert reparsed.get_target_dom() is not None
        assert reparsed.get_state_n() == reparsed.S_TRANSLATED
        assert reparsed.isapproved()

    def test_state_transition_removes_generic_approval(self):
        """Apple target state does not conflict with generic approval metadata."""
        content = _APPLE_WORKFLOW_XLIFF.replace(
            b'<trans-unit id="greeting"',
            b'<trans-unit id="greeting" approved="yes"',
        )
        store = self.StoreClass.parsestring(content)
        greeting = store.units[0]
        assert greeting.xmlelement.get("approved") == "yes"

        greeting.markapproved(False)

        assert "approved" not in greeting.xmlelement.attrib
        assert greeting.get_target_dom().get("state") == "needs-review-translation"
        serialized = bytes(store)
        assert b"approved=" not in serialized

        reparsed = self.StoreClass.parsestring(serialized).units[0]
        assert reparsed.get_state_n() == reparsed.S_NEEDS_REVIEW
        assert not reparsed.isapproved()

    def test_exact_xliff_states_are_preserved(self):
        """Setting an exact numeric state does not collapse XLIFF variants."""
        greeting = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF).units[0]
        target = greeting.get_target_dom()

        for xml_state, state_n in greeting.statemap.items():
            if xml_state == "new":
                continue
            target.set("state", xml_state)
            assert greeting.get_state_n() == state_n

            greeting.set_state_n(greeting.get_state_n())

            assert target.get("state") == xml_state

    def test_remove_bare_developer_notes(self):
        store = self.StoreClass.parsestring(_APPLE_WORKFLOW_XLIFF)
        greeting = store.units[0]
        greeting.addnote("Internal note.", origin="translator")
        greeting.addnote(
            "Replacement developer note.",
            origin="developer",
            position="replace",
        )

        assert greeting.getnotes(origin="developer") == "Replacement developer note."
        assert greeting.getnotes(origin="translator") == "Internal note."

        greeting.removenotes(origin="developer")

        assert greeting.getnotes() == "Internal note."

    def test_parse_apple_plural_basic(self):
        """Plurals are folded into one unit with a multistring source/target."""
        store = self.StoreClass()
        store.parse(_BASIC_PLURAL_XLIFF)

        # The four raw trans-units are folded into a single plural unit
        assert len(store.units) == 1

        unit = store.units[0]
        assert unit.hasplural()
        assert unit.format_value_type == "d"
        assert unit._plural_base_key == "items:count"

        # source and target are multistrings (zero, one, other for English)
        assert isinstance(unit.source, multistring)
        assert isinstance(unit.target, multistring)
        assert unit.source.strings[1] == "One item"  # 'one' form
        assert unit.source.strings[2] == "%d items"  # 'other' form
        assert unit.target.strings[1] == "One item"
        assert unit.target.strings[2] == "%d items"

    def test_plural_state_aggregation_and_propagation(self):
        """Folded plurals expose and update their least-complete form state."""
        content = _BASIC_PLURAL_XLIFF.replace(
            b"<target>One item</target>",
            b'<target state="needs-review-translation">One item</target>',
        )
        store = self.StoreClass.parsestring(content)
        unit = store.units[0]

        assert unit.get_state_n() == unit.S_NEEDS_REVIEW
        assert not unit.isapproved()
        assert unit.isfuzzy()

        unit.markapproved()
        assert unit.get_state_n() == unit.S_TRANSLATED
        assert unit.isapproved()
        assert bytes(store).count(b'state="translated"') == 2

        unit.markapproved(False)
        assert unit.get_state_n() == unit.S_NEEDS_REVIEW
        assert not unit.isapproved()
        assert bytes(store).count(b'state="needs-review-translation"') == 2

        unit.set_state_n(unit.S_UNTRANSLATED)
        assert unit.get_state_n() == unit.S_UNTRANSLATED
        assert bytes(store).count(b'state="new"') == 2

        unit.markapproved(False)
        unit.target = multistring(["", "One translated item", "%d translated items"])
        serialized = bytes(store)
        assert serialized.count(b'state="needs-review-translation"') == 2

        reparsed = self.StoreClass.parsestring(serialized)
        assert reparsed.units[0].get_state_n() == unit.S_NEEDS_REVIEW

    def test_dirty_plural_state_uses_in_memory_targets(self):
        """Plural state changes immediately when implicit target forms are edited."""
        store = self.StoreClass.parsestring(_BASIC_PLURAL_XLIFF)
        unit = store.units[0]

        unit.target = multistring(["", "", "%d items"])

        assert unit.get_state_n() == unit.S_UNTRANSLATED
        assert not unit.isapproved()
        assert not unit.istranslated()
        assert unit.isfuzzy()

        unit.target = multistring(["", "One translated item", "%d items"])

        assert unit.get_state_n() == unit.S_TRANSLATED
        assert unit.isapproved()
        assert unit.istranslated()
        assert not unit.isfuzzy()

    def test_dirty_empty_plural_ignores_stale_translated_state(self):
        """Clearing a form supersedes its old explicit translated state."""
        content = _BASIC_PLURAL_XLIFF.replace(
            b"<target>One item</target>",
            b'<target state="translated">One item</target>',
        ).replace(
            b"<target>%d items</target>",
            b'<target state="translated">%d items</target>',
        )
        store = self.StoreClass.parsestring(content)
        unit = store.units[0]
        assert unit.get_state_n() == unit.S_TRANSLATED

        unit.target = multistring(["", "", "%d items"])

        assert unit.get_state_n() == unit.S_UNTRANSLATED
        assert not unit.isapproved()
        assert not unit.istranslated()
        assert unit.isfuzzy()

        serialized = bytes(store)
        assert serialized.count(b'state="translated"') == 1
        reparsed = self.StoreClass.parsestring(serialized).units[0]
        assert reparsed.get_state_n() == reparsed.S_UNTRANSLATED
        assert not reparsed.isapproved()

    def test_plural_target_edit_clears_state_override(self):
        """Editing targets invalidates an earlier plural-wide transition."""
        store = self.StoreClass.parsestring(_BASIC_PLURAL_XLIFF)
        unit = store.units[0]
        unit.markapproved()
        assert unit._plural_state_override == unit.S_TRANSLATED

        unit.target = multistring(["", "", "%d items"])

        assert unit._plural_state_override is None
        assert unit.get_state_n() == unit.S_UNTRANSLATED
        assert not unit.isapproved()
        assert not unit.istranslated()

        serialized = bytes(store)
        assert serialized.count(b'state="translated"') == 1
        reparsed = self.StoreClass.parsestring(serialized).units[0]
        assert reparsed.get_state_n() == reparsed.S_UNTRANSLATED

    def test_dirty_plural_preserves_unchanged_empty_form_state(self):
        """Editing another form retains state metadata on an empty target."""
        content = _BASIC_PLURAL_XLIFF.replace(
            b"<target>One item</target>",
            b'<target state="needs-review-translation"></target>',
        )
        store = self.StoreClass.parsestring(content)
        unit = store.units[0]
        assert unit.get_state_n() == unit.S_NEEDS_REVIEW

        unit.target = multistring(["", "", "%d translated items"])

        assert unit._plural_dirty_targets == {"other"}
        assert unit.get_state_n() == unit.S_NEEDS_REVIEW
        serialized = bytes(store)
        assert serialized.count(b'state="needs-review-translation"') == 1

        reparsed = self.StoreClass.parsestring(serialized).units[0]
        assert reparsed.get_state_n() == reparsed.S_NEEDS_REVIEW

    def test_new_plural_state_derives_target_tags(self):
        """New plural state evaluates each required in-memory target form."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = _add_plural(
            store,
            "items:count",
            ["", "", "%d items"],
            source_strings=["", "One item", "%d items"],
        )
        assert unit._plural_tags == []

        assert unit.get_state_n() == unit.S_UNTRANSLATED
        assert not unit.isapproved()
        assert not unit.istranslated()
        assert unit.isfuzzy()

    def test_plural_state_transition_creates_missing_targets(self):
        """A plural state transition persists when form targets are absent."""
        content = _BASIC_PLURAL_XLIFF.replace(
            b"        <target>One item</target>\n",
            b"",
        ).replace(
            b"        <target>%d items</target>\n",
            b"",
        )
        store = self.StoreClass.parsestring(content)
        unit = store.units[0]
        assert all(
            next(form.iterchildren(unit.namespaced("target")), None) is None
            for form in unit._plural_forms.values()
        )

        unit.markapproved()

        assert unit._plural_dirty
        serialized = bytes(store)
        assert serialized.count(b'state="translated"') == 2

        reparsed = self.StoreClass.parsestring(serialized).units[0]
        assert reparsed.get_state_n() == reparsed.S_TRANSLATED
        assert reparsed.isapproved()

    def test_dirty_plural_preserves_per_form_state(self):
        """Rebuilding edited forms retains each form's exact explicit state."""
        content = _BASIC_PLURAL_XLIFF.replace(
            b"<target>One item</target>",
            b'<target state="needs-review-adaptation" '
            b'state-qualifier="leveraged-mt">One item</target>',
        )
        store = self.StoreClass.parsestring(content)
        unit = store.units[0]

        unit.target = multistring(["", "One translated item", "%d translated items"])
        serialized = bytes(store)

        assert serialized.count(b'state="needs-review-adaptation"') == 1
        assert serialized.count(b'state-qualifier="leveraged-mt"') == 1
        assert serialized.count(b" state=") == 1
        reparsed = self.StoreClass.parsestring(serialized)
        assert (
            reparsed.units[0].get_state_n() == unit.statemap["needs-review-adaptation"]
        )
        one_target = next(
            reparsed.units[0]
            ._plural_forms["one"]
            .iterchildren(reparsed.units[0].namespaced("target"))
        )
        assert one_target.get("state-qualifier") == "leveraged-mt"

    def test_plural_state_uses_folded_form_index(self, monkeypatch):
        """State reads and writes do not rescan the containing XML body."""
        store = self.StoreClass.parsestring(_BASIC_PLURAL_XLIFF)
        unit = store.units[0]
        assert set(unit._plural_forms) == {"one", "other"}

        def fail_on_scan(*args):
            raise AssertionError("plural state rescanned the XML body")

        monkeypatch.setattr(
            self.StoreClass,
            "_is_plural_form_sibling",
            fail_on_scan,
        )

        assert unit.get_state_n() == unit.S_TRANSLATED
        unit.markapproved(False)
        assert unit.get_state_n() == unit.S_NEEDS_REVIEW

    def test_parse_apple_plural_complex(self):
        """Each plural group becomes one unit; regular units are preserved."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="shopping-list" xml:space="preserve">
        <source>%1$#@apple@ and %2$#@orange@.</source>
        <target>%1$#@apple@ and %2$#@orange@.</target>
      </trans-unit>
      <trans-unit id="shopping-list:apple:dict" xml:space="preserve">
        <source>NSStringPluralRuleType</source>
        <target>NSStringPluralRuleType</target>
      </trans-unit>
      <trans-unit id="shopping-list:apple:dict/:string" xml:space="preserve">
        <source>d</source>
        <target>d</target>
      </trans-unit>
      <trans-unit id="shopping-list:apple:dict/one:dict/:string" xml:space="preserve">
        <source>One apple</source>
        <target>One apple</target>
      </trans-unit>
      <trans-unit id="shopping-list:apple:dict/other:dict/:string" xml:space="preserve">
        <source>%d apples</source>
        <target>%d apples</target>
      </trans-unit>
      <trans-unit id="shopping-list:orange:dict" xml:space="preserve">
        <source>NSStringPluralRuleType</source>
        <target>NSStringPluralRuleType</target>
      </trans-unit>
      <trans-unit id="shopping-list:orange:dict/:string" xml:space="preserve">
        <source>d</source>
        <target>d</target>
      </trans-unit>
      <trans-unit id="shopping-list:orange:dict/zero:dict/:string" xml:space="preserve">
        <source>no oranges</source>
        <target>no oranges</target>
      </trans-unit>
      <trans-unit id="shopping-list:orange:dict/one:dict/:string" xml:space="preserve">
        <source>one orange</source>
        <target>one orange</target>
      </trans-unit>
      <trans-unit id="shopping-list:orange:dict/other:dict/:string" xml:space="preserve">
        <source>%d oranges</source>
        <target>%d oranges</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(xliff_content)

        # 1 regular string + 2 plural groups = 3 units
        assert len(store.units) == 3

        # The regular format string is kept as-is
        assert store.units[0].source == "%1$#@apple@ and %2$#@orange@."
        assert not store.units[0].hasplural()

        # apple group
        apple = store.units[1]
        assert apple.hasplural()
        assert apple._plural_base_key == "shopping-list:apple"
        assert apple.format_value_type == "d"
        assert apple.target.strings[1] == "One apple"  # 'one'
        assert apple.target.strings[2] == "%d apples"  # 'other'

        # orange group
        orange = store.units[2]
        assert orange.hasplural()
        assert orange._plural_base_key == "shopping-list:orange"
        assert orange.target.strings[0] == "no oranges"  # 'zero'
        assert orange.target.strings[1] == "one orange"  # 'one'
        assert orange.target.strings[2] == "%d oranges"  # 'other'

    # ------------------------------------------------------------------
    # getid / setid
    # ------------------------------------------------------------------

    def test_plural_unit_getid(self):
        """getid() on a parsed plural unit returns filename + ID_SEPARATOR + base_key."""
        store = self.StoreClass()
        store.parse(_BASIC_PLURAL_XLIFF)

        unit = store.units[0]
        assert unit.hasplural()
        # The ID should end with the base key (not the XML ":dict" suffix)
        assert unit.getid().endswith("items:count")
        assert unit.getid() == "Localizable.strings\x04items:count"

    def test_plural_unit_setid(self):
        """setid() on a plural unit updates the base key, XML id, and marks dirty."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = _add_plural(store, "items:count", ["", "One item", "%d items"])

        # Initial state
        assert unit._plural_base_key == "items:count"
        assert unit.xmlelement.get("id") == "items:count:dict"
        assert unit.getid().endswith("items:count")

        # Change the logical ID
        unit.setid("widgets:count")
        assert unit._plural_base_key == "widgets:count"
        assert unit.xmlelement.get("id") == "widgets:count:dict"
        assert unit.getid().endswith("widgets:count")
        assert unit._plural_dirty

    def test_regular_unit_setid(self):
        """setid() on a regular unit behaves like the parent class."""
        store = self.StoreClass()
        store.parse(_SINGULAR_XLIFF)

        unit = store.units[0]
        assert not unit.hasplural()
        unit.setid("farewell")
        assert unit.xmlelement.get("id") == "farewell"
        assert unit.getid().endswith("farewell")

    # ------------------------------------------------------------------
    # Adding plural units using the standard API
    # ------------------------------------------------------------------

    def test_add_plural_unit_standard_api(self):
        """Plural units are added via addsourceunit + multistring + setid."""
        store = self.StoreClass()
        store.settargetlanguage("en")

        unit = _add_plural(store, "items:count", ["", "One item", "%d items"])

        assert len(store.units) == 1
        assert unit.hasplural()
        assert unit._plural_base_key == "items:count"
        assert unit.format_value_type == "d"
        assert unit.target.strings[1] == "One item"
        assert unit.target.strings[2] == "%d items"

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def test_serialize_plural_roundtrip(self):
        """Parse → serialize → parse produces identical plural content."""
        store = self.StoreClass()
        store.parse(_BASIC_PLURAL_XLIFF)
        output = bytes(store)

        store2 = self.StoreClass()
        store2.parse(output)

        assert len(store2.units) == 1
        unit = store2.units[0]
        assert unit.hasplural()
        assert unit.target.strings[1] == "One item"
        assert unit.target.strings[2] == "%d items"

    def test_serialize_plural_xml_structure(self):
        """The serialised XML contains the Apple XLIFF plural trans-unit structure."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        _add_plural(store, "items:count", ["", "One item", "%d items"])

        output = bytes(store).decode("utf-8")

        assert 'id="items:count:dict"' in output
        assert "<source>NSStringPluralRuleType</source>" in output

        assert 'id="items:count:dict/:string"' in output
        assert "<source>d</source>" in output

        assert 'id="items:count:dict/one:dict/:string"' in output
        assert "<source>One item</source>" in output

        assert 'id="items:count:dict/other:dict/:string"' in output
        assert "<source>%d items</source>" in output

        # zero form was empty → should be absent
        assert 'id="items:count:dict/zero:dict/:string"' not in output

    def test_serialize_plural_all_forms(self):
        """All three English plural forms are serialised when provided."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        _add_plural(store, "items:count", ["No items", "One item", "%d items"])

        output = bytes(store).decode("utf-8")

        assert 'id="items:count:dict/zero:dict/:string"' in output
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert 'id="items:count:dict/other:dict/:string"' in output
        assert "<source>No items</source>" in output
        assert "<source>One item</source>" in output
        assert "<source>%d items</source>" in output

    def test_unknown_language_single_plural_uses_other(self):
        """A single plural form for unknown CLDR data writes the other category."""
        store = self.StoreClass()
        store.settargetlanguage("tok")
        _add_plural(store, "items:count", ["the only form"])

        output = bytes(store).decode("utf-8")
        assert 'id="items:count:dict/other:dict/:string"' in output
        assert 'id="items:count:dict/one:dict/:string"' not in output
        assert 'id="items:count:dict/zero:dict/:string"' not in output

    def test_unknown_language_two_plurals_use_zero_and_other(self):
        """Two plural forms for unknown CLDR data write zero and other."""
        store = self.StoreClass()
        store.settargetlanguage("tok")
        _add_plural(store, "items:count", ["No items", "%d items"])

        output = bytes(store).decode("utf-8")
        assert 'id="items:count:dict/zero:dict/:string"' in output
        assert 'id="items:count:dict/other:dict/:string"' in output
        assert 'id="items:count:dict/one:dict/:string"' not in output
        assert "<source>No items</source>" in output
        assert "<source>%d items</source>" in output

    # ------------------------------------------------------------------
    # Conversion: singular → plural
    # ------------------------------------------------------------------

    def test_singular_to_plural_by_multistring_assignment(self):
        """A regular unit is converted to a plural unit by assigning a multistring."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_SINGULAR_XLIFF)

        unit = store.units[0]
        assert not unit.hasplural()
        assert unit.source == "Hello"

        # Convert to plural
        unit.source = multistring(["", "One item", "%d items"])
        unit.target = multistring(["", "Jeden Artikel", "%d Artikel"])
        unit.setid("items:count")
        unit.format_value_type = "d"

        assert unit.hasplural()
        assert unit._plural_base_key == "items:count"
        assert unit.target.strings[1] == "Jeden Artikel"
        assert unit.target.strings[2] == "%d Artikel"

        # Serialise – the XML must have the full Apple XLIFF plural structure
        output = bytes(store).decode("utf-8")
        assert 'id="items:count:dict"' in output
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert "Jeden Artikel" in output

        # Round-trip
        store2 = self.StoreClass()
        store2.settargetlanguage("en")
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 1
        assert store2.units[0].hasplural()
        assert store2.units[0].target.strings[1] == "Jeden Artikel"

    # ------------------------------------------------------------------
    # Conversion: plural → singular
    # ------------------------------------------------------------------

    def test_plural_to_singular_by_string_assignment(self):
        """Assigning a plain string clears the plural state of a unit."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_BASIC_PLURAL_XLIFF)

        unit = store.units[0]
        assert unit.hasplural()

        # Convert to singular
        unit.source = "Item count"
        unit.target = "Anzahl der Objekte"

        assert not unit.hasplural()
        assert unit.source == "Item count"
        assert unit.target == "Anzahl der Objekte"

    def test_plural_to_singular_full_roundtrip(self):
        """A plural-to-singular conversion serialises cleanly."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_BASIC_PLURAL_XLIFF)

        unit = store.units[0]
        assert unit.hasplural()

        # Convert to singular: clear plural state then fix the id
        unit.source = "Item count"
        unit.target = "Anzahl"
        unit.setid("items_label")  # clears _plural_base_key, removes stale elements

        output = bytes(store).decode("utf-8")
        assert 'id="items_label"' in output
        assert "<source>Item count</source>" in output
        assert "Anzahl" in output
        # stale plural XML elements must be gone
        assert "items:count:dict/:string" not in output
        assert "one:dict/:string" not in output

        # Round-trip
        store2 = self.StoreClass()
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 1
        assert not store2.units[0].hasplural()
        assert store2.units[0].target == "Anzahl"

    # ------------------------------------------------------------------
    # remove_plural_unit / removeunit
    # ------------------------------------------------------------------

    def test_remove_plural_unit(self):
        """removeunit() on a plural unit removes it and its sibling XML elements."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        _add_plural(store, "items:count", ["", "One item", "%d items"])
        _add_plural(store, "orders:count", ["", "One order", "%d orders"])

        assert len(store.units) == 2

        # Find and remove the items:count plural unit
        items_unit = next(u for u in store.units if u._plural_base_key == "items:count")
        store.removeunit(items_unit)
        assert len(store.units) == 1

        # Remaining unit is for orders:count
        remaining = store.units[0]
        assert remaining._plural_base_key == "orders:count"
        assert remaining.target.strings[1] == "One order"

    def test_removeunit_cleans_sibling_xml(self):
        """removeunit() on a plural unit also removes the sibling XML elements."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_BASIC_PLURAL_XLIFF)

        unit = store.units[0]
        assert unit.hasplural()
        store.removeunit(unit)

        assert len(store.units) == 0
        output = bytes(store).decode("utf-8")
        assert "items:count" not in output

    # ------------------------------------------------------------------
    # Mixed store: singular + plural
    # ------------------------------------------------------------------

    def test_convert_non_plural_to_plural(self):
        """A non-plural unit is removed and replaced by a plural group."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="greeting" xml:space="preserve">
        <source>Hello</source>
        <target>Hello</target>
      </trans-unit>
      <trans-unit id="item_count" xml:space="preserve">
        <source>%d items</source>
        <target>%d items</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(xliff_content)

        assert len(store.units) == 2

        # Remove the non-plural unit
        unit_to_replace = next(
            u for u in store.units if u.xmlelement.get("id") == "item_count"
        )
        store.removeunit(unit_to_replace)
        assert len(store.units) == 1

        # Add a plural unit in its place (1 original + 1 plural = 2 units)
        _add_plural(
            store,
            "item_count:count",
            ["", "One item", "%d items"],
            source_strings=["", "One item", "%d items"],
        )
        assert len(store.units) == 2

        output = bytes(store).decode("utf-8")
        assert 'id="greeting"' in output
        assert 'id="item_count:count:dict"' in output
        assert 'id="item_count:count:dict/one:dict/:string"' in output
        assert 'id="item_count:count:dict/other:dict/:string"' in output

        # Round-trip
        store2 = self.StoreClass()
        store2.settargetlanguage("en")
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 2

        plural = next(u for u in store2.units if u.hasplural())
        assert plural._plural_base_key == "item_count:count"
        assert plural.target.strings[1] == "One item"
        assert plural.target.strings[2] == "%d items"

    def test_convert_plural_to_non_plural(self):
        """A plural group is removed and replaced by a regular unit."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_BASIC_PLURAL_XLIFF)

        # After folding: 1 merged plural = 1 unit
        assert len(store.units) == 1

        plural_unit = store.units[0]
        assert plural_unit._plural_base_key == "items:count"
        store.removeunit(plural_unit)
        assert len(store.units) == 0

        new_unit = store.addsourceunit(
            "Items", filename="Localizable.strings", createifmissing=True
        )
        new_unit.setid("items_label")
        new_unit.target = "Items"
        assert len(store.units) == 1

        output = bytes(store).decode("utf-8")
        assert 'id="items_label"' in output
        assert "items:count:dict" not in output

        # Round-trip
        store2 = self.StoreClass()
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 1
        assert store2.units[0].target == "Items"

    def test_add_plural_unit_to_parsed_store(self):
        """A plural unit can be added to an already-parsed store."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_SINGULAR_XLIFF)
        assert len(store.units) == 1

        _add_plural(store, "items:count", ["", "One item", "%d items"])
        assert len(store.units) == 2

        plural = next(u for u in store.units if u.hasplural())
        assert plural.target.strings[1] == "One item"
        assert plural.target.strings[2] == "%d items"

    # ------------------------------------------------------------------
    # Target update round-trip
    # ------------------------------------------------------------------

    def test_plural_unit_target_update_roundtrip(self):
        """Changing a parsed plural unit's target round-trips correctly."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(_BASIC_PLURAL_XLIFF)

        unit = store.units[0]
        assert unit.hasplural()

        unit.target = multistring(["", "Jeden Artikel", "%d Artikel"])

        output = bytes(store).decode("utf-8")
        assert "Jeden Artikel" in output
        assert "%d Artikel" in output
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert 'id="items:count:dict/other:dict/:string"' in output

        store2 = self.StoreClass()
        store2.settargetlanguage("en")
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 1
        assert store2.units[0].target.strings[1] == "Jeden Artikel"
        assert store2.units[0].target.strings[2] == "%d Artikel"

    # ------------------------------------------------------------------
    # hasplural + getid (combined)
    # ------------------------------------------------------------------

    def test_plural_unit_hasplural_and_getid(self):
        """hasplural() and getid() behave correctly for both unit types."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="L.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="hello" xml:space="preserve">
        <source>Hello</source><target>Hello</target>
      </trans-unit>
      <trans-unit id="n:count:dict" xml:space="preserve">
        <source>NSStringPluralRuleType</source><target>NSStringPluralRuleType</target>
      </trans-unit>
      <trans-unit id="n:count:dict/:string" xml:space="preserve">
        <source>d</source><target>d</target>
      </trans-unit>
      <trans-unit id="n:count:dict/one:dict/:string" xml:space="preserve">
        <source>one</source><target>one</target>
      </trans-unit>
      <trans-unit id="n:count:dict/other:dict/:string" xml:space="preserve">
        <source>other</source><target>other</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        store = self.StoreClass()
        store.parse(xliff_content)

        assert len(store.units) == 2

        regular = store.units[0]
        assert not regular.hasplural()
        assert "hello" in regular.getid()

        plural = store.units[1]
        assert plural.hasplural()
        # getid() returns the base key WITHOUT the ":dict" XML suffix
        assert plural.getid().endswith("n:count")
        assert "n:count:dict" not in plural.getid()

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def test_get_base_key(self):
        """get_base_key() extracts the correct base key from plural-style XML ids."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="test" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="key:var:dict" xml:space="preserve">
        <source>NSStringPluralRuleType</source>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        store = self.StoreClass()
        store.parse(xliff_content)
        unit = store.units[0]
        assert unit.get_base_key() == "key:var"

    def test_targetlanguage_auto_detection_filename(self):
        """Target language is auto-detected from the .lproj directory name."""
        store = self.StoreClass()
        store.filename = "Project/it.lproj/Localizable.xliff"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_base_filename(self):
        """Base.lproj is treated as English."""
        store = self.StoreClass()
        store.filename = "Project/Base.lproj/Localizable.xliff"
        assert store.gettargetlanguage() == "en"

    # ------------------------------------------------------------------
    # Real-world patterns (ONLYOFFICE-style marker-less plurals)
    # ------------------------------------------------------------------

    def test_real_world_plural_patterns(self):
        """Marker-less real-world plural patterns (ONLYOFFICE style) are handled."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="lt" datatype="plaintext">
    <body>
      <trans-unit id="/%d days are left until the license expiration.:dict/NSStringLocalizedFormatKey:dict/:string">
        <source>%#@days@</source>
        <target>%#@dienos@</target>
      </trans-unit>
      <trans-unit id="/%d days are left until the license expiration.:dict/days:dict/few:dict/:string">
        <source>%d days are left until the license expiration.</source>
        <target state="translated">Days left until expiration (few).</target>
      </trans-unit>
      <trans-unit id="/%d days are left until the license expiration.:dict/days:dict/many:dict/:string">
        <source>%d days are left until the license expiration.</source>
        <target state="translated">Days left until expiration (many).</target>
      </trans-unit>
      <trans-unit id="/%d days are left until the license expiration.:dict/days:dict/one:dict/:string">
        <source>%d day are left until the license expiration.</source>
        <target state="translated">Days left until expiration (one).</target>
      </trans-unit>
      <trans-unit id="/%d days are left until the license expiration.:dict/days:dict/other:dict/:string">
        <source>%d days are left until the license expiration.</source>
        <target state="translated">Days left until expiration (other).</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

        store = self.StoreClass()
        store.settargetlanguage("lt")
        store.parse(xliff_content)

        # NSStringLocalizedFormatKey (format_type only, no forms) → regular unit
        # days plural group → folded unit
        assert len(store.units) == 2

        format_key_unit = store.units[0]
        assert "NSStringLocalizedFormatKey" in format_key_unit.xmlelement.get("id")
        assert not format_key_unit.hasplural()

        days_unit = store.units[1]
        assert days_unit.hasplural()
        # Lithuanian has multiple plural forms (few, many, one, other)
        assert len([s for s in days_unit.target.strings if s]) >= 4
