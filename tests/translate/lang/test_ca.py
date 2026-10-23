from __future__ import annotations

from typing import TYPE_CHECKING

from translate.filters import checks
from translate.lang import factory
from translate.storage import base

if TYPE_CHECKING:
    from translate.filters.checks.checker import CheckFailures


def test_no_inverted_opening_punctuation() -> None:
    """Catalan does not take the inverted opening marks that Spanish adds."""
    catalan = factory.getlanguage("ca")
    spanish = factory.getlanguage("es")
    # The same input, to make the difference the only variable.
    assert spanish.punctranslate("Abc efg?") == "\u00bfAbc efg?"
    assert catalan.punctranslate("Abc efg?") == "Abc efg?"
    assert spanish.punctranslate("Abc efg!") == "\u00a1Abc efg!"
    assert catalan.punctranslate("Abc efg!") == "Abc efg!"


def test_sentences() -> None:
    """Sentence segmentation needs no Catalan-specific rule."""
    language = factory.getlanguage("ca")
    assert language.sentences("") == []
    assert language.sentences("S'ha modificat el fitxer. Voleu desar-lo?") == [
        "S'ha modificat el fitxer.",
        "Voleu desar-lo?",
    ]


def _check(source: str, target: str, language: str) -> CheckFailures:
    checker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage=language)
    )
    unit = base.TranslationUnit(source)
    unit.target = target
    return checker.run_filters(unit)


def test_capitalisation_checks_are_skipped() -> None:
    """Catalan does not capitalise common nouns the way English does."""
    # "Domain" is a common noun and takes no capital in Catalan.
    assert "startcaps" not in _check("Domain", "domini", "ca")
    assert "simplecaps" not in _check(
        "Invalid Site Name", "nom del lloc no vàlid", "ca"
    )
    # The same strings still fail for a language without the exception.
    assert "startcaps" in _check("Domain", "domini", "af")


def test_acronyms_check_is_skipped() -> None:
    """Catalan style guides expand initialisms such as ID into words."""
    assert "acronyms" not in _check("Invalid site ID.", "Identificador no vàlid.", "ca")
    assert "acronyms" in _check("Invalid site ID.", "Identificador no vàlid.", "af")
