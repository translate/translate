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
        """Test parsing Apple XLIFF with simple plurals."""
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

        # Check that units were parsed
        assert len(store.units) == 4

        # Check the marker unit
        marker_unit = store.units[0]
        assert marker_unit.is_plural_marker
        assert marker_unit.get_base_key() == "items:count"

        # Check format type unit
        format_unit = store.units[1]
        assert format_unit.is_format_type
        assert format_unit.target == "d"

        # Check plural form units
        one_unit = store.units[2]
        assert one_unit.is_plural_form
        assert one_unit.get_plural_form() == "one"
        assert one_unit.target == "One item"

        other_unit = store.units[3]
        assert other_unit.is_plural_form
        assert other_unit.get_plural_form() == "other"
        assert other_unit.target == "%d items"

    def test_parse_apple_plural_complex(self):
        """Test parsing Apple XLIFF with complex plural example from issue."""
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

        # Check that all units were parsed
        assert len(store.units) == 10

        # Check the format string
        format_string_unit = store.units[0]
        assert format_string_unit.source == "%1$#@apple@ and %2$#@orange@."

        # Check grouped plural units
        apple_plural = store.get_plural_unit("shopping-list:apple")
        assert apple_plural is not None
        assert apple_plural["format_value_type"] == "d"
        assert isinstance(apple_plural["target"], multistring)
        # For English, we expect: zero, one, other
        assert len(apple_plural["target"].strings) == 3
        assert apple_plural["target"].strings[1] == "One apple"  # 'one' form
        assert apple_plural["target"].strings[2] == "%d apples"  # 'other' form

        orange_plural = store.get_plural_unit("shopping-list:orange")
        assert orange_plural is not None
        assert orange_plural["format_value_type"] == "d"
        assert isinstance(orange_plural["target"], multistring)
        assert len(orange_plural["target"].strings) == 3
        assert orange_plural["target"].strings[0] == "no oranges"  # 'zero' form
        assert orange_plural["target"].strings[1] == "one orange"  # 'one' form
        assert orange_plural["target"].strings[2] == "%d oranges"  # 'other' form

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
        """Test adding a plural unit programmatically."""
        store = self.StoreClass()
        store.settargetlanguage("en")

        # Add a plural unit
        plural_strings = ["", "One item", "%d items"]
        store.add_plural_unit("items:count", plural_strings, "d")

        # Verify the units were added (marker + format + non-empty plural forms)
        # zero is empty, so only one and other are added
        assert len(store.units) == 4

        # Check marker unit
        marker_unit = store.units[0]
        assert marker_unit.xmlelement.get("id") == "items:count:dict"
        assert marker_unit.source == "NSStringPluralRuleType"

        # Check format unit
        format_unit = store.units[1]
        assert format_unit.xmlelement.get("id") == "items:count:dict/:string"
        assert format_unit.target == "d"

        # Check plural form units
        one_unit = store.units[2]
        assert "one:dict/:string" in one_unit.xmlelement.get("id")
        assert one_unit.target == "One item"

        other_unit = store.units[3]
        assert "other:dict/:string" in other_unit.xmlelement.get("id")
        assert other_unit.target == "%d items"

        # Verify we can retrieve the plural unit
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
        """Test parsing real-world Apple XLIFF plural patterns."""
        # Pattern from ONLYOFFICE files - uses leading slashes in IDs
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
        
        # Should parse successfully and recognize plurals
        assert len(store.units) == 5
        
        # The NSStringLocalizedFormatKey trans-unit exists
        format_key_unit = store.units[0]
        assert "NSStringLocalizedFormatKey" in format_key_unit.xmlelement.get("id")
        
        # Check plural forms
        plural = store.get_plural_unit("/%d days are left until the license expiration.:dict/days")
        assert plural is not None
        # Lithuanian has multiple plural forms (few, many, one, other)
        assert len([s for s in plural['target'].strings if s]) >= 4
