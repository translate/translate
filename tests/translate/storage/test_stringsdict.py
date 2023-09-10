import plistlib
from io import BytesIO

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import stringsdict, test_monolingual


class TestStringsDictUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = stringsdict.StringsDictUnit

    def test_source(self):
        unit = self.UnitClass()
        unit.set_unitid(unit.IdClass([("key", "Test String"), ("key", "p")]))
        unit2 = self.UnitClass("Test String:p")
        unit3 = self.UnitClass("Test String 2:p")
        unit4 = self.UnitClass("Test String:q")

        assert unit == unit2
        assert unit != unit3
        assert unit != unit4

    def test_eq_formatvaluetype(self):
        unit = self.UnitClass("Test String:p")
        unit2 = self.UnitClass("Test String:p")

        assert unit == unit2
        unit2.format_value_type = "d"
        assert unit != unit2
        unit.format_value_type = "d"
        assert unit == unit2

    def test_innerkey(self):
        unit = self.UnitClass()
        unit.set_unitid(unit.IdClass([("key", "Test String"), ("key", "p")]))
        assert unit.outerkey == "Test String"
        assert unit.innerkey == "p"


class TestStringsDictFile(test_monolingual.TestMonolingualStore):
    StoreClass = stringsdict.StringsDictFile

    def test_serialize(self):
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

    def test_targetlanguage_default_handlings(self):
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

    def test_targetlanguage_auto_detection_filename(self):
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "Project/it.lproj/Localizable.stringsdict"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_base_filename(self):
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "Project/Base.lproj/Localizable.stringsdict"
        assert store.gettargetlanguage() == "en"

    def test_targetlanguage_auto_detection_filename_default_language(self):
        store = self.StoreClass()

        store.setsourcelanguage("nl")

        # Check language auto_detection
        store.filename = "Project/Localizable.stringsdict"
        assert store.gettargetlanguage() == "nl"

        # Clear cache
        store.settargetlanguage(None)

        store.filename = "invalid_filename"
        assert store.gettargetlanguage() == "nl"

    def test_plural_zero_always_set(self):
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

    def test_add_unit(self):
        store = self.StoreClass()

        unit = store.UnitClass("item")
        unit.setid("item")
        unit.target = "test target"
        store.addunit(unit)

        content = bytes(store)

        store2 = self.StoreClass()
        store2.parse(content)
        assert store2.units[0].target == "test target"
