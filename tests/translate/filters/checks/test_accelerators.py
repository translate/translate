"""Tests for the accelerator checks."""

from pytest import mark

from tests.translate.filters.checks.helpers import fails, fails_serious, passes, strprep
from translate.filters import checks
from translate.storage import base


def test_accelerators() -> None:
    """Tests accelerators."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert passes(stdchecker.accelerators, "&File", "&Fayile")
    assert fails(stdchecker.accelerators, "&File", "Fayile")
    assert fails(stdchecker.accelerators, "File", "&Fayile")
    assert passes(stdchecker.accelerators, "Mail && News", "Pos en Nuus")
    assert fails(stdchecker.accelerators, "Mail &amp; News", "Pos en Nuus")
    assert passes(stdchecker.accelerators, "&Allow", "&\ufeb2\ufee3\ufe8e\ufea3")
    assert fails(stdchecker.accelerators, "Open &File", "Vula& Ifayile")
    kdechecker = checks.KdeChecker()
    assert passes(kdechecker.accelerators, "&File", "&Fayile")
    assert fails(kdechecker.accelerators, "&File", "Fayile")
    assert fails(kdechecker.accelerators, "File", "&Fayile")
    gnomechecker = checks.GnomeChecker()
    assert passes(gnomechecker.accelerators, "_File", "_Fayile")
    assert fails(gnomechecker.accelerators, "_File", "Fayile")
    assert fails(gnomechecker.accelerators, "File", "_Fayile")
    assert fails(gnomechecker.accelerators, "_File", "_Fayil_e")
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.accelerators, "&File", "&Fayile")
    assert passes(
        mozillachecker.accelerators,
        "Warn me if this will disable any of my add&-ons",
        "&Waarsku my as dit enige van my byvoegings sal deaktiveer",
    )
    assert fails_serious(mozillachecker.accelerators, "&File", "Fayile")
    assert fails_serious(mozillachecker.accelerators, "File", "&Fayile")
    assert passes(mozillachecker.accelerators, "Mail &amp; News", "Pos en Nuus")
    assert fails_serious(mozillachecker.accelerators, "Mail &amp; News", "Pos en &Nuus")
    assert passes(mozillachecker.accelerators, "Mail & News", "Pos & Nuus")
    ooochecker = checks.OpenOfficeChecker()
    assert passes(ooochecker.accelerators, "~File", "~Fayile")
    assert fails(ooochecker.accelerators, "~File", "Fayile")
    assert fails(ooochecker.accelerators, "File", "~Fayile")

    # We don't want an accelerator for letters with a diacritic
    assert fails(ooochecker.accelerators, "F~ile", "L~êer")
    lochecker = checks.LibreOfficeChecker()
    assert passes(lochecker.accelerators, "~File", "~Fayile")
    assert fails(lochecker.accelerators, "~File", "Fayile")
    assert fails(lochecker.accelerators, "File", "~Fayile")

    # We don't want an accelerator for letters with a diacritic
    assert fails(lochecker.accelerators, "F~ile", "L~êer")

    # Bug 289: accept accented accelerator characters
    afchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers="&", targetlanguage="fi")
    )
    assert passes(afchecker.accelerators, "&Reload Frame", "P&äivitä kehys")

    trchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers="&", targetlanguage="tr")
    )
    assert passes(trchecker.accelerators, "&Download", "&İndir")
    assert passes(trchecker.accelerators, "&Business", "İ&ş")
    assert passes(trchecker.accelerators, "&Remove", "Kald&ır")
    assert passes(trchecker.accelerators, "&Three", "&Üç")
    assert passes(trchecker.accelerators, "&Three", "Ü&ç")
    assert passes(trchecker.accelerators, "&Before", "&Önce")
    assert passes(trchecker.accelerators, "Fo&ur", "D&ört")
    assert passes(trchecker.accelerators, "Mo&dern", "Ça&ğdaş")
    assert passes(trchecker.accelerators, "Mo&dern", "&Çağdaş")
    assert passes(trchecker.accelerators, "&February", "&Şubat")
    assert passes(trchecker.accelerators, "P&lain", "D&üz")
    assert passes(trchecker.accelerators, "GAR&DEN", "BA&Ğ")

    # Problems:
    # Accelerator before variable - see test_acceleratedvariables


@mark.xfail(reason="Accelerated variables needs a better implementation")
def test_acceleratedvariables() -> None:
    """Test for accelerated variables."""
    # FIXME: disabled since acceleratedvariables has been removed, but these checks are still needed
    mozillachecker = checks.MozillaChecker()
    assert fails(mozillachecker.acceleratedvariables, "%S &Options", "&%S Ikhetho")  # ty:ignore[unresolved-attribute]
    assert passes(mozillachecker.acceleratedvariables, "%S &Options", "%S &Ikhetho")  # ty:ignore[unresolved-attribute]
    ooochecker = checks.OpenOfficeChecker()
    assert fails(
        ooochecker.acceleratedvariables,  # ty:ignore[unresolved-attribute]
        "%PRODUCTNAME% ~Options",
        "~%PRODUCTNAME% Ikhetho",
    )
    assert passes(
        ooochecker.acceleratedvariables,  # ty:ignore[unresolved-attribute]
        "%PRODUCTNAME% ~Options",
        "%PRODUCTNAME% ~Ikhetho",
    )
    lochecker = checks.LibreOfficeChecker()
    assert fails(
        lochecker.acceleratedvariables,  # ty:ignore[unresolved-attribute]
        "%PRODUCTNAME% ~Options",
        "~%PRODUCTNAME% Ikhetho",
    )
    assert passes(
        lochecker.acceleratedvariables,  # ty:ignore[unresolved-attribute]
        "%PRODUCTNAME% ~Options",
        "%PRODUCTNAME% ~Ikhetho",
    )


def test_mozilla_no_accelerators_for_indic() -> None:
    """
    Test accelerators in MozillaChecker fails if accelerator in target.

    No-accelerators is a special behavior of accelerators check in some
    languages that is present in MozillaChecker.
    """
    mozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="as")
    )
    assert fails(mozillachecker.accelerators, "&File", "&Fayile")
    assert fails(mozillachecker.accelerators, "My add&-ons", "&Byvoengs mit")
    assert passes(mozillachecker.accelerators, "&File", "Fayile")
    assert fails(mozillachecker.accelerators, "File", "&Fayile")
    assert passes(mozillachecker.accelerators, "Mail &amp; News", "Po en Nuus")
    assert fails(mozillachecker.accelerators, "Mail &amp; News", "Po en &Nuus")
    assert passes(mozillachecker.accelerators, "Mail & News", "Pos & Nuus")


def test_noaccelerators_only_in_mozilla_checker() -> None:
    """
    Test no-accelerators check is only present in Mozilla checker.

    No-accelerators is a special behavior of accelerators check in some
    languages that is present in MozillaChecker.
    """
    asmozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="as")
    )
    glmozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="gl")
    )
    stdchecker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(accelmarkers="&", targetlanguage="as")
    )

    # Accelerators check passes for Assamesse in Mozilla checker. It fails for
    # Assamesse in Standard checker or for other languages in Mozilla Checker.
    str1, str2, __ = strprep("&Check for updates", "আপডেইটসমূহৰ বাবে নিৰীক্ষণ কৰক")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    gl_failures = glmozillachecker.run_filters(unit)
    std_failures = stdchecker.run_filters(unit)

    assert "accelerators" not in asmozillachecker.run_filters(unit)
    assert "accelerators" in gl_failures
    assert "should not appear" not in gl_failures["accelerators"]
    assert "accelerators" in std_failures
    assert "should not appear" not in std_failures["accelerators"]

    # Accelerators check passes. The ampersand should be detected as part of
    # a variable.
    str1, str2, __ = strprep("About &brandFullName;", "&brandFullName; ৰ বিষয়ে")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    assert "accelerators" not in asmozillachecker.run_filters(unit)
    assert "accelerators" not in glmozillachecker.run_filters(unit)
    assert "accelerators" not in stdchecker.run_filters(unit)

    # Accelerators check fails for Assamesse in Mozilla checker since the
    # accelerator is present in the target. It passes for other languages or
    # other checkers.
    str1, str2, __ = strprep("&Cancel", "বাতিল কৰক (&C)")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    as_failures = asmozillachecker.run_filters(unit)

    assert asmozillachecker.config.language_script == "assamese"
    assert "accelerators" in as_failures
    assert "should not appear" in as_failures["accelerators"]
    assert "accelerators" not in glmozillachecker.run_filters(unit)
    assert "accelerators" not in stdchecker.run_filters(unit)


def test_ensure_accelerators_not_in_target_if_not_in_source() -> None:
    """Test accelerators check works different for some languages in Mozilla."""
    af_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="af")
    )
    km_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="km")
    )

    # Afrikaans passes: Correct use of accesskeys.
    # Khmer fails: Translation shouldn't have an accesskey.
    src, tgt, __ = strprep("&One", "&Een")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    km_failures = km_mozilla_checker.run_filters(unit)

    assert "accelerators" not in af_mozilla_checker.run_filters(unit)
    assert "accelerators" in km_failures
    assert "should not appear" in km_failures["accelerators"]

    # Afrikaans fails: Translation is missing the accesskey.
    # Khmer passes: Translation doesn't need accesskey for this language.
    src, tgt, __ = strprep("&Two", "Twee")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    af_failures = af_mozilla_checker.run_filters(unit)

    assert "accelerators" in af_failures
    assert "Missing accelerator" in af_failures["accelerators"]
    assert "accelerators" not in km_mozilla_checker.run_filters(unit)

    # Afrikaans fails: No accesskey in the source, but yes on translation.
    # Khmer fails: Translation doesn't need accesskey, but it has accesskey.
    src, tgt, __ = strprep("Three", "&Drie")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    af_failures = af_mozilla_checker.run_filters(unit)
    km_failures = km_mozilla_checker.run_filters(unit)

    assert "accelerators" in af_failures
    assert "Added accelerator" in af_failures["accelerators"]
    assert "accelerators" in km_failures
    assert "should not appear" in km_failures["accelerators"]
