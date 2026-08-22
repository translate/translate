"""
Runs the standard checks over a batch of string pairs.

This used to be the ``__main__`` block of ``translate.filters.checks``, which
only printed the failures it found; the failures are asserted here instead.
"""

from collections.abc import Mapping

from pytest import mark

from translate.filters import checks
from translate.filters.checks.checker import CheckFailureInfo
from translate.filters.decorators import Category
from translate.lang import data
from translate.storage import base

#: Pairs of (source, target) together with the checks they are expected to fail
TESTSET = [
    (r"simple", r"somple", []),
    (r"\this equals \that", r"does \this equal \that?", ["endpunc", "startpunc"]),
    (r"this \'equals\' that", r"this 'equals' that", ["escapes", "singlequoting"]),
    (
        r" start and end! they must match.",
        r"start and end! they must match.",
        ["startwhitespace", "unchanged"],
    ),
    (
        r"check for matching %variables marked like %this",
        r"%this %variable is marked",
        ["printf", "startpunc"],
    ),
    (
        r"check for mismatching %variables marked like %this",
        r"%that %variable is marked",
        ["printf", "startpunc"],
    ),
    (r"check for mismatching %variables% too", r"how many %variable% are marked", []),
    (r"%% %%", r"%%", ["purepunc", "startpunc"]),
    (r"Row: %1, Column: %2", r"Mothalo: %1, Kholomo: %2", []),
    (r"simple lowercase", r"it is all lowercase", []),
    (r"simple lowercase", r"It Is All Lowercase", ["simplecaps", "startcaps"]),
    (r"Simple First Letter Capitals", r"First Letters", []),
    (r"SIMPLE CAPITALS", r"First Letters", ["acronyms", "simplecaps"]),
    (r"SIMPLE CAPITALS", r"ALL CAPITALS", ["acronyms"]),
    (r"forgot to translate", r"  ", ["blank"]),
]


def run_filters(
    str1: str, str2: str, categorised: bool = False
) -> Mapping[str, str | CheckFailureInfo]:
    """Runs the standard checks over a pair of strings."""
    unit = base.TranslationUnit(data.normalize(str1))
    unit.target = data.normalize(str2)

    return checks.StandardChecker().run_filters(unit, categorised)


@mark.parametrize(("source", "target", "expected"), TESTSET)
def test_standard_batch_run(source: str, target: str, expected: list[str]) -> None:
    """Tests that the standard checks flag exactly the expected problems."""
    failures = run_filters(source, target)

    assert sorted(failures) == expected
    # Uncategorised results map the check name straight to its message
    assert all(isinstance(message, str) for message in failures.values())


def test_standard_batch_run_categorised() -> None:
    """Tests that categorised results carry the message and its category."""
    failures = run_filters("forgot to translate", "  ", categorised=True)

    assert failures == {
        "blank": {
            "message": "Translation is empty",
            "category": Category.FUNCTIONAL,
        }
    }
