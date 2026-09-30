from decimal import Decimal

import pytest

from translate.lang import data
from translate.misc import cldr_plurals

# Samples from the CLDR plural rules (supplemental/plurals.json).
SAMPLES = {
    "en": {
        "one": ["1"],
        "other": ["0", "2", "16", "100", "0.0", "1.0", "1.5", "10.0"],
    },
    "fr": {
        "one": ["0", "1", "0.0", "1.5"],
        "many": ["1000000"],
        "other": ["2", "17", "100", "1000", "2.0", "3.5"],
    },
    "ru": {
        "one": ["1", "21", "31", "101", "1001"],
        "few": ["2", "3", "4", "22", "24", "102", "1002"],
        "many": ["0", "5", "11", "12", "14", "19", "100", "111", "1000000"],
        "other": ["0.0", "1.5", "10.0", "100.0"],
    },
    "uk": {
        "one": ["1", "21", "101"],
        "few": ["2", "22", "44"],
        "many": ["0", "5", "11", "25", "111"],
        "other": ["0.5", "1.0", "2.5"],
    },
    "pl": {
        "one": ["1"],
        "few": ["2", "4", "22", "24"],
        "many": ["0", "5", "12", "21", "111"],
        "other": ["0.0", "1.5", "10.0"],
    },
    "cs": {
        "one": ["1"],
        "few": ["2", "4"],
        "many": ["0.0", "1.5", "10.0"],
        "other": ["0", "5", "19", "100"],
    },
    "lt": {
        "one": ["1", "21", "1.0", "21.0"],
        "few": ["2", "9", "22", "2.0"],
        "many": ["0.1", "1.5", "10.1"],
        "other": ["0", "10", "11", "19", "20", "0.0", "10.0"],
    },
    "lv": {
        "zero": ["0", "10", "11", "19", "20", "0.0", "0.11", "10.12"],
        "one": ["1", "21", "0.1", "1.0", "0.21", "1.21"],
        "other": ["2", "9", "22", "0.2", "0.25"],
    },
    "ar": {
        "zero": ["0", "0.0"],
        "one": ["1", "1.0"],
        "two": ["2", "2.00"],
        "few": ["3", "10", "103", "110"],
        "many": ["11", "26", "99", "111"],
        "other": ["100", "102", "200", "0.1", "1.5"],
    },
    "sl": {
        "one": ["1", "101"],
        "two": ["2", "102"],
        "few": ["3", "4", "103", "0.5", "1.5"],
        "other": ["0", "5", "19", "100"],
    },
    "gd": {
        "one": ["1", "11", "1.0"],
        "two": ["2", "12", "2.0"],
        "few": ["3", "10", "13", "19"],
        "other": ["0", "20", "34", "0.5"],
    },
    "is": {
        "one": ["1", "21", "0.1", "10.1"],
        "other": ["0", "2", "11", "0.0", "2.0", "10.0"],
    },
    "da": {"one": ["1", "0.1", "1.6"], "other": ["0", "2", "0.0", "2.0"]},
    "fil": {"one": ["0", "1", "5", "0.0", "0.5"], "other": ["4", "6", "9", "0.4"]},
    "kw": {
        "zero": ["0"],
        "one": ["1"],
        "two": ["2", "22", "1000", "100000"],
        "few": ["3", "23"],
        "many": ["21", "41"],
        "other": ["4", "20", "1100"],
    },
    "ja": {"other": ["0", "1", "2", "1.5"]},
}


@pytest.mark.parametrize("language", SAMPLES)
def test_samples(language) -> None:
    for category, numbers in SAMPLES[language].items():
        for number in numbers:
            assert cldr_plurals.get_category(language, number) == category, number


def test_integer_and_decimal_input() -> None:
    assert cldr_plurals.get_category("en", 1) == "one"
    assert cldr_plurals.get_category("en", Decimal("1.0")) == "other"
    assert cldr_plurals.get_category("en", -1) == "one"


def test_operands() -> None:
    assert cldr_plurals.get_operands("1.230") == {
        "n": Decimal("1.230"),
        "i": 1,
        "v": 3,
        "w": 2,
        "f": 230,
        "t": 23,
        "c": 0,
        "e": 0,
    }
    assert cldr_plurals.get_operands(5)["v"] == 0


def test_operands_invalid() -> None:
    with pytest.raises(ValueError, match="Not a number"):
        cldr_plurals.get_operands("abc")


def test_categories() -> None:
    assert cldr_plurals.get_categories("en") == ["one", "other"]
    assert cldr_plurals.get_categories("ru") == ["one", "few", "many", "other"]
    assert cldr_plurals.get_categories("ar") == list(cldr_plurals.CATEGORIES)
    assert cldr_plurals.get_categories("ja") == ["other"]


def test_all_rules_compile() -> None:
    for language in cldr_plurals.plural_rules:
        assert cldr_plurals.get_category(language, 1) in cldr_plurals.CATEGORIES


def test_consistent_with_plural_tags() -> None:
    """Integer categories match the plural tags used by the toolkit."""
    for language in ("en", "fr", "ru", "uk", "pl", "cs", "lt", "ar", "sl", "gd"):
        integer_categories = {
            cldr_plurals.get_category(language, number) for number in range(1000)
        }
        expected = set(data.plural_tags[language]) - {"many"}
        assert expected <= integer_categories


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("uk", "uk"),
        ("uk_UA", "uk"),
        ("pt_PT", "pt-PT"),
        ("pt-PT", "pt-PT"),
        ("pt_BR", "pt"),
        ("sr@latin", "sr"),
        ("de_DE.UTF-8", "de"),
        ("zh_Hans_CN", "zh"),
        ("EN", "en"),
        ("xx", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_language(code, expected) -> None:
    assert cldr_plurals.normalize_language(code) == expected


@pytest.mark.parametrize(
    "rule",
    [
        "n = ",
        "n = 1 and",
        "x = 1",
        "n % = 1",
        "n < 1",
        "n 1",
        "n = 1 1",
        "n = 1..",
        "n = one",
        "n = 1 @integer 1",
    ],
)
def test_invalid_rules(rule) -> None:
    with pytest.raises(ValueError, match="Invalid plural rule"):
        cldr_plurals.compile_rule(rule)


def test_compile_rule() -> None:
    rule = cldr_plurals.compile_rule("n % 10 = 3..4,9 and n % 100 != 10..19")
    assert rule(cldr_plurals.get_operands(3))
    assert rule(cldr_plurals.get_operands(29))
    assert not rule(cldr_plurals.get_operands(13))
    assert not rule(cldr_plurals.get_operands("3.5"))
