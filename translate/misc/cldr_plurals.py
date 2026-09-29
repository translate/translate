#
# Copyright 2026 Ivan Tugay <listepo@gmail.com>
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""
CLDR cardinal plural rules and a small evaluator for them.

The rules allow mapping a number to the CLDR plural category (``zero``,
``one``, ``two``, ``few``, ``many`` or ``other``) that formats such as Fluent,
ICU MessageFormat or Android resources use to select plural variants.

The rules are taken verbatim (without the ``@integer``/``@decimal`` samples)
from ``supplemental/plurals.json`` of the CLDR JSON data, see
https://github.com/unicode-org/cldr-json. The ``other`` category is implicit:
it applies whenever no other rule matches.

The rule syntax is described in
https://unicode.org/reports/tr35/tr35-numbers.html#Language_Plural_Rules
"""

from __future__ import annotations

import re
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from functools import cache

CLDR_VERSION = "48"

CATEGORIES = ("zero", "one", "two", "few", "many", "other")
"""All CLDR plural categories, in their canonical order."""

# Languages sharing the same set of rules are grouped together.
# spellchecker:off
_RULESETS: tuple[tuple[tuple[str, ...], dict[str, str]], ...] = (
    (
        (
            "bm",
            "bo",
            "dz",
            "hnj",
            "id",
            "ig",
            "ii",
            "ja",
            "jbo",
            "jv",
            "jw",
            "kde",
            "kea",
            "km",
            "ko",
            "lkt",
            "lo",
            "ms",
            "my",
            "nqo",
            "osa",
            "sah",
            "ses",
            "sg",
            "su",
            "th",
            "to",
            "tpi",
            "und",
            "vi",
            "wo",
            "yo",
            "yue",
            "zh",
        ),
        {},
    ),
    (
        (
            "af",
            "an",
            "asa",
            "az",
            "bal",
            "bem",
            "bez",
            "bg",
            "brx",
            "ce",
            "cgg",
            "chr",
            "ckb",
            "dv",
            "ee",
            "el",
            "eo",
            "eu",
            "fo",
            "fur",
            "gsw",
            "ha",
            "haw",
            "hu",
            "jgo",
            "jmc",
            "ka",
            "kaj",
            "kcg",
            "kk",
            "kkj",
            "kl",
            "ks",
            "ksb",
            "ku",
            "ky",
            "lb",
            "lg",
            "mas",
            "mgo",
            "ml",
            "mn",
            "mr",
            "nah",
            "nb",
            "nd",
            "ne",
            "nn",
            "nnh",
            "no",
            "nr",
            "ny",
            "nyn",
            "om",
            "or",
            "os",
            "pap",
            "ps",
            "rm",
            "rof",
            "rwk",
            "saq",
            "sd",
            "sdh",
            "seh",
            "sn",
            "so",
            "sq",
            "ss",
            "ssy",
            "st",
            "syr",
            "ta",
            "te",
            "teo",
            "tig",
            "tk",
            "tn",
            "tr",
            "ts",
            "ug",
            "uz",
            "ve",
            "vo",
            "vun",
            "wae",
            "xh",
            "xog",
        ),
        {
            "one": "n = 1",
        },
    ),
    (
        ("ak", "bho", "csw", "guw", "ln", "mg", "nso", "pa", "ti", "wa"),
        {
            "one": "n = 0..1",
        },
    ),
    (
        (
            "am",
            "as",
            "bn",
            "doi",
            "fa",
            "gu",
            "hi",
            "kn",
            "kok",
            "kok-Latn",
            "pcm",
            "zu",
        ),
        {
            "one": "i = 0 or n = 1",
        },
    ),
    (
        (
            "ast",
            "de",
            "en",
            "et",
            "fi",
            "fy",
            "gl",
            "ia",
            "ie",
            "io",
            "lij",
            "nl",
            "sc",
            "sv",
            "sw",
            "ur",
            "yi",
        ),
        {
            "one": "i = 1 and v = 0",
        },
    ),
    (
        ("ceb", "fil", "tl"),
        {
            "one": "v = 0 and i = 1,2,3 or v = 0 and i % 10 != 4,6,9 or v != 0 and f % 10 != 4,6,9",
        },
    ),
    (
        ("da",),
        {
            "one": "n = 1 or t != 0 and i = 0,1",
        },
    ),
    (
        ("ff", "hy", "kab"),
        {
            "one": "i = 0,1",
        },
    ),
    (
        ("is",),
        {
            "one": "t = 0 and i % 10 = 1 and i % 100 != 11 or t % 10 = 1 and t % 100 != 11",
        },
    ),
    (
        ("mk",),
        {
            "one": "v = 0 and i % 10 = 1 and i % 100 != 11 or f % 10 = 1 and f % 100 != 11",
        },
    ),
    (
        ("si",),
        {
            "one": "n = 0,1 or i = 0 and f = 1",
        },
    ),
    (
        ("tzm",),
        {
            "one": "n = 0..1 or n = 11..99",
        },
    ),
    (
        ("blo", "cv", "ksh"),
        {
            "zero": "n = 0",
            "one": "n = 1",
        },
    ),
    (
        ("bs", "hr", "sh", "sr"),
        {
            "one": "v = 0 and i % 10 = 1 and i % 100 != 11 or f % 10 = 1 and f % 100 != 11",
            "few": "v = 0 and i % 10 = 2..4 and i % 100 != 12..14 or f % 10 = 2..4 and f % 100 != 12..14",
        },
    ),
    (
        ("ca", "it", "lld", "pt-PT", "scn", "vec"),
        {
            "one": "i = 1 and v = 0",
            "many": "e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5",
        },
    ),
    (
        ("es",),
        {
            "one": "n = 1",
            "many": "e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5",
        },
    ),
    (
        ("fr",),
        {
            "one": "i = 0,1",
            "many": "e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5",
        },
    ),
    (
        ("he",),
        {
            "one": "i = 1 and v = 0 or i = 0 and v != 0",
            "two": "i = 2 and v = 0",
        },
    ),
    (
        ("iu", "naq", "sat", "se", "sma", "smi", "smj", "smn", "sms"),
        {
            "one": "n = 1",
            "two": "n = 2",
        },
    ),
    (
        ("lag",),
        {
            "zero": "n = 0",
            "one": "i = 0,1 and n != 0",
        },
    ),
    (
        ("lv", "prg"),
        {
            "zero": "n % 10 = 0 or n % 100 = 11..19 or v = 2 and f % 100 = 11..19",
            "one": "n % 10 = 1 and n % 100 != 11 or v = 2 and f % 10 = 1 and f % 100 != 11 or v != 2 and f % 10 = 1",
        },
    ),
    (
        ("mo", "ro"),
        {
            "one": "i = 1 and v = 0",
            "few": "v != 0 or n = 0 or n != 1 and n % 100 = 1..19",
        },
    ),
    (
        ("pt",),
        {
            "one": "i = 0..1",
            "many": "e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5",
        },
    ),
    (
        ("shi",),
        {
            "one": "i = 0 or n = 1",
            "few": "n = 2..10",
        },
    ),
    (
        ("be",),
        {
            "one": "n % 10 = 1 and n % 100 != 11",
            "few": "n % 10 = 2..4 and n % 100 != 12..14",
            "many": "n % 10 = 0 or n % 10 = 5..9 or n % 100 = 11..14",
        },
    ),
    (
        ("cs", "sk"),
        {
            "one": "i = 1 and v = 0",
            "few": "i = 2..4 and v = 0",
            "many": "v != 0",
        },
    ),
    (
        ("dsb", "hsb"),
        {
            "one": "v = 0 and i % 100 = 1 or f % 100 = 1",
            "two": "v = 0 and i % 100 = 2 or f % 100 = 2",
            "few": "v = 0 and i % 100 = 3..4 or f % 100 = 3..4",
        },
    ),
    (
        ("gd",),
        {
            "one": "n = 1,11",
            "two": "n = 2,12",
            "few": "n = 3..10,13..19",
        },
    ),
    (
        ("lt",),
        {
            "one": "n % 10 = 1 and n % 100 != 11..19",
            "few": "n % 10 = 2..9 and n % 100 != 11..19",
            "many": "f != 0",
        },
    ),
    (
        ("pl",),
        {
            "one": "i = 1 and v = 0",
            "few": "v = 0 and i % 10 = 2..4 and i % 100 != 12..14",
            "many": "v = 0 and i != 1 and i % 10 = 0..1 or v = 0 and i % 10 = 5..9 or v = 0 and i % 100 = 12..14",
        },
    ),
    (
        ("ru", "uk"),
        {
            "one": "v = 0 and i % 10 = 1 and i % 100 != 11",
            "few": "v = 0 and i % 10 = 2..4 and i % 100 != 12..14",
            "many": "v = 0 and i % 10 = 0 or v = 0 and i % 10 = 5..9 or v = 0 and i % 100 = 11..14",
        },
    ),
    (
        ("sl",),
        {
            "one": "v = 0 and i % 100 = 1",
            "two": "v = 0 and i % 100 = 2",
            "few": "v = 0 and i % 100 = 3..4 or v != 0",
        },
    ),
    (
        ("br",),
        {
            "one": "n % 10 = 1 and n % 100 != 11,71,91",
            "two": "n % 10 = 2 and n % 100 != 12,72,92",
            "few": "n % 10 = 3..4,9 and n % 100 != 10..19,70..79,90..99",
            "many": "n != 0 and n % 1000000 = 0",
        },
    ),
    (
        ("ga",),
        {
            "one": "n = 1",
            "two": "n = 2",
            "few": "n = 3..6",
            "many": "n = 7..10",
        },
    ),
    (
        ("gv",),
        {
            "one": "v = 0 and i % 10 = 1",
            "two": "v = 0 and i % 10 = 2",
            "few": "v = 0 and i % 100 = 0,20,40,60,80",
            "many": "v != 0",
        },
    ),
    (
        ("mt",),
        {
            "one": "n = 1",
            "two": "n = 2",
            "few": "n = 0 or n % 100 = 3..10",
            "many": "n % 100 = 11..19",
        },
    ),
    (
        ("sgs",),
        {
            "one": "n % 10 = 1 and n % 100 != 11",
            "two": "n = 2",
            "few": "n != 2 and n % 10 = 2..9 and n % 100 != 11..19",
            "many": "f != 0",
        },
    ),
    (
        ("ar", "ars"),
        {
            "zero": "n = 0",
            "one": "n = 1",
            "two": "n = 2",
            "few": "n % 100 = 3..10",
            "many": "n % 100 = 11..99",
        },
    ),
    (
        ("cy",),
        {
            "zero": "n = 0",
            "one": "n = 1",
            "two": "n = 2",
            "few": "n = 3",
            "many": "n = 6",
        },
    ),
    (
        ("kw",),
        {
            "zero": "n = 0",
            "one": "n = 1",
            "two": "n % 100 = 2,22,42,62,82 or n % 1000 = 0 and n % 100000 = 1000..20000,40000,60000,80000 or n != 0 and n % 1000000 = 100000",
            "few": "n % 100 = 3,23,43,63,83",
            "many": "n != 1 and n % 100 = 1,21,41,61,81",
        },
    ),
)
# spellchecker:on

plural_rules: dict[str, dict[str, str]] = {
    lang: rules for langs, rules in _RULESETS for lang in langs
}
"""CLDR cardinal plural rules by language code (``other`` is implicit)."""

_OPERANDS = frozenset("niwvftce")
_TOKEN_RE = re.compile(r"\s*(\.\.|!=|=|%|,|[a-z]+|\d+)")

Operands = dict[str, Decimal]
Condition = Callable[[Operands], bool]


def normalize_language(code: str | None) -> str | None:
    """
    Find the language code with CLDR plural rules best matching *code*.

    Accepts gettext style (``pt_BR``, ``sr@latin``) as well as BCP 47 style
    (``pt-PT``) codes and falls back to the base language.

    :return: The key in :data:`plural_rules`, or None if the language is
        unknown.
    """
    if not code:
        return None
    code = code.split("@", 1)[0].split(".", 1)[0].replace("_", "-").strip()
    parts = code.split("-")
    for candidate in ("-".join(parts[:2]), parts[0]):
        for variant in (candidate, candidate.lower()):
            if variant in plural_rules:
                return variant
    return None


def get_categories(language: str) -> list[str]:
    """Return the CLDR categories used by *language*, in canonical order."""
    rules = plural_rules[language]
    return [
        category for category in CATEGORIES if category in rules or category == "other"
    ]


def get_operands(number: int | str | Decimal) -> Operands:
    """
    Compute the CLDR plural operands for *number*.

    Integers and decimal strings (``"1.50"``, where trailing zeros are
    significant) are supported. Compact decimal exponents are not, so ``c``
    and ``e`` are always 0.
    """
    try:
        value = abs(Decimal(str(number)))
    except InvalidOperation as error:
        raise ValueError(f"Not a number: {number!r}") from error
    text = f"{value:f}"
    integer, _, fraction = text.partition(".")
    stripped = fraction.rstrip("0")
    return {
        "n": value,
        "i": Decimal(integer),
        "v": Decimal(len(fraction)),
        "w": Decimal(len(stripped)),
        "f": Decimal(fraction or 0),
        "t": Decimal(stripped or 0),
        "c": Decimal(0),
        "e": Decimal(0),
    }


class _RuleParser:
    """Recursive descent parser for the CLDR plural rule syntax."""

    def __init__(self, rule: str) -> None:
        self.rule = rule
        self.tokens = _TOKEN_RE.findall(rule)
        if "".join(self.tokens) != re.sub(r"\s+", "", rule):
            raise ValueError(f"Invalid plural rule: {rule!r}")
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise ValueError(f"Invalid plural rule: {self.rule!r}")
        self.pos += 1
        return token

    def parse(self) -> Condition:
        condition = self.or_condition()
        if self.peek() is not None:
            raise ValueError(f"Invalid plural rule: {self.rule!r}")
        return condition

    def or_condition(self) -> Condition:
        conditions = [self.and_condition()]
        while self.peek() == "or":
            self.take()
            conditions.append(self.and_condition())
        return lambda ops: any(condition(ops) for condition in conditions)

    def and_condition(self) -> Condition:
        relations = [self.relation()]
        while self.peek() == "and":
            self.take()
            relations.append(self.relation())
        return lambda ops: all(relation(ops) for relation in relations)

    def number(self) -> int:
        token = self.take()
        if not token.isdigit():
            raise ValueError(f"Invalid plural rule: {self.rule!r}")
        return int(token)

    def relation(self) -> Condition:
        operand = self.take()
        if operand not in _OPERANDS:
            raise ValueError(f"Invalid plural rule: {self.rule!r}")
        modulus = None
        if self.peek() == "%":
            self.take()
            modulus = self.number()
        operator = self.take()
        if operator not in {"=", "!="}:
            raise ValueError(f"Invalid plural rule: {self.rule!r}")
        ranges = [self.range()]
        while self.peek() == ",":
            self.take()
            ranges.append(self.range())

        def relation(ops: Operands) -> bool:
            value = ops[operand]
            if modulus is not None:
                value %= modulus
            # Ranges only match integral values: 2.5 is not in 2..3.
            matches = value == value.to_integral_value() and any(
                low <= value <= high for low, high in ranges
            )
            return matches if operator == "=" else not matches

        return relation

    def range(self) -> tuple[int, int]:
        low = self.number()
        if self.peek() == "..":
            self.take()
            return low, self.number()
        return low, low


def compile_rule(rule: str) -> Condition:
    """
    Compile a CLDR plural rule (without samples) to a function.

    The function takes the operands returned by :func:`get_operands`.

    :raises ValueError: if the rule is invalid.
    """
    return _RuleParser(rule).parse()


@cache
def _compile(language: str) -> tuple[tuple[str, Condition], ...]:
    return tuple(
        (category, compile_rule(rule))
        for category, rule in plural_rules[language].items()
    )


def get_category(language: str, number: int | str | Decimal) -> str:
    """
    Return the CLDR plural category of *number* in *language*.

    :param language: A key of :data:`plural_rules`, see
        :func:`normalize_language`.
    :raises KeyError: if the language is unknown.
    """
    ops = get_operands(number)
    for category, condition in _compile(language):
        if condition(ops):
            return category
    return "other"
