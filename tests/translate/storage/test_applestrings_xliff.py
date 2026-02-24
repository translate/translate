"""Tests for Apple XLIFF format with plural support."""

from translate.misc.multistring import multistring
from translate.storage import applestrings_xliff

from . import test_xliff


class TestAppleStringsXliffUnit(test_xliff.TestXLIFFUnit):
    """Tests for AppleStringsXliffUnit."""

    UnitClass = applestrings_xliff.AppleStringsXliffUnit


class TestAppleStringsXliffFile(test_xliff.TestXLIFFfile):
    """Tests for AppleStringsXliffFile."""

    StoreClass = applestrings_xliff.AppleStringsXliffFile

    def test_parse_basic_string(self):
        """Test parsing a basic non-plural string."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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
        store = self.StoreClass()
        store.parse(xliff_content)

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "Hello"
        assert unit.target == "Hello"

    def test_parse_apple_plural_basic(self):
        """Test parsing Apple XLIFF with simple plurals – plurals are folded into one unit."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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
        store = self.StoreClass()
        store.parse(xliff_content)

        # The four raw trans-units are folded into a single plural unit
        assert len(store.units) == 1

        unit = store.units[0]
        assert unit.hasplural()
        assert unit.format_value_type == "d"
        assert unit._plural_base_key == "items:count"

        # source and target are multistrings (zero, one, other for English)
        assert isinstance(unit.source, multistring)
        assert isinstance(unit.target, multistring)
        assert unit.source.strings[1] == "One item"   # 'one' form
        assert unit.source.strings[2] == "%d items"   # 'other' form
        assert unit.target.strings[1] == "One item"
        assert unit.target.strings[2] == "%d items"

    def test_parse_apple_plural_complex(self):
        """Test parsing Apple XLIFF with complex plural example – each group becomes one unit."""
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
        format_string_unit = store.units[0]
        assert format_string_unit.source == "%1$#@apple@ and %2$#@orange@."

        # Apple group: accessible via get_plural_unit() and directly via unit
        apple_unit = store.units[1]
        assert apple_unit.hasplural()
        assert apple_unit.format_value_type == "d"
        assert isinstance(apple_unit.target, multistring)
        # For English: zero, one, other
        assert len(apple_unit.target.strings) == 3
        assert apple_unit.target.strings[1] == "One apple"   # 'one'
        assert apple_unit.target.strings[2] == "%d apples"   # 'other'

        # Convenience accessor still works
        apple_plural = store.get_plural_unit("shopping-list:apple")
        assert apple_plural is not None
        assert apple_plural["format_value_type"] == "d"
        assert apple_plural["target"].strings[1] == "One apple"
        assert apple_plural["target"].strings[2] == "%d apples"

        orange_unit = store.units[2]
        assert orange_unit.hasplural()
        orange_plural = store.get_plural_unit("shopping-list:orange")
        assert orange_plural is not None
        assert orange_plural["target"].strings[0] == "no oranges"   # 'zero'
        assert orange_plural["target"].strings[1] == "one orange"   # 'one'
        assert orange_plural["target"].strings[2] == "%d oranges"   # 'other'

    def test_get_base_key(self):
        """Test extracting base keys from Apple XLIFF IDs."""
        store = self.StoreClass()

        # Test with marker unit
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
        store.parse(xliff_content)
        unit = store.units[0]
        assert unit.get_base_key() == "key:var"

    def test_targetlanguage_auto_detection_filename(self):
        """Test that target language can be auto-detected from filename."""
        store = self.StoreClass()

        # Check language auto-detection (like stringsdict)
        store.filename = "Project/it.lproj/Localizable.xliff"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_base_filename(self):
        """Test that Base.lproj is treated as 'en'."""
        store = self.StoreClass()

        # Check language auto-detection
        store.filename = "Project/Base.lproj/Localizable.xliff"
        assert store.gettargetlanguage() == "en"

    def test_add_plural_unit(self):
        """Test adding a plural unit programmatically – results in a single merged unit."""
        store = self.StoreClass()
        store.settargetlanguage("en")

        # Add a plural unit
        plural_strings = ["", "One item", "%d items"]
        store.add_plural_unit("items:count", plural_strings, "d")

        # add_plural_unit creates a single merged unit (not 4 raw trans-units)
        assert len(store.units) == 1

        unit = store.units[0]
        assert unit.hasplural()
        assert unit._plural_base_key == "items:count"
        assert unit.format_value_type == "d"

        # source and target are multistrings
        assert isinstance(unit.source, multistring)
        assert isinstance(unit.target, multistring)
        assert unit.target.strings[1] == "One item"
        assert unit.target.strings[2] == "%d items"

        # Verify we can retrieve the plural unit via the convenience method
        plural = store.get_plural_unit("items:count")
        assert plural is not None
        assert plural["target"].strings[1] == "One item"
        assert plural["target"].strings[2] == "%d items"

    def test_serialize_plural_roundtrip(self):
        """Test that we can parse and serialize plural units."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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

        # Parse
        store = self.StoreClass()
        store.parse(xliff_content)

        # Serialize
        output = bytes(store)

        # Parse again
        store2 = self.StoreClass()
        store2.parse(output)

        # Verify
        plural = store2.get_plural_unit("items:count")
        assert plural is not None
        assert plural["target"].strings[1] == "One item"
        assert plural["target"].strings[2] == "%d items"

    def test_real_world_plural_patterns(self):
        """Test parsing real-world Apple XLIFF plural patterns (ONLYOFFICE style)."""
        # Pattern from ONLYOFFICE files - uses leading slashes in IDs and
        # no NSStringPluralRuleType marker; plural forms are nested directly.
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

        # NSStringLocalizedFormatKey (format_type but no plural forms → kept as regular unit)
        # + merged plural unit for "days" variable = 2 units
        assert len(store.units) == 2

        # The NSStringLocalizedFormatKey trans-unit is preserved as a regular unit
        format_key_unit = store.units[0]
        assert "NSStringLocalizedFormatKey" in format_key_unit.xmlelement.get("id")

        # The "days" plural group is folded into one unit
        days_unit = store.units[1]
        assert days_unit.hasplural()

        # Lithuanian has multiple plural forms (few, many, one, other)
        assert len([s for s in days_unit.target.strings if s]) >= 4

        # Also accessible via get_plural_unit()
        plural = store.get_plural_unit(
            "/%d days are left until the license expiration.:dict/days"
        )
        assert plural is not None
        assert len([s for s in plural["target"].strings if s]) >= 4

    def test_serialize_plural_xml_structure(self):
        """Test that serialized plural units have the correct XML structure."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.add_plural_unit("items:count", ["", "One item", "%d items"], "d")

        output = bytes(store).decode("utf-8")

        # Verify the marker unit
        assert 'id="items:count:dict"' in output
        assert "<source>NSStringPluralRuleType</source>" in output

        # Verify the format type unit
        assert 'id="items:count:dict/:string"' in output
        assert "<source>d</source>" in output

        # Verify plural form units
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert "<source>One item</source>" in output

        assert 'id="items:count:dict/other:dict/:string"' in output
        assert "<source>%d items</source>" in output

        # Verify zero form is not present (was empty)
        assert 'id="items:count:dict/zero:dict/:string"' not in output

    def test_serialize_plural_all_forms(self):
        """Test serialization when all plural forms are provided."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.add_plural_unit("items:count", ["No items", "One item", "%d items"], "d")

        output = bytes(store).decode("utf-8")

        # All three forms should be present
        assert 'id="items:count:dict/zero:dict/:string"' in output
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert 'id="items:count:dict/other:dict/:string"' in output
        assert "<source>No items</source>" in output
        assert "<source>One item</source>" in output
        assert "<source>%d items</source>" in output

    def test_convert_non_plural_to_plural(self):
        """Test changing a non-plural unit to plural on a parsed store."""
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
            (u for u in store.units if u.xmlelement.get("id") == "item_count"), None
        )
        assert unit_to_replace is not None
        store.removeunit(unit_to_replace)

        assert len(store.units) == 1

        # Add plural unit in its place (creates a single merged unit)
        store.add_plural_unit("item_count:count", ["", "One item", "%d items"], "d")

        # 1 original (greeting) + 1 merged plural = 2 units
        assert len(store.units) == 2

        # Serialize and check output (XML has all 4 trans-units for the plural)
        output = bytes(store).decode("utf-8")
        assert 'id="greeting"' in output
        assert 'id="item_count:count:dict"' in output
        assert 'id="item_count:count:dict/one:dict/:string"' in output
        assert 'id="item_count:count:dict/other:dict/:string"' in output

        # Verify round-trip
        store2 = self.StoreClass()
        store2.settargetlanguage("en")
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 2
        plural = store2.get_plural_unit("item_count:count")
        assert plural is not None
        assert plural["target"].strings[1] == "One item"
        assert plural["target"].strings[2] == "%d items"

    def test_convert_plural_to_non_plural(self):
        """Test changing plural units back to a non-plural unit."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="Localizable.strings" source-language="en" target-language="en" datatype="plaintext">
    <body>
      <trans-unit id="greeting" xml:space="preserve">
        <source>Hello</source>
        <target>Hello</target>
      </trans-unit>
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

        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(xliff_content)

        # After folding: 1 greeting + 1 merged plural = 2 units
        assert len(store.units) == 2

        # Remove all plural units for "items:count"
        removed = store.remove_plural_unit("items:count")
        assert removed is True

        # Only the greeting unit should remain
        assert len(store.units) == 1

        # Verify plural unit is gone
        assert store.get_plural_unit("items:count") is None

        # Add a simple non-plural unit in its place
        new_unit = store.addsourceunit(
            "Items", filename="Localizable.strings", createifmissing=True
        )
        new_unit.setid("items_label")
        new_unit.target = "Items"

        assert len(store.units) == 2

        # Serialize and verify
        output = bytes(store).decode("utf-8")
        assert 'id="greeting"' in output
        assert 'id="items_label"' in output
        assert "items:count:dict" not in output

        # Verify round-trip
        store2 = self.StoreClass()
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 2
        greeting_unit = next(
            (u for u in store2.units if u.xmlelement.get("id") == "greeting"), None
        )
        assert greeting_unit is not None
        assert greeting_unit.target == "Hello"

    def test_remove_plural_unit(self):
        """Test remove_plural_unit method."""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.add_plural_unit("items:count", ["", "One item", "%d items"], "d")
        store.add_plural_unit("orders:count", ["", "One order", "%d orders"], "d")

        # Each group is now a single merged unit  →  2 units total
        assert len(store.units) == 2

        # Remove one group
        removed = store.remove_plural_unit("items:count")
        assert removed is True
        assert len(store.units) == 1

        # The remaining unit should be for orders:count
        assert store.get_plural_unit("items:count") is None
        orders_plural = store.get_plural_unit("orders:count")
        assert orders_plural is not None
        assert orders_plural["target"].strings[1] == "One order"

        # Removing a non-existent key returns False
        assert store.remove_plural_unit("nonexistent:key") is False

    def test_add_plural_unit_to_parsed_store(self):
        """Test that add_plural_unit works correctly on a parsed store."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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

        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(xliff_content)

        assert len(store.units) == 1

        # Add plural unit to the already-parsed store
        store.add_plural_unit("items:count", ["", "One item", "%d items"], "d")

        # 1 original + 1 merged plural = 2 units
        assert len(store.units) == 2

        plural = store.get_plural_unit("items:count")
        assert plural is not None
        assert plural["target"].strings[1] == "One item"
        assert plural["target"].strings[2] == "%d items"

    def test_plural_unit_target_update_roundtrip(self):
        """Test that changing a parsed plural unit's target round-trips correctly."""
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(xliff_content)

        unit = store.units[0]
        assert unit.hasplural()

        # Change the target (simulate translation update)
        unit.target = multistring(["", "Ein Artikel", "%d Artikel"])

        # Serialize – should output updated Apple XLIFF
        output = bytes(store).decode("utf-8")
        assert "Ein Artikel" in output
        assert "%d Artikel" in output
        assert 'id="items:count:dict/one:dict/:string"' in output
        assert 'id="items:count:dict/other:dict/:string"' in output

        # Round-trip
        store2 = self.StoreClass()
        store2.settargetlanguage("en")
        store2.parse(output.encode("utf-8"))
        assert len(store2.units) == 1
        assert store2.units[0].target.strings[1] == "Ein Artikel"
        assert store2.units[0].target.strings[2] == "%d Artikel"

    def test_plural_unit_hasplural_and_getid(self):
        """Test hasplural() and getid() on a folded plural unit."""
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
        # getid() returns the base key (without ":dict" suffix)
        assert plural.getid().endswith("n:count")
        assert "n:count:dict" not in plural.getid()
