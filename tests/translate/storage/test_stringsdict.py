import plistlib
from io import BytesIO

import pytest

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base, stringsdict

from . import test_monolingual


class TestStringsDictUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = stringsdict.StringsDictUnit

    def test_source(self) -> None:
        unit = self.UnitClass()
        unit.set_unitid(unit.IdClass([("key", "Test String"), ("key", "p")]))
        unit2 = self.UnitClass("Test String:p")
        unit3 = self.UnitClass("Test String 2:p")
        unit4 = self.UnitClass("Test String:q")

        assert unit == unit2
        assert unit != unit3
        assert unit != unit4

    def test_eq_formatvaluetype(self) -> None:
        unit = self.UnitClass("Test String:p")
        unit2 = self.UnitClass("Test String:p")

        assert unit == unit2
        unit2.format_value_type = "d"
        assert unit != unit2
        unit.format_value_type = "d"
        assert unit == unit2

    def test_eq_other_unit_type(self) -> None:
        unit = self.UnitClass("Test String:p")
        unit.target = "target"
        unit2 = base.TranslationUnit("Test String:p")
        unit2.target = "target"

        assert unit != unit2

    def test_innerkey(self) -> None:
        unit = self.UnitClass()
        unit.set_unitid(unit.IdClass([("key", "Test String"), ("key", "p")]))
        assert unit.outerkey == "Test String"
        assert unit.innerkey == "p"


class TestStringsDictFile(test_monolingual.TestMonolingualStore):
    StoreClass = stringsdict.StringsDictFile

    @staticmethod
    def get_simple_plural(
        localized_format="%#@count@", *, include_format=True, include_plural=True
    ):
        outer = {}
        if include_format:
            outer["NSStringLocalizedFormatKey"] = localized_format
        if include_plural:
            outer["count"] = {
                "NSStringFormatSpecTypeKey": "NSStringPluralRuleType",
                "NSStringFormatValueTypeKey": "d",
                "one": "One item",
                "other": "%d items",
            }
        return {"items": outer}

    def test_serialize(self) -> None:
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>shopping-list</key>
        <dict>
            <key>NSStringLocalizedFormatKey</key>
            <string>%1$#@apple@ and %2$#@orange@.</string>
            <key>apple</key>
            <dict>
                <key>NSStringFormatSpecTypeKey</key>
                <string>NSStringPluralRuleType</string>
                <key>NSStringFormatValueTypeKey</key>
                <string>d</string>
                <key>one</key>
                <string>One apple</string>
                <key>other</key>
                <string>%d apples</string>
            </dict>
            <key>orange</key>
            <dict>
                <key>NSStringFormatSpecTypeKey</key>
                <string>NSStringPluralRuleType</string>
                <key>NSStringFormatValueTypeKey</key>
                <string>d</string>
                <key>zero</key>
                <string>no oranges</string>
                <key>one</key>
                <string>one orange</string>
                <key>other</key>
                <string>%d oranges</string>
            </dict>
        </dict>
        <key>other-string</key>
        <dict>
            <key>NSStringLocalizedFormatKey</key>
            <string>Other string</string>
        </dict>
    </dict>
</plist>"""
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(content)

        assert store.units[0].source == "shopping-list"
        assert store.units[0].target == "%1$#@apple@ and %2$#@orange@."
        assert store.units[1].source == "shopping-list:apple"
        assert store.units[1].target.strings == ["", "One apple", "%d apples"]
        assert store.units[2].source == "shopping-list:orange"
        assert store.units[2].target.strings == [
            "no oranges",
            "one orange",
            "%d oranges",
        ]
        assert store.units[3].source == "other-string"
        assert store.units[3].target == "Other string"

        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_single_plural_is_folded(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural()))

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "items:count"
        assert unit.target.strings == ["", "One item", "%d items"]
        assert unit.localized_format == "%#@count@"
        assert unit.format_value_type == "d"

        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_single_plural_preserves_positional_format(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural("%1$#@count@")))

        assert len(store.units) == 1
        assert store.units[0].localized_format == "%1$#@count@"

        output = plistlib.loads(bytes(store))
        assert output["items"]["NSStringLocalizedFormatKey"] == "%1$#@count@"

        store.units[0].setid(store.units[0].getid())
        output = plistlib.loads(bytes(store))
        assert output["items"]["NSStringLocalizedFormatKey"] == "%1$#@count@"

    def test_single_plural_with_literal_format_is_not_folded(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural("There are %#@count@.")))

        assert [unit.source for unit in store.units] == ["items", "items:count"]
        assert store.units[0].target == "There are %#@count@."
        assert store.units[1].localized_format is None

        newstore = self.reparse(store)
        self.check_equality(store, newstore)

    def test_format_only_plural_is_folded(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural(include_plural=False)))

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "items:count"
        assert unit.target.strings == ["", "", ""]
        assert unit.localized_format == "%#@count@"

        # Do not serialize the incomplete entry.
        assert plistlib.loads(bytes(store)) == {}

        unit.target = multistring(["", "One item", "%d items"])
        output = plistlib.loads(bytes(store))["items"]
        assert output["NSStringLocalizedFormatKey"] == "%#@count@"
        assert output["count"]["other"] == "%d items"
        assert "NSStringFormatValueTypeKey" not in output["count"]

    def test_plural_only_is_omitted_without_format(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural(include_format=False)))

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "items:count"
        assert unit.localized_format is None

        # The missing format might have contained literal text, so it cannot be
        # reconstructed safely from the plural variable name.
        assert plistlib.loads(bytes(store)) == {}

    def test_new_plural_synthesizes_format(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = store.UnitClass("items:amount")
        unit.target = multistring(["", "One item", "%d items"])
        store.addunit(unit)

        output = plistlib.loads(bytes(store))["items"]
        assert output["NSStringLocalizedFormatKey"] == "%#@amount@"
        assert output["amount"]["other"] == "%d items"

    def test_set_unitid_plural_synthesizes_format(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = store.UnitClass()
        unit.set_unitid(unit.IdClass([("key", "items"), ("key", "amount")]))
        unit.target = multistring(["", "One item", "%d items"])
        store.addunit(unit)

        output = plistlib.loads(bytes(store))["items"]
        assert output["NSStringLocalizedFormatKey"] == "%#@amount@"
        assert output["amount"]["other"] == "%d items"

    def test_new_plural_requires_variable_in_id(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = store.UnitClass("items")
        unit.target = multistring(["", "One item", "%d items"])
        store.addunit(unit)

        with pytest.raises(
            TypeError,
            match="Plural stringsdict unit IDs must include a variable name",
        ):
            bytes(store)

    def test_targetlanguage_default_handlings(self) -> None:
        store = self.StoreClass()

        # Initial value is None
        assert store.gettargetlanguage() is None

        # sourcelanguage shouldn't change the targetlanguage
        store.setsourcelanguage("en")
        assert store.gettargetlanguage() is None

        # targetlanguage setter works correctly
        store.settargetlanguage("de")
        assert store.gettargetlanguage() == "de"

        # explicit targetlanguage wins over filename
        store.filename = "Project/it.lproj/Localizable.stringsdict"
        assert store.gettargetlanguage() == "de"

    def test_targetlanguage_auto_detection_filename(self) -> None:
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "Project/it.lproj/Localizable.stringsdict"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_base_filename(self) -> None:
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "Project/Base.lproj/Localizable.stringsdict"
        assert store.gettargetlanguage() == "en"

    def test_targetlanguage_auto_detection_filename_default_language(self) -> None:
        store = self.StoreClass()

        store.setsourcelanguage("nl")

        # Check language auto_detection
        store.filename = "Project/Localizable.stringsdict"
        assert store.gettargetlanguage() == "nl"

        # Clear cache
        store.settargetlanguage(None)

        store.filename = "invalid_filename"
        assert store.gettargetlanguage() == "nl"

    def test_plural_zero_always_set(self) -> None:
        def lang_without_zero(tuple):
            return len(tuple[1]) > 3 and "zero" not in tuple[1]

        lang = next(filter(lang_without_zero, data.plural_tags.items()))

        store = self.StoreClass()
        store.settargetlanguage(lang[0])

        store.addsourceunit("item")

        unit = store.UnitClass("item:p")
        unit.target = multistring(lang[1])
        store.addunit(unit)

        bytes_io = BytesIO()
        store.serialize(bytes_io)
        bytes_io.seek(0)

        plist = plistlib.load(bytes_io)
        assert plist["item"]["p"]["zero"]

    def test_unknown_language_single_plural_uses_other(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("tok")
        store.addsourceunit("item")

        unit = store.UnitClass("item:p")
        unit.target = multistring(["the only form"])
        store.addunit(unit)

        bytes_io = BytesIO()
        store.serialize(bytes_io)
        bytes_io.seek(0)

        plural = plistlib.load(bytes_io)["item"]["p"]
        assert plural["other"] == "the only form"
        assert "one" not in plural
        assert "zero" not in plural

    def test_unknown_language_two_plurals_use_zero_and_other(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("tok")
        store.addsourceunit("item")

        unit = store.UnitClass("item:p")
        unit.target = multistring(["no items", "items"])
        store.addunit(unit)

        bytes_io = BytesIO()
        store.serialize(bytes_io)
        bytes_io.seek(0)

        plural = plistlib.load(bytes_io)["item"]["p"]
        assert plural["zero"] == "no items"
        assert plural["other"] == "items"
        assert "one" not in plural

    def test_add_unit(self) -> None:
        store = self.StoreClass()

        unit = store.UnitClass("item")
        unit.setid("item")
        unit.target = "test target"
        store.addunit(unit)

        content = bytes(store)

        store2 = self.StoreClass()
        store2.parse(content)
        assert store2.units[0].target == "test target"
