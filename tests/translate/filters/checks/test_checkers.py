"""Tests for constructing and configuring the checkers themselves."""

from tests.translate.filters.checks.helpers import fails, fails_serious, passes, strprep
from translate.filters import checks
from translate.storage import base


def test_defaults() -> None:
    """Tests default setup and that checks aren't altered by other constructions."""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []
    mozillachecker = checks.MozillaChecker()
    assert len(mozillachecker.config.varmatches) == 9
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []


def test_construct() -> None:
    """Tests that the checkers can be constructed."""
    checks.StandardChecker()
    checks.MozillaChecker()
    checks.OpenOfficeChecker()
    checks.LibreOfficeChecker()
    checks.GnomeChecker()
    checks.KdeChecker()
    checks.IOSChecker()


def test_accelerator_markers() -> None:
    """Test that we have the correct accelerator marker for the various default configs."""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.accelmarkers == []
    mozillachecker = checks.MozillaChecker()
    assert mozillachecker.config.accelmarkers == ["&"]
    ooochecker = checks.OpenOfficeChecker()
    assert ooochecker.config.accelmarkers == ["~"]
    lochecker = checks.LibreOfficeChecker()
    assert lochecker.config.accelmarkers == ["~"]
    gnomechecker = checks.GnomeChecker()
    assert gnomechecker.config.accelmarkers == ["_"]
    kdechecker = checks.KdeChecker()
    assert kdechecker.config.accelmarkers == ["&"]


def test_messages() -> None:
    """Test that our helpers can check for messages and that these error messages can contain Unicode."""
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
    )
    assert fails(
        stdchecker.validchars,
        "Some unexpected characters",
        "©",
        "Invalid characters: '©' (\\u00a9)",
    )
    stdchecker = checks.StandardChecker()
    assert fails_serious(
        stdchecker.escapes,
        r"A tab",
        r"'n Ṱab\t",
        r"""Escapes in original () don't match escapes in translation ('Ṱab\t')""",
    )


def test_minimalchecker() -> None:
    """Tests the Minimal quality checker."""
    # The minimal checker only checks for untranslated, unchanged and blank strings.
    # All other quality checks should be ignored.
    minimalchecker = checks.MinimalChecker()
    assert fails(minimalchecker.untranslated, "I am untranslated", "")
    assert passes(minimalchecker.untranslated, "I am translated", "Ek is vertaal")
    assert fails(minimalchecker.unchanged, "Unchanged", "Unchanged")
    assert passes(minimalchecker.unchanged, "Unchanged", "Changed")
    assert fails(minimalchecker.blank, "Blank string", " ")

    # Doublewords check is disabled.
    src, tgt, __ = strprep("Save the rhino", "Save the the rhino")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "doublewords" not in minimalchecker.run_filters(unit)

    # Printf check is disabled.
    src, tgt, __ = strprep("Non-matching printf variables", "Ek is %s")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "printf" not in minimalchecker.run_filters(unit)


def test_reducedchecker() -> None:
    """Tests the Reduced quality checker."""
    # The reduced checker only runs the following tests:
    # untranslated, unchanged, blank, doublespacing, doublewords, spellcheck.
    # All other quality checks should be ignored.
    reducedchecker = checks.ReducedChecker()
    assert fails(reducedchecker.untranslated, "I am untranslated", "")
    assert passes(reducedchecker.untranslated, "I am translated", "Ek is vertaal")
    assert fails(reducedchecker.unchanged, "Unchanged", "Unchanged")
    assert passes(reducedchecker.unchanged, "Unchanged", "Changed")
    assert fails(reducedchecker.blank, "Blank string", " ")
    assert passes(
        reducedchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin. No double spacing.",
    )
    assert fails(
        reducedchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin.  Uneeded double space in translation.",
    )
    assert passes(reducedchecker.doublewords, "Save the rhino", "Save the rhino")
    assert fails(reducedchecker.doublewords, "Save the rhino", "Save the the rhino")

    # Printf check is disabled.
    src, tgt, __ = strprep("Non-matching printf variables", "Ek is %s")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "printf" not in reducedchecker.run_filters(unit)

    # Escapes check is disabled.
    src, tgt, __ = strprep("A file", "'n Leer\n")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "escapes" not in reducedchecker.run_filters(unit)


def test_skip_checks_per_language_in_some_checkers() -> None:
    """Test some checks are skipped for some languages in Mozilla checker."""
    # Hijack checker config language ignoretests to test check is skipped.
    checker_config = checks.CheckerConfig(targetlanguage="gl")
    previous_ignoretests = checker_config.lang.ignoretests
    checker_config.lang.ignoretests = {
        "mozilla": ["accelerators"],
    }

    # Prepare the checkers and the unit.
    mozillachecker = checks.MozillaChecker(checkerconfig=checker_config)
    stdchecker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(accelmarkers="&", targetlanguage="gl")
    )

    str1, str2, __ = strprep("&Check for updates", "আপডেইটসমূহৰ বাবে নিৰীক্ষণ কৰক")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    # Accelerators check is disabled for this language in MozillaChecker.
    assert "accelerators" not in mozillachecker.run_filters(unit)

    # But it is not in StandardChecker.
    assert "accelerators" in stdchecker.run_filters(unit)

    # Undo hijack.
    checker_config.lang.ignoretests = previous_ignoretests


def test_ensure_bengali_languages_script_is_correct() -> None:
    """Test script for Bengali languages is correctly set."""
    bn_BD_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_BD")
    )
    bn_IN_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_IN")
    )
    bn_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_IN")
    )
    assert bn_BD_mozilla_checker.config.language_script == "Beng"
    assert bn_IN_mozilla_checker.config.language_script == "Beng"
    assert bn_mozilla_checker.config.language_script == "Beng"


def test_category() -> None:
    """Tests checker categories aren't mixed up."""
    unit = base.TranslationUnit("foo")
    unit.target = "bar"

    standard_checker = checks.StandardChecker()
    assert standard_checker.categories == {}
    standard_checker.run_filters(unit)
    assert standard_checker.categories != {}
    assert "validxml" not in standard_checker.categories
    standard_categories_count = len(standard_checker.categories.values())

    libo_checker = checks.LibreOfficeChecker()
    assert libo_checker.categories == {}
    libo_checker.run_filters(unit)
    assert libo_checker.categories != {}
    assert "validxml" in libo_checker.categories

    standard_checker = checks.StandardChecker()
    assert standard_checker.categories == {}
    standard_checker.run_filters(unit)
    assert standard_checker.categories != {}
    assert len(standard_checker.categories.values()) == standard_categories_count
    assert "validxml" not in standard_checker.categories
