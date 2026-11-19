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

    def reparse(self, store):
        parsed = self.StoreClass()
        parsed.settargetlanguage(store.gettargetlanguage())
        parsed.parse(bytes(store))
        return parsed

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

    @pytest.mark.parametrize(
        ("language", "target", "expected"),
        [
            (
                "en",
                ["", "new one", "new other"],
                {"one": "new one", "other": "new other"},
            ),
            ("ja", "new other", {"other": "new other"}),
        ],
    )
    def test_imported_variable_positional_target(
        self, language, target, expected
    ) -> None:
        content = self.get_simple_plural()
        fields = content["items"]["count"]
        fields.pop("NSStringFormatSpecTypeKey")
        fields["custom"] = "keep"
        store = self.StoreClass()
        store.settargetlanguage(language)
        store.parse(plistlib.dumps(content))
        assert (
            plistlib.loads(bytes(store))["items"]["count"]["NSStringFormatSpecTypeKey"]
            == "NSStringPluralRuleType"
        )
        store.units[0].target = target
        assert plistlib.loads(bytes(store))["items"]["count"] == {
            "NSStringFormatSpecTypeKey": "NSStringPluralRuleType",
            "NSStringFormatValueTypeKey": "d",
            "custom": "keep",
            **expected,
        }

    def test_equality_after_metadata_edit(self) -> None:
        content = self.get_simple_plural()
        del content["items"]["count"]["NSStringFormatSpecTypeKey"]
        store = self.StoreClass()
        store.parse(plistlib.dumps(content))
        unit = store.units[0]
        unit.format_value_type = "f"
        assert self.reparse(store).units[0] == unit

    @pytest.mark.parametrize("field", ["many", "custom"])
    def test_equality_includes_unprojected_fields(self, field) -> None:
        content = self.get_simple_plural()
        stores = [self.StoreClass(), self.StoreClass()]
        for index, store in enumerate(stores):
            store.settargetlanguage("cs")
            content["items"]["count"][field] = str(index)
            store.parse(plistlib.dumps(content))
        assert stores[0].units[0] != stores[1].units[0]

    def test_foreign_scalar_merge(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural()))
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = "replacement"
        store.settargetlanguage("cs")
        unit.merge(donor, overwrite=True)
        assert unit.plural_forms["other"] == "replacement"
        unit.rich_target = unit.rich_target
        assert unit.plural_forms["other"] == "replacement"

    def test_named_forms(self) -> None:
        content = self.get_simple_plural()
        content["items"]["count"].update(many="fraction", other="")
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse(plistlib.dumps(content))
        unit = store.units[0]
        assert plistlib.loads(bytes(store)) == content
        assert unit.plural_forms["many"] == "fraction"
        unit.update_plural_forms({"one": None, "other": "rest"})
        assert self.reparse(store).units[0].plural_forms == {
            "many": "fraction",
            "other": "rest",
        }
        unit.plural_forms = {"many": ""}
        with pytest.raises(ValueError):
            unit.update_plural_forms({"invalid": "bad"})
        assert self.reparse(store).units[0].plural_forms == {"many": ""}

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

    @pytest.mark.parametrize(
        "language", ["ru", "pl", "uk", "be", "rus", "pol", "ukr", "bel", "ru_RU"]
    )
    @pytest.mark.parametrize("localized_format", ["%1$#@count@", "Count: %#@count@"])
    @pytest.mark.parametrize("value_type", ["d", "f"])
    def test_plural_without_other_uses_many(
        self, language, localized_format, value_type
    ) -> None:
        content = self.get_simple_plural(localized_format)
        plural = content["items"]["count"]
        plural.update(
            {
                "NSStringFormatValueTypeKey": value_type,
                "zero": "No items",
                "few": "%d few items",
                "many": "%d many items",
                "other": "Distinct imported fallback",
            }
        )
        store = self.StoreClass()
        store.settargetlanguage(language)
        store.parse(plistlib.dumps(content))
        target = ["No items", "One item", "%d few items", "%d many items"]
        assert store.units[-1].target.strings == target

        serialized = bytes(store)
        output = plistlib.loads(serialized)
        expected = self.get_simple_plural(localized_format)
        expected["items"]["count"] = plural
        assert output == expected
        assert store.units[-1].target.strings == target

        newstore = self.reparse(store)
        self.check_equality(store, newstore)
        assert bytes(newstore) == serialized

    @pytest.mark.parametrize("language", ["ru", "pl", "uk", "be"])
    @pytest.mark.parametrize("many", [None, ""])
    @pytest.mark.parametrize("localized_format", ["%#@count@", "Count: %#@count@"])
    def test_plural_without_other_and_empty_many(
        self, language, many, localized_format
    ) -> None:
        content = self.get_simple_plural(localized_format)
        plural = content["items"]["count"]
        plural["few"] = "%d few items"
        if many is not None:
            plural["many"] = many
        store = self.StoreClass()
        store.settargetlanguage(language)
        store.parse(plistlib.dumps(content))

        output = plistlib.loads(bytes(store))
        assert output == content

    @pytest.mark.parametrize("language", ["en", "de"])
    def test_represented_other_cannot_use_one_as_fallback(self, language) -> None:
        content = self.get_simple_plural()
        content["items"]["count"]["other"] = ""
        store = self.StoreClass()
        store.settargetlanguage(language)
        store.parse(plistlib.dumps(content))

        assert plistlib.loads(bytes(store)) == content

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

        assert unit.plural_forms == {}
        assert plistlib.loads(bytes(store)) == self.get_simple_plural(
            include_plural=False
        )

        unit.target = multistring(["", "One item", "%d items"])
        output = plistlib.loads(bytes(store))["items"]
        assert output["NSStringLocalizedFormatKey"] == "%#@count@"
        assert output["count"]["other"] == "%d items"
        assert "NSStringFormatValueTypeKey" not in output["count"]

    def test_preserve_plural_without_format(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        store.parse(plistlib.dumps(self.get_simple_plural(include_format=False)))

        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "items:count"
        assert unit.localized_format is None

        # The missing format might have contained literal text, so it cannot be
        # reconstructed safely from the plural variable name.
        assert plistlib.loads(bytes(store)) == self.get_simple_plural(
            include_format=False
        )

    def test_equality_of_positional_placeholder(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("en")
        unit = store.UnitClass("items:amount")
        unit.target = multistring(["", "one", "other"])
        store.addunit(unit)
        parsed = self.reparse(store).units[0]
        assert unit == parsed
        parsed.update_plural_forms({"zero": ""})
        assert unit != parsed

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
