"""Tests for the whitespace checks."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_startwhitespace() -> None:
    """Tests startwhitespace."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startwhitespace, "A setence.", "I'm correct.")
    assert fails(stdchecker.startwhitespace, " A setence.", "I'm incorrect.")


def test_endwhitespace() -> None:
    """Tests endwhitespace."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.endwhitespace, "A setence.", "I'm correct.")
    assert passes(stdchecker.endwhitespace, "A setence. ", "I'm correct. ")
    assert fails(stdchecker.endwhitespace, "A setence. ", "'I'm incorrect.")
    assert passes(
        stdchecker.endwhitespace,
        "Problem with something: %s\n",
        "Probleem met iets: %s\n",
    )

    zh_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="zh"))
    # This should pass since the space is not needed in Chinese
    assert passes(zh_checker.endwhitespace, "Init. Limit: ", "起始时间限制：")


def test_doublespacing() -> None:
    """Tests double spacing."""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.doublespacing, "Sentence.  Another sentence.", "Sin.  'n Ander sin."
    )
    assert passes(
        stdchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin. No double spacing.",
    )
    assert fails(
        stdchecker.doublespacing,
        "Sentence.  Another sentence.",
        "Sin. Missing the double space.",
    )
    assert fails(
        stdchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin.  Uneeded double space in translation.",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah %PROGRAMNAME Calc"
    )
    assert passes(
        ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah % PROGRAMNAME Calc"
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah %PROGRAMNAME Calc"
    )
    assert passes(
        lochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah % PROGRAMNAME Calc"
    )
